import unittest
from unittest.mock import Mock, patch

# Class chứa hàm cần test
from django.contrib.auth.views import LoginView


class TestGetSuccessURLAllowedHosts(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm:
        def get_success_url_allowed_hosts(self, request=None):
            if request is None:
                request = self.request
            return {request.get_host(), *self.success_url_allowed_hosts}
    """

    def setUp(self):
        self.view = LoginView()
        # Thiết lập sẵn allowed hosts mặc định
        self.view.success_url_allowed_hosts = {"example.com"}

    @patch("django.http.request.HttpRequest.get_host")
    def test_happy_path_with_request(self, mock_get_host):
        """
        Happy Path:
        - request được truyền vào
        - get_host() trả về host hợp lệ
        - kết quả là set chứa host + success_url_allowed_hosts
        """
        mock_get_host.return_value = "testserver"

        request = Mock()
        request.get_host = mock_get_host

        result = self.view.get_success_url_allowed_hosts(request)

        self.assertEqual(result, {"testserver", "example.com"})
        mock_get_host.assert_called_once()

    @patch("django.http.request.HttpRequest.get_host")
    def test_edge_case_request_none_use_self_request(self, mock_get_host):
        """
        Edge Case:
        - request=None
        - sử dụng self.request
        """
        mock_get_host.return_value = "selfhost"

        mock_request = Mock()
        mock_request.get_host = mock_get_host

        self.view.request = mock_request

        result = self.view.get_success_url_allowed_hosts()

        self.assertEqual(result, {"selfhost", "example.com"})
        mock_get_host.assert_called_once()

    @patch("django.http.request.HttpRequest.get_host")
    def test_edge_case_empty_allowed_hosts(self, mock_get_host):
        """
        Edge Case:
        - success_url_allowed_hosts rỗng
        - chỉ còn lại host từ request
        """
        mock_get_host.return_value = "onlyhost"

        request = Mock()
        request.get_host = mock_get_host

        self.view.success_url_allowed_hosts = set()

        result = self.view.get_success_url_allowed_hosts(request)

        self.assertEqual(result, {"onlyhost"})
        mock_get_host.assert_called_once()


if __name__ == "__main__":
    unittest.main()