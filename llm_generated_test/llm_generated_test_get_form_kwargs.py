import unittest
from unittest.mock import patch, Mock

# Class chứa hàm get_form_kwargs (trong Django auth views)
from django.contrib.auth.views import LoginView


class TestGetFormKwargs(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm:
        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs["request"] = self.request
            return kwargs
    """

    def setUp(self):
        self.view = LoginView()

    @patch("django.views.generic.edit.FormMixin.get_form_kwargs")
    def test_get_form_kwargs_happy_path(self, mock_super_kwargs):
        """
        Happy Path:
        - super().get_form_kwargs() trả về dict có sẵn dữ liệu
        - request được thêm vào kwargs
        """
        # Mock dữ liệu trả về từ super
        mock_super_kwargs.return_value = {"initial": "data"}

        # Mock request
        mock_request = Mock()
        self.view.request = mock_request

        result = self.view.get_form_kwargs()

        self.assertIn("request", result)
        self.assertEqual(result["request"], mock_request)
        self.assertEqual(result["initial"], "data")

    @patch("django.views.generic.edit.FormMixin.get_form_kwargs")
    def test_get_form_kwargs_empty_dict(self, mock_super_kwargs):
        """
        Edge Case:
        - super().get_form_kwargs() trả về dict rỗng
        - request vẫn phải được thêm vào
        """
        mock_super_kwargs.return_value = {}

        mock_request = Mock()
        self.view.request = mock_request

        result = self.view.get_form_kwargs()

        self.assertEqual(result, {"request": mock_request})

    @patch("django.views.generic.edit.FormMixin.get_form_kwargs")
    def test_get_form_kwargs_missing_keys(self, mock_super_kwargs):
        """
        Edge Case:
        - super().get_form_kwargs() trả về dict thiếu các key thông thường
        - Hàm vẫn hoạt động bình thường và thêm request
        """
        mock_super_kwargs.return_value = {"unexpected": 123}

        mock_request = Mock()
        self.view.request = mock_request

        result = self.view.get_form_kwargs()

        self.assertIn("request", result)
        self.assertEqual(result["request"], mock_request)
        self.assertEqual(result["unexpected"], 123)


if __name__ == "__main__":
    unittest.main()