import unittest
from unittest.mock import Mock, patch

# Class chứa hàm form_valid
from django.contrib.auth.views import LoginView


class TestFormValid(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm:
        def form_valid(self, form):
            auth_login(self.request, form.get_user())
            return HttpResponseRedirect(self.get_success_url())
    """

    def setUp(self):
        self.view = LoginView()
        self.view.request = Mock()

    @patch("django.contrib.auth.views.HttpResponseRedirect")
    @patch("django.contrib.auth.views.auth_login")
    def test_form_valid_happy_path(self, mock_auth_login, mock_redirect):
        """
        Happy Path:
        - form.get_user() trả về user hợp lệ
        - auth_login được gọi đúng
        - trả về HttpResponseRedirect với success_url
        """
        mock_user = Mock()

        form = Mock()
        form.get_user.return_value = mock_user

        self.view.get_success_url = Mock(return_value="/home/")

        response = self.view.form_valid(form)

        mock_auth_login.assert_called_once_with(self.view.request, mock_user)
        mock_redirect.assert_called_once_with("/home/")
        self.assertTrue(mock_redirect.called)

    @patch("django.contrib.auth.views.HttpResponseRedirect")
    @patch("django.contrib.auth.views.auth_login")
    def test_form_valid_user_none(self, mock_auth_login, mock_redirect):
        """
        Edge Case:
        - form.get_user() trả về None
        - auth_login vẫn được gọi với None
        """
        form = Mock()
        form.get_user.return_value = None

        self.view.get_success_url = Mock(return_value="/home/")

        response = self.view.form_valid(form)

        mock_auth_login.assert_called_once_with(self.view.request, None)
        mock_redirect.assert_called_once_with("/home/")

    @patch("django.contrib.auth.views.auth_login")
    def test_form_valid_get_user_raises_exception(self, mock_auth_login):
        """
        Edge Case:
        - form.get_user() raise Exception
        - Hàm không bắt exception => test phải assert raise
        """
        form = Mock()
        form.get_user.side_effect = Exception("Error getting user")

        self.view.get_success_url = Mock(return_value="/home/")

        with self.assertRaises(Exception):
            self.view.form_valid(form)

        mock_auth_login.assert_not_called()


if __name__ == "__main__":
    unittest.main()