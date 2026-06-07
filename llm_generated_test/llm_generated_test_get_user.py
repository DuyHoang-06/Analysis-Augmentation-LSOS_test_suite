import unittest
from unittest.mock import patch, Mock
from django.core.exceptions import ValidationError

# Import class chứa hàm get_user (thường là PasswordResetConfirmView)
from django.contrib.auth.views import PasswordResetConfirmView


class TestGetUser(unittest.TestCase):
    """
    Test suite để bao phủ 100% hàm get_user
    """

    def setUp(self):
        self.view = PasswordResetConfirmView()

    @patch("django.contrib.auth.views.UserModel")
    @patch("django.contrib.auth.views.urlsafe_base64_decode")
    def test_get_user_happy_path(self, mock_decode, mock_user_model):
        """
        Happy Path:
        - uidb64 hợp lệ
        - decode thành công
        - lấy được user từ DB
        """
        # Mock decode -> trả về bytes
        mock_decode.return_value = b"123"

        # Mock pk conversion
        mock_user_model._meta.pk.to_python.return_value = 123

        # Mock user object
        mock_user = Mock()
        mock_user_model._default_manager.get.return_value = mock_user

        result = self.view.get_user("valid_uid")

        self.assertEqual(result, mock_user)
        mock_decode.assert_called_once_with("valid_uid")
        mock_user_model._default_manager.get.assert_called_once_with(pk=123)

    @patch("django.contrib.auth.views.UserModel")
    @patch("django.contrib.auth.views.urlsafe_base64_decode")
    def test_get_user_invalid_uid_decode_error(self, mock_decode, mock_user_model):
        """
        Edge Case:
        - decode lỗi (TypeError / ValueError)
        - phải return None
        """
        mock_decode.side_effect = ValueError("Invalid base64")

        result = self.view.get_user("invalid_uid")

        self.assertIsNone(result)

    @patch("django.contrib.auth.views.UserModel")
    @patch("django.contrib.auth.views.urlsafe_base64_decode")
    def test_get_user_user_not_found(self, mock_decode, mock_user_model):
        """
        Edge Case:
        - decode OK nhưng không tìm thấy user
        - raise DoesNotExist
        """
        mock_decode.return_value = b"999"
        mock_user_model._meta.pk.to_python.return_value = 999

        # Giả lập exception DoesNotExist
        mock_user_model.DoesNotExist = Exception
        mock_user_model._default_manager.get.side_effect = mock_user_model.DoesNotExist()

        result = self.view.get_user("valid_but_not_exist")

        self.assertIsNone(result)

    @patch("django.contrib.auth.views.UserModel")
    @patch("django.contrib.auth.views.urlsafe_base64_decode")
    def test_get_user_validation_error(self, mock_decode, mock_user_model):
        """
        Edge Case:
        - pk conversion lỗi ValidationError
        """
        mock_decode.return_value = b"invalid_pk"
        mock_user_model._meta.pk.to_python.side_effect = ValidationError("Invalid PK")

        result = self.view.get_user("bad_pk")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()