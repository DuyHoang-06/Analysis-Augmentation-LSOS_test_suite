import unittest
from unittest.mock import Mock, patch

# Giả sử class chứa hàm get_redirect_url là một View
from django.contrib.auth.views import LoginView


class TestGetRedirectURL(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm get_redirect_url
    """

    def setUp(self):
        # Khởi tạo view và cấu hình cần thiết
        self.view = LoginView()
        self.view.redirect_field_name = "next"

        # Mock method get_success_url_allowed_hosts
        self.view.get_success_url_allowed_hosts = Mock(return_value={"testserver"})

    @patch("django.contrib.auth.views.url_has_allowed_host_and_scheme")
    def test_get_redirect_url_happy_path_valid_url(self, mock_url_check):
        """
        Happy Path:
        - Có redirect URL hợp lệ trong POST
        - url_has_allowed_host_and_scheme trả về True
        """
        mock_url_check.return_value = True

        request = Mock()
        request.POST.get.return_value = "/home/"
        request.GET.get.return_value = None
        request.is_secure.return_value = False

        result = self.view.get_redirect_url(request)

        self.assertEqual(result, "/home/")
        mock_url_check.assert_called_once()

    @patch("django.contrib.auth.views.url_has_allowed_host_and_scheme")
    def test_get_redirect_url_unsafe_url(self, mock_url_check):
        """
        Edge Case:
        - URL không an toàn (malicious)
        - Hàm check trả về False
        => phải return ""
        """
        mock_url_check.return_value = False

        request = Mock()
        request.POST.get.return_value = "http://evil.com"
        request.GET.get.return_value = None
        request.is_secure.return_value = False

        result = self.view.get_redirect_url(request)

        self.assertEqual(result, "")

    @patch("django.contrib.auth.views.url_has_allowed_host_and_scheme")
    def test_get_redirect_url_missing_param(self, mock_url_check):
        """
        Edge Case:
        - Không có redirect param trong cả POST và GET
        - redirect_to = None
        - Hàm check vẫn được gọi
        """
        mock_url_check.return_value = False  # None thường bị coi là unsafe

        request = Mock()
        request.POST.get.return_value = None
        request.GET.get.return_value = None
        request.is_secure.return_value = False

        result = self.view.get_redirect_url(request)

        self.assertEqual(result, "")
        mock_url_check.assert_called_once()


if __name__ == "__main__":
    unittest.main()