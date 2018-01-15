import mock
from handler import ping
from requests import HTTPError


class MockResponseSuccess():

    def raise_for_status(self):
        return


class MockBotoClient():
    def __init__(self):
        self.calls = []

    def put_metric_data(self, *args, **kwargs):
        self.calls.append(mock.call(*args, **kwargs))


@mock.patch('handler.requests.get', return_value=MockResponseSuccess())
@mock.patch('handler.boto3.client', return_value=MockBotoClient())
@mock.patch('handler.current_time_in_seconds', side_effect=[500, 1000])
@mock.patch('handler.os.environ.get', side_effect=['https://google.com', 'MyNamespace', 'google'])
@mock.patch('test_handler.MockBotoClient.put_metric_data')
def test_ping_successful(mock_put_metric, *_):
    result = ping({}, {})

    assert mock_put_metric.call_args_list == [mock.call(
        MetricData=[{
            'MetricName': 'google',
            'Dimensions': [
                {
                    'Name': 'Host',
                    'Value': 'https://google.com'
                }
            ],
            'Value': 500,
            'Unit': 'Seconds'
        }],
        Namespace='MyNamespace'
    )]

    assert result == {
        'body': '{"message": "Pinged: https://google.com Duration: 500"}',
        'statusCode': 200
    }


class MockResponseFailure():

    def raise_for_status(self):
        raise HTTPError('Server Error: 500 for url: https://google.com')


@mock.patch('handler.requests.get', return_value=MockResponseFailure())
@mock.patch('handler.boto3.client', return_value=MockBotoClient())
@mock.patch('handler.current_time_in_seconds', side_effect=[500, 1000])
@mock.patch('handler.os.environ.get', side_effect=['https://google.com', 'MyNamespace', 'google'])
@mock.patch('test_handler.MockBotoClient.put_metric_data')
def test_ping_failure(mock_put_metric, *_):
    result = ping({}, {})

    assert mock_put_metric.call_args_list == [mock.call(
        MetricData=[{
            'MetricName': 'google',
            'Dimensions': [
                {
                    'Name': 'Host',
                    'Value': 'https://google.com'
                }
            ],
            'Value': 0,  # Cloudwatch alerts on 0 or less
            'Unit': 'Seconds'
        }],
        Namespace='MyNamespace'
    )]

    assert result == {
        'body': '{"message": "Checked failed for https://google.com, Server Error: 500 for url: https://google.com"}',
        'statusCode': 200
    }
