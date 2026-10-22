import json
import os
import boto3
from datetime import datetime, timezone, timedelta

PROFILES_TABLE = os.environ["PROFILES_TABLE"]
LOGS_TABLE = os.environ["LOGS_TABLE"]
RECOMMENDATION_FUNCTION = os.environ["RECOMMENDATION_FUNCTION"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]
ALLOWED_ORIGIN = os.environ["ALLOWED_ORIGIN"]

dynamodb = boto3.resource("dynamodb")
sfn = boto3.client("stepfunctions")
user_table = dynamodb.Table(PROFILES_TABLE)




def respond(code, payload):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN
        },
        "body": json.dumps(payload, default=str)
    }


def lambda_handler(event, context):
    # Identity comes from the verified token, never from the request body
    claims = (event.get("requestContext", {})
                   .get("authorizer", {})
                   .get("claims", {}))
    user_id = claims.get("sub")

    if not user_id:
        return respond(401, {"error": "No verified identity on request"})

    body = event.get("body") or {}
    if isinstance(body, str):
        body = json.loads(body)

    service = body.get("service")
    action = body.get("action")

    if not service or not action:
        return respond(400, {"error": "service and action are required"})

    user_profile = user_table.get_item(Key={"user_id": user_id}).get("Item")

    # Build the context in the same format the risk engine expects
    ist_hour = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).hour
    user_context = {
        "user_role": (user_profile or {}).get("user_role", "citizen"),
        "is_off_hours": 1 if (ist_hour < 6 or ist_hour > 22) else 0,
        # Demo only: a real system would derive these from login history and IP geolocation
        "failed_attempts_24h": int(body.get("failed_attempts_24h", 0)),
        "location_distance_km": float(body.get("location_distance_km", 0)),
    }
    service_context = {
        "service_type": service.replace("-", "_"),
        "department": body.get("department", "general"),
    }

    workflow_input = {
        "user_id": user_id,
        "service": service,
        "action": action,
        "user_context": user_context,
        "service_context": service_context,
    }

    # Run the workflow synchronously; fail closed if it errors
    try:
        run = sfn.start_sync_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(workflow_input),
        )
        if run["status"] != "SUCCEEDED":
            raise RuntimeError(f"{run.get('error')}: {run.get('cause')}")
        result = json.loads(run["output"])
    except Exception as e:
        print("Workflow failed:", str(e))
        return respond(503, {
            "error": "Access decision unavailable",
            "decision": "DENY",
            "source": "fail_closed"
        })

    outcome = result.get("decision") or {}

    return respond(200, {
        "message": "Access request processed",
        "user_id": user_id,
        "service": service,
        "action": action,
        "decision": outcome.get("recommendation"),
        "reason": outcome.get("reason"),
        "source": outcome.get("source")
    })
