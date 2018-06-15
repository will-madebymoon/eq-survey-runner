from botocore.exceptions import ClientError
from structlog import get_logger

from app.globals import get_dynamodb

logger = get_logger()


def update_item(table, key, item, immutable_attributes=None, overwrite=True):

    if isinstance(table, str):
        table = get_table(table)

    immutable_attributes = immutable_attributes or {}

    attributes = {k: v for (k, v) in item.items() if k not in key.keys()}

    expression = ['{path} = :{path}'.format(path=k)
                  for k in attributes.keys() if k not in immutable_attributes]
    expression += ['{path} = if_not_exists({path}, :{path})'.format(path=k)
                   for k in immutable_attributes]
    expression_values = {':{}'.format(k): v for (k, v) in attributes.items()}

    update_kwargs = {
        'Key': key,
        'UpdateExpression': 'SET {}'.format(', '.join(expression)),
        'ExpressionAttributeValues': expression_values
    }

    if not overwrite:
        first_key = next(iter(key.keys()))
        update_kwargs['ConditionExpression'] = 'attribute_not_exists({first_key})'.format(
            first_key=first_key)

    response = table.update_item(**update_kwargs)['ResponseMetadata']['HTTPStatusCode']
    return response == 200


def get_item(table, key):
    """ Get an item given its key """
    if isinstance(table, str):
        table = get_table(table)

    response = table.get_item(Key=key)
    item = response.get('Item', None)

    return item


def delete_item(table, key):
    """Deletes an item by its key
    """
    if isinstance(table, str):
        table = get_table(table)

    response = table.delete_item(Key=key)
    item = response.get('Item', None)
    return item


def delete_all(table):
    """Deletes all items from a table
    """
    if isinstance(table, str):
        table = get_table(table)

    try:
        keys = [k['AttributeName'] for k in table.key_schema]
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return

    response = table.scan()

    with table.batch_writer() as batch:
        for item in response['Items']:
            key_dict = {k: item[k] for k in keys}
            batch.delete_item(Key=key_dict)


def get_table(table_name):
    dynamodb = get_dynamodb()
    if dynamodb and table_name:
        return dynamodb.Table(table_name)
