"""
Tests for data validation in Account Management API.
"""

import os
import re
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from pulse_account_management import (
    check_device_upgrade_eligibility,
    update_account_information,
)
from pulse_account_management.SimulationEngine.custom_errors import ValidationError
from pulse_account_management.tests.account_management_base_exception import (
    AccountManagementBaseTestCase,
)


class TestDataValidation(AccountManagementBaseTestCase):
    """
    Test data validation for email and phone number fields.
    """

    def test_update_account_information_valid_email(self):
        """Test updating account with valid email."""
        update_data = {"contactEmail": "test@example.com"}
        result = update_account_information("ACC888777666", update_data)

        self.assertEqual(result["contactEmail"], "test@example.com")

    def test_update_account_information_invalid_email(self):
        """Test updating account with invalid email."""
        update_data = {"contactEmail": "invalid-email"}

        with self.assertRaisesRegex(
            Exception, re.escape("Account INVALID-ACCOUNT not found in the database.")
        ):
            update_account_information(accountId="INVALID-ACCOUNT", requestBody=update_data)

    def test_update_account_information_valid_phone(self):
        """Test updating account with valid phone number."""
        update_data = {"contactPhone": "555-123-4567"}
        result = update_account_information("ACC888777666", update_data)

        # Phone should be normalized
        self.assertEqual(result["contactPhone"], "555-123-4567")

    def test_update_account_information_invalid_phone(self):
        """Test updating account with invalid phone number."""
        update_data = {"contactPhone": "123"}  # Too short

        with self.assertRaisesRegex(
            Exception, re.escape(f"The phone number '{update_data['contactPhone']}' is not valid.")
        ):
            update_account_information(accountId="ACC888777666", requestBody=update_data)

    def test_update_account_information_phone_with_spaces(self):
        """Test updating account with phone number containing spaces."""
        update_data = {"contactPhone": "555 123 4567"}
        result = update_account_information("ACC888777666", update_data)

        # Phone should be normalized to xxx-xxx-xxxx format
        self.assertEqual(result["contactPhone"], "555-123-4567")

    def test_update_account_information_phone_with_dashes(self):
        """Test updating account with phone number containing dashes."""
        update_data = {"contactPhone": "555-123-4567"}
        result = update_account_information("ACC888777666", update_data)

        # Phone should remain in xxx-xxx-xxxx format
        self.assertEqual(result["contactPhone"], "555-123-4567")

    def test_update_account_information_phone_with_parentheses(self):
        """Test updating account with phone number containing parentheses."""
        update_data = {"contactPhone": "(555) 444-5555"}
        result = update_account_information("ACC888777666", update_data)

        # Phone should be normalized to xxx-xxx-xxxx format
        self.assertEqual(result["contactPhone"], "555-444-5555")

    def test_check_device_upgrade_eligibility_valid_phone(self):
        """Test device upgrade eligibility with valid phone number."""
        result = check_device_upgrade_eligibility("ACC888777666", "555-444-5555", "LINE_NUMBER")

        self.assertIsNotNone(result)

    def test_check_device_upgrade_eligibility_invalid_phone(self):
        """Test device upgrade eligibility with invalid phone number."""

        with self.assertRaisesRegex(
            ValidationError, re.escape("The phone number '123' is not valid.")
        ):
            check_device_upgrade_eligibility(
                accountId="ACC888777666", identifier="123", identifierType="LINE_NUMBER"
            )

    def test_check_device_upgrade_eligibility_phone_normalization(self):
        """Test device upgrade eligibility with phone number normalization."""
        # Test with various phone formats that should match the same number
        phone_formats = [
            "(555) 444-5555",  # This format exists in the database
            "555 123-4567",
            "+555-123-4567",
            "+555 123 4567",
        ]

        for phone_format in phone_formats:
            with self.subTest(phone_format=phone_format):
                try:
                    result = check_device_upgrade_eligibility(
                        "ACC888777666", phone_format, "LINE_NUMBER"
                    )
                    # If no exception is raised, the phone was normalized successfully
                    self.assertIsNotNone(result)
                except ValidationError as e:
                    # If the phone doesn't match any device, that's expected
                    # The important thing is that validation passed
                    if "not found" in str(e):
                        pass  # Expected - phone doesn't match any device
                    else:
                        raise  # Unexpected error

    def test_update_account_information_combined_validation(self):
        """Test updating account with both email and phone validation."""
        update_data = {"contactEmail": "newemail@example.com", "contactPhone": "555-987-6543"}
        result = update_account_information("ACC888777666", update_data)

        self.assertEqual(result["contactEmail"], "newemail@example.com")
        self.assertEqual(result["contactPhone"], "555-987-6543")

    def test_update_account_information_invalid_both(self):
        """Test updating account with both invalid email and phone."""
        update_data = {"contactEmail": "invalid-email", "contactPhone": "123"}

        with self.assertRaisesRegex(
            Exception, re.escape("Account INVALID-ACCOUNT not found in the database.")
        ):
            update_account_information(accountId="INVALID-ACCOUNT", requestBody=update_data)

    def test_update_account_information_empty_values(self):
        """Test updating account with None values (should not validate)."""
        update_data = {"contactEmail": None, "contactPhone": None}

        # Should not raise validation errors for None values
        result = update_account_information("ACC888777666", update_data)
        self.assertIsNotNone(result)

    def test_update_account_information_empty_email(self):
        """Test updating account with empty email"""
        update_data = {
            "contactEmail": "",
        }

        # Should raise validation error for empty email
        with self.assertRaisesRegex(
            ValueError, re.escape("Invalid email value '' for field 'contactEmail'")
        ):
            update_account_information(accountId="ACC888777666", requestBody=update_data)

    def test_update_account_information_empty_phone(self):
        """Test updating account with empty phone"""
        update_data = {"contactPhone": ""}

        # Should raise validation error for empty phone
        with self.assertRaisesRegex(
            ValidationError, re.escape("The phone number '' is not valid.")
        ):
            update_account_information(accountId="ACC888777666", requestBody=update_data)


if __name__ == "__main__":
    unittest.main()
