import unittest
from unittest.mock import patch, Mock

# Class chứa hàm get_success_url (trong Django auth views)
from django.contrib.auth.views import LoginView


class TestGetSuccessURL(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm:
        def get_success_url(self):
            return self.get_redirect_url() or self.get_default_redirect_url()
    """

    def setUp(self):
        self.view = LoginView()

    def test_get_success_url_happy_path(self):
        """
        Happy Path:
        - get_redirect_url trả về URL hợp lệ (truthy)
        - Không gọi get_default_redirect_url
        """
        with patch.object(self.view, "get_redirect_url", return_value="/home/") as mock_redirect, \
             patch.object(self.view, "get_default_redirect_url", return_value="/default/") as mock_default:

            result = self.view.get_success_url()

            self.assertEqual(result, "/home/")
            mock_redirect.assert_called_once()
            mock_default.assert_not_called()  # vì không cần fallback

    def test_get_success_url_fallback_when_empty_string(self):
        """
        Edge Case:
        - get_redirect_url trả về "" (falsy)
        - Phải fallback sang get_default_redirect_url
        """
        with patch.object(self.view, "get_redirect_url", return_value="") as mock_redirect, \
             patch.object(self.view, "get_default_redirect_url", return_value="/default/") as mock_default:

            result = self.view.get_success_url()

            self.assertEqual(result, "/default/")
            mock_redirect.assert_called_once()
            mock_default.assert_called_once()

    def test_get_success_url_fallback_when_none(self):
        """
        Edge Case:
        - get_redirect_url trả về None
        - Phải fallback sang get_default_redirect_url
        """
        with patch.object(self.view, "get_redirect_url", return_value=None) as mock_redirect, \
             patch.object(self.view, "get_default_redirect_url", return_value="/default/") as mock_default:

            result = self.view.get_success_url()

            self.assertEqual(result, "/default/")
            mock_redirect.assert_called_once()
            mock_default.assert_called_once()


if __name__ == "__main__":
    unittest.main()