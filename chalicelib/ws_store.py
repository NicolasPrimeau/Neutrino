from typing import Set

import boto3
import botocore
import botocore.exceptions


def insert_new_connection(session_id: str, connection_id: str):
    try:
        _table().put_item(
            Item={"sessionId": session_id, "connectionIds": {connection_id}},
            ConditionExpression="attribute_not_exists(connectionIds)"
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            _table().update_item(
                Key={
                    'sessionId': session_id,
                },
                UpdateExpression="ADD connectionIds :items",
                ExpressionAttributeValues={
                    ':items': {connection_id}
                },
            )
        else:
            raise e


def get_connection_ids_for_session(session_id: str) -> Set[str]:
    result = _table().get_item(Key={'sessionId': session_id})
    return set(result.get("Item", {}).get("connectionIds", []) if result else set())


def remove_connection(session_id: str, connection_id: str):
    _table().update_item(
        Key={
            'sessionId': session_id,
        },
        UpdateExpression="DELETE connectionIds :items",
        ExpressionAttributeValues={
            ':items': {connection_id},
        },
    )


def delete_item(session_id: str):
    _table().delete_item(Key={
        "sessionId": session_id
    })


def _table():
    return boto3.resource('dynamodb').Table("neutrino-prod")
