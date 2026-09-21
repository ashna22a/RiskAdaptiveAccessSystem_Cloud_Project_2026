import json


def lambda_handler(event, context):
    body = event.get("body", event)

    if isinstance(body, str):
        body = json.loads(body)

    user_id = body.get("user_id")
    service = body.get("service")
    action = body.get("action")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Access request received",
            "user_id": user_id,
            "service": service,
            "action": action
        })
    }
