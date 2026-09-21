import json


def lambda_handler(event, context):
    body = event.get("body", event)

    if isinstance(body, str):
        body = json.loads(body)

    user_id = body.get("user_id")
    service = body.get("service")
    action = body.get("action")

    if not user_id or not service or not action:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "user_id, service, and action are required"
            })
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Access request received",
            "user_id": user_id,
            "service": service,
            "action": action,
            "status": "PENDING_RISK_ASSESSMENT"
        })
    }
