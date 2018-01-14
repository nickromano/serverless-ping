import mock
from handler import ping
from requests import HTTPError


class MockResponseSuccess():

    def raise_for_status(self):
        return


@mock.patch('handler.requests.get')
@mock.patch('handler.boto_client.put_metric_data')
@mock.patch('handler.current_time_in_seconds')
@mock.patch('handler.os.environ.get')
def test_ping_successful(mock_environ_get, mock_current_time_in_seconds, mock_boto_put_metric, mock_requests_get):
    mock_requests_get.return_value = MockResponseSuccess()
    mock_current_time_in_seconds.side_effect = [500, 1000]
    mock_environ_get.side_effect = ['https://google.com', 'MyNamespace', 'google']

    result = ping({}, {})

    assert mock_boto_put_metric.call_args_list == [mock.call(
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


@mock.patch('handler.requests.get')
@mock.patch('handler.boto_client.put_metric_data')
@mock.patch('handler.current_time_in_seconds')
@mock.patch('handler.os.environ.get')
def test_ping_failure(mock_environ_get, mock_current_time_in_seconds, mock_boto_put_metric, mock_requests_get):
    mock_requests_get.return_value = MockResponseFailure()
    mock_current_time_in_seconds.side_effect = [500, 1000]
    mock_environ_get.side_effect = ['https://google.com', 'MyNamespace', 'google']

    result = ping({}, {})

    assert mock_boto_put_metric.call_args_list == [mock.call(
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
