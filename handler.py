import json
import os
import time
import boto3
import logging

import sys, os  # noqa
# get this file's directory independent of where it's run from
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "vendored"))

import requests  # noqa
from raven.contrib.awslambda import LambdaClient  # noqa

boto_client = boto3.client('cloudwatch')
raven_client = LambdaClient()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def response_with_message(message):
    logger.info(message)
    return {"statusCode": 200, "body": json.dumps({"message": message})}


def publish_elapsed_time_for_host(elapsed_time, host):
    boto_client.put_metric_data(
        Namespace=os.environ.get('PING_ALARM_NAMESPACE'),
        MetricData=[
            {
                'MetricName': os.environ.get('PING_METRIC_NAME'),
                'Dimensions': [
                    {
                        'Name': 'Host',
                        'Value': host
                    },
                ],
                'Value': elapsed_time,
                'Unit': 'Seconds'
            },
        ]
    )


@raven_client.capture_exceptions
def ping(event, context):
    ping_host = os.environ.get('PING_HOST')

    start = time.time()
    try:
        response = requests.get(ping_host)
        response.raise_for_status()
    except requests.RequestException as e:
        publish_elapsed_time_for_host(0, ping_host)
        return response_with_message("Checked failed for {}, {}".format(ping_host, str(e)))

    elapsed_time = time.time() - start
    publish_elapsed_time_for_host(elapsed_time, ping_host)

    return response_with_message("Pinged: {} Duration: {}".format(ping_host, elapsed_time))


if __name__ == '__main__':
    ping({}, {})
