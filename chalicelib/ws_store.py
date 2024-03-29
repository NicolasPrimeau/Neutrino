import datetime
import time
from typing import Set, Optional, Tuple

import boto3
import botocore
import botocore.exceptions


def insert_new_connection(session_id: str, connection_id: str) -> Set[str]:
    try:
        week = datetime.datetime.today() + datetime.timedelta(days=1)
        expiration_date = int(time.mktime(week.timetuple()))

        _table().put_item(
            Item={
                "sessionId": session_id,
                "connectionIds": {connection_id},
                "expirationDate": expiration_date,
                "sourceCode": "",
                "languageId": "",
            },
            ConditionExpression="attribute_not_exists(connectionIds)",
        )
        return {connection_id}
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return _extract_connections(_table().update_item(
                Key={
                    'sessionId': session_id,
                },
                UpdateExpression="ADD connectionIds :items",
                ExpressionAttributeValues={
                    ':items': {connection_id}
                },
                ReturnValues="ALL_NEW",
            ))
        else:
            raise e


def save_source_code(session_id: str, source_code: str, language_id: int):
    _table().update_item(
        Key={
            'sessionId': session_id,
        },
        UpdateExpression="SET sourceCode = :source_code, languageId = :language_id",
        ExpressionAttributeValues={
            ":source_code": source_code,
            ":language_id": language_id
        }
    )


def get_source_code(session_id: str) -> Tuple[Optional[str], Optional[int]]:
    result = _table().get_item(Key={'sessionId': session_id})
    attributes = result.get("Item", result.get("Attributes", {}))
    source_code = attributes.get("sourceCode")
    language_id = attributes.get("languageId")
    return source_code, int(language_id) if language_id else None


def get_connection_ids_for_session(session_id: str) -> Set[str]:
    return _extract_connections(_table().get_item(Key={'sessionId': session_id}))


def remove_connection(session_id: str, connection_id: str) -> Set[str]:
    return _extract_connections(_table().update_item(
        Key={
            'sessionId': session_id,
        },
        UpdateExpression="DELETE connectionIds :items",
        ExpressionAttributeValues={
            ':items': {connection_id},
        },
        ReturnValues="ALL_NEW",
    ))


def delete_item(session_id: str):
    _table().delete_item(Key={
        "sessionId": session_id
    })


def _extract_connections(result) -> Set[str]:
    return set(result.get("Item", result.get("Attributes", {})).get("connectionIds", []) if result else set())


def _table():
    return boto3.resource('dynamodb').Table("neutrino-prod")
