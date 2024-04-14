import pytest
import requests
from unittest.mock import Mock, patch


@pytest.fixture
def some_data():
    return {"a": 1, "b": 2, "c": 3}

def test_addition(some_data):
    assert some_data["a"] + some_data["b"] == 3

def test_subtraction(some_data):
    assert some_data["c"] - some_data["b"] == 1






def send_request(url):
    response = requests.get(url)
    return response.status_code


def test_send_request():
    mock_get = Mock(return_value=Mock(status_code=200))
    with patch('requests.get', mock_get):
        status_code = send_request('http://example.com')
        assert status_code == 200
        mock_get.assert_called_once_with('http://example.com')




def test_send_request_pytest_mock(mocker):
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.status_code = 200
    status_code = send_request('http://example.com')
    assert status_code == 200
    mock_get.assert_called_once_with('http://example.com')