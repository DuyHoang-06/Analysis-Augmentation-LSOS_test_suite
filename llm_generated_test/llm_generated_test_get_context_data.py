import unittest
from unittest.mock import patch, Mock

# Class chứa hàm get_context_data (trong Django auth views)
from django.contrib.auth.views import LoginView


class TestGetContextData(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm:
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            current_site = get_current_site(self.request)
            context.update(
                {
                    self.redirect_field_name: self.get_redirect_url(),
                    "site": current_site,
                    "site_name": current_site.name,
                    **(self.extra_context or {}),
                }
            )
            return context
    """

    def setUp(self):
        self.view = LoginView()
        self.view.redirect_field_name = "next"

    @patch("django.contrib.auth.views.get_current_site")
    @patch("django.views.generic.base.ContextMixin.get_context_data")
    def test_get_context_data_happy_path(self, mock_super_context, mock_get_site):
        """
        Happy Path:
        - context ban đầu từ super
        - có request hợp lệ
        - có extra_context
        - trả về đầy đủ site, site_name, redirect URL
        """
        # Mock context từ super
        mock_super_context.return_value = {"base": "value"}

        # Mock request
        mock_request = Mock()
        self.view.request = mock_request

        # Mock site object
        mock_site = Mock()
        mock_site.name = "TestSite"
        mock_get_site.return_value = mock_site

        # Mock redirect URL
        self.view.get_redirect_url = Mock(return_value="/home/")

        # Extra context
        self.view.extra_context = {"extra_key": "extra_value"}

        result = self.view.get_context_data()

        self.assertEqual(result["base"], "value")
        self.assertEqual(result["next"], "/home/")
        self.assertEqual(result["site"], mock_site)
        self.assertEqual(result["site_name"], "TestSite")
        self.assertEqual(result["extra_key"], "extra_value")

    @patch("django.contrib.auth.views.get_current_site")
    @patch("django.views.generic.base.ContextMixin.get_context_data")
    def test_get_context_data_extra_context_none(self, mock_super_context, mock_get_site):
        """
        Edge Case:
        - extra_context = None
        - Không bị lỗi khi unpack
        """
        mock_super_context.return_value = {}

        mock_request = Mock()
        self.view.request = mock_request

        mock_site = Mock()
        mock_site.name = "TestSite"
        mock_get_site.return_value = mock_site

        self.view.get_redirect_url = Mock(return_value="/home/")
        self.view.extra_context = None

        result = self.view.get_context_data()

        self.assertEqual(result["next"], "/home/")
        self.assertEqual(result["site_name"], "TestSite")

    @patch("django.contrib.auth.views.get_current_site")
    @patch("django.views.generic.base.ContextMixin.get_context_data")
    def test_get_context_data_missing_request(self, mock_super_context, mock_get_site):
        """
        Edge Case:
        - request không tồn tại (None)
        - get_current_site vẫn được gọi với None
        """
        mock_super_context.return_value = {}

        self.view.request = None

        mock_site = Mock()
        mock_site.name = "NoRequestSite"
        mock_get_site.return_value = mock_site

        self.view.get_redirect_url = Mock(return_value="")

        result = self.view.get_context_data()

        self.assertEqual(result["site_name"], "NoRequestSite")
        self.assertEqual(result["next"], "")