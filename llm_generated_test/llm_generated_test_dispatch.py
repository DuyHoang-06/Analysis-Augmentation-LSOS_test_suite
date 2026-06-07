import unittest
from unittest.mock import Mock, patch

# Class chứa hàm dispatch
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect


class TestDispatch(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm:
        def dispatch(self, request, *args, **kwargs):
            if self.redirect_authenticated_user and self.request.user.is_authenticated:
                redirect_to = self.get_success_url()
                if redirect_to == self.request.path:
                    raise ValueError(...)
                return HttpResponseRedirect(redirect_to)
            return super().dispatch(request, *args, **kwargs)
    """

    def setUp(self):
        self.view = LoginView()
        self.view.redirect_authenticated_user = True

    def _build_request(self, is_authenticated=True, path="/login/"):
        """
        Helper tạo mock request + user
        """
        request = Mock()
        user = Mock()
        user.is_authenticated = is_authenticated

        request.user = user
        request.path = path
        return request

    @patch("django.contrib.auth.views.HttpResponseRedirect")
    def test_dispatch_happy_path_redirect_authenticated_user(self, mock_redirect):
        """
        Happy Path:
        - User đã đăng nhập
        - redirect_authenticated_user = True
        - get_success_url trả về URL khác path
        => Trả về HttpResponseRedirect
        """
        request = self._build_request(is_authenticated=True, path="/login/")
        self.view.request = request

        # Mock success URL
        self.view.get_success_url = Mock(return_value="/home/")

        response = self.view.dispatch(request)

        self.assertTrue(mock_redirect.called)
        mock_redirect.assert_called_once_with("/home/")

    def test_dispatch_redirect_loop_raises_error(self):
        """
        Edge Case:
        - redirect_to == request.path
        => raise ValueError (loop redirect)
        """
        request = self._build_request(is_authenticated=True, path="/login/")
        self.view.request = request

        # Gây loop
        self.view.get_success_url = Mock(return_value="/login/")

        with self.assertRaises(ValueError):
            self.view.dispatch(request)

    @patch("django.views.generic.base.View.dispatch")
    def test_dispatch_user_not_authenticated_calls_super(self, mock_super_dispatch):
        """
        Edge Case:
        - User chưa đăng nhập
        => gọi super().dispatch
        """
        request = self._build_request(is_authenticated=False)
        self.view.request = request

        mock_super_dispatch.return_value = "super_response"

        response = self.view.dispatch(request)

        self.assertEqual(response, "super_response")
        mock_super_dispatch.assert_called_once_with(request)

    @patch("django.views.generic.base.View.dispatch")
    def test_dispatch_redirect_flag_disabled_calls_super(self, mock_super_dispatch):
        """
        Edge Case:
        - redirect_authenticated_user = False
        => luôn đi vào super().dispatch
        """
        self.view.redirect_authenticated_user = False

        request = self._build_request(is_authenticated=True)
        self.view.request = request

        mock_super_dispatch.return_value = "super_response"

        response = self.view.dispatch(request)

        self.assertEqual(response, "super_response")
        mock_super_dispatch.assert_called_once_with(request)


if __name__ == "__main__":
    unittest.main()