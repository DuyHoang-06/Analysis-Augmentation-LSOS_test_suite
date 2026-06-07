import unittest
from unittest.mock import patch, Mock

# Class chứa hàm get_form_class (trong Django auth views)
from django.contrib.auth.views import LoginView


class TestGetFormClass(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm get_form_class:
        def get_form_class(self):
            return self.authentication_form or self.form_class
    """

    def setUp(self):
        self.view = LoginView()

    def test_get_form_class_happy_path_with_authentication_form(self):
        """
        Happy Path:
        - authentication_form tồn tại (khác None)
        - Phải trả về authentication_form
        """
        mock_auth_form = Mock(name="AuthForm")
        mock_default_form = Mock(name="DefaultForm")

        self.view.authentication_form = mock_auth_form
        self.view.form_class = mock_default_form

        result = self.view.get_form_class()

        self.assertEqual(result, mock_auth_form)

    def test_get_form_class_fallback_to_form_class_when_auth_form_none(self):
        """
        Edge Case:
        - authentication_form = None
        - Phải fallback sang form_class
        """
        mock_default_form = Mock(name="DefaultForm")

        self.view.authentication_form = None
        self.view.form_class = mock_default_form

        result = self.view.get_form_class()

        self.assertEqual(result, mock_default_form)

    def test_get_form_class_both_none(self):
        """
        Edge Case:
        - Cả authentication_form và form_class đều None
        - Kết quả phải là None
        """
        self.view.authentication_form = None
        self.view.form_class = None

        result = self.view.get_form_class()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()