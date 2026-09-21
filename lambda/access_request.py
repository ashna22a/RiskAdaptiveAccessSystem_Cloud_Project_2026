def lambda_handler(event, context):
    user_id = event.get("user_id")
    service = event.get("service")
    action = event.get("action")

    return {
        "statusCode": 200,
        "body": {
            "message": "Access request received",
            "user_id": user_id,
            "service": service,
            "action": action
        }
    }
