import os
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
user_table = dynamodb.Table(os.environ["PROFILES_TABLE"])

def lambda_handler(event, context):
    attrs = event["request"]["userAttributes"]

    try:
        user_table.put_item(
            Item={
                "user_id": attrs["sub"],
                "email": attrs.get("email", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "failed_attempts": 0,
                "user_role": "citizen"
            },
            ConditionExpression="attribute_not_exists(user_id)"
        )
    except Exception as e:
        # Never block a sign-up because the profile write failed
        print("Profile write failed:", str(e))

    # Cognito triggers must return the event unchanged
    return event
