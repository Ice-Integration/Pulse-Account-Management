"""
Test cases for custom_errors module
"""

import re
import unittest

from pulse_account_management.SimulationEngine.custom_errors import (
    AccountNotFoundError,
    DeviceNotFoundError,
    DuplicateAccountError,
    InsufficientFundsError,
    InsufficientPermissionsError,
    InvalidRequestError,
    InvalidUpgradeEligibilityError,
    PaymentMethodNotFoundError,
    ResourceNotFoundError,
    ServiceModificationError,
    ServicePlanNotFoundError,
    ValidationError,
)


class TestCustomErrors(unittest.TestCase):
    """
    Test suite for custom error classes.
    Tests exception instantiation, inheritance, and message handling.
    """

    def raise_error(self, message, exception_class):
        """Helper method to raise an error with the given message and exception class."""
        raise exception_class(message)

    def test_invalid_request_error_basic(self):
        """Test basic InvalidRequestError instantiation."""
        error = InvalidRequestError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, InvalidRequestError)

    def test_invalid_request_error_with_message(self):
        """Test InvalidRequestError with custom message."""
        message = "Invalid request parameters provided"
        error = InvalidRequestError(message)
        self.assertEqual(str(error), message)

    def test_invalid_request_error_raise_and_catch(self):
        """Test raising and catching InvalidRequestError."""
        message = "Test invalid request"

        with self.assertRaisesRegex(InvalidRequestError, re.escape(message)):
            self.raise_error(message, InvalidRequestError)

    def test_resource_not_found_error_basic(self):
        """Test basic ResourceNotFoundError instantiation."""
        error = ResourceNotFoundError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, ResourceNotFoundError)

    def test_resource_not_found_error_with_message(self):
        """Test ResourceNotFoundError with custom message."""
        message = "Resource not found in database"
        error = ResourceNotFoundError(message)
        self.assertEqual(str(error), message)

    def test_resource_not_found_error_raise_and_catch(self):
        """Test raising and catching ResourceNotFoundError."""
        message = "Test resource not found"

        with self.assertRaisesRegex(ResourceNotFoundError, re.escape(message)):
            self.raise_error(message, ResourceNotFoundError)

    def test_validation_error_basic(self):
        """Test basic ValidationError instantiation."""
        error = ValidationError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, ValidationError)

    def test_validation_error_with_message(self):
        """Test ValidationError with custom message."""
        message = "Input validation failed for field 'email'"
        error = ValidationError(message)
        self.assertEqual(str(error), message)

    def test_validation_error_raise_and_catch(self):
        """Test raising and catching ValidationError."""
        message = "Invalid email format"

        with self.assertRaisesRegex(ValidationError, re.escape(message)):
            self.raise_error(message, ValidationError)

    def test_account_not_found_error_basic(self):
        """Test basic AccountNotFoundError instantiation."""
        error = AccountNotFoundError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, AccountNotFoundError)

    def test_account_not_found_error_with_message(self):
        """Test AccountNotFoundError with custom message."""
        message = "Account with ID 'ACCT-12345' not found"
        error = AccountNotFoundError(message)
        self.assertEqual(str(error), message)

    def test_account_not_found_error_raise_and_catch(self):
        """Test raising and catching AccountNotFoundError."""
        account_id = "ACCT-NONEXISTENT"
        message = f"Account {account_id} not found in database"

        with self.assertRaisesRegex(AccountNotFoundError, re.escape(message)):
            self.raise_error(message, AccountNotFoundError)

    def test_device_not_found_error_basic(self):
        """Test basic DeviceNotFoundError instantiation."""
        error = DeviceNotFoundError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, DeviceNotFoundError)

    def test_device_not_found_error_with_message(self):
        """Test DeviceNotFoundError with custom message."""
        message = "Device with ID 'DEV-67890' not found"
        error = DeviceNotFoundError(message)
        self.assertEqual(str(error), message)

    def test_device_not_found_error_raise_and_catch(self):
        """Test raising and catching DeviceNotFoundError."""
        device_id = "DEV-MISSING"
        message = f"Device {device_id} not found in account"

        with self.assertRaisesRegex(DeviceNotFoundError, re.escape(message)):
            self.raise_error(message, DeviceNotFoundError)

    def test_service_plan_not_found_error_basic(self):
        """Test basic ServicePlanNotFoundError instantiation."""
        error = ServicePlanNotFoundError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, ServicePlanNotFoundError)

    def test_service_plan_not_found_error_with_message(self):
        """Test ServicePlanNotFoundError with custom message."""
        message = "Service plan with ID 'PLAN-001' not found"
        error = ServicePlanNotFoundError(message)
        self.assertEqual(str(error), message)

    def test_service_plan_not_found_error_raise_and_catch(self):
        """Test raising and catching ServicePlanNotFoundError."""
        plan_id = "PLAN-INVALID"
        message = f"Service plan {plan_id} is not available"

        with self.assertRaisesRegex(ServicePlanNotFoundError, re.escape(message)):
            self.raise_error(message, ServicePlanNotFoundError)

    def test_insufficient_permissions_error_basic(self):
        """Test basic InsufficientPermissionsError instantiation."""
        error = InsufficientPermissionsError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, InsufficientPermissionsError)

    def test_insufficient_permissions_error_with_message(self):
        """Test InsufficientPermissionsError with custom message."""
        message = "User lacks admin privileges for this operation"
        error = InsufficientPermissionsError(message)
        self.assertEqual(str(error), message)

    def test_insufficient_permissions_error_raise_and_catch(self):
        """Test raising and catching InsufficientPermissionsError."""
        operation = "delete_account"
        message = f"Insufficient permissions to perform {operation}"

        with self.assertRaisesRegex(InsufficientPermissionsError, re.escape(message)):
            self.raise_error(message, InsufficientPermissionsError)

    def test_duplicate_account_error_basic(self):
        """Test basic DuplicateAccountError instantiation."""
        error = DuplicateAccountError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, DuplicateAccountError)

    def test_duplicate_account_error_with_message(self):
        """Test DuplicateAccountError with custom message."""
        message = "Account with email 'user@example.com' already exists"
        error = DuplicateAccountError(message)
        self.assertEqual(str(error), message)

    def test_duplicate_account_error_raise_and_catch(self):
        """Test raising and catching DuplicateAccountError."""
        account_id = "ACCT-DUPLICATE"
        message = f"Account {account_id} already exists in the system"

        with self.assertRaisesRegex(DuplicateAccountError, re.escape(message)):
            self.raise_error(message, DuplicateAccountError)

    def test_invalid_upgrade_eligibility_error_basic(self):
        """Test basic InvalidUpgradeEligibilityError instantiation."""
        error = InvalidUpgradeEligibilityError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, InvalidUpgradeEligibilityError)

    def test_invalid_upgrade_eligibility_error_with_message(self):
        """Test InvalidUpgradeEligibilityError with custom message."""
        message = "Device is not eligible for upgrade - contract period not met"
        error = InvalidUpgradeEligibilityError(message)
        self.assertEqual(str(error), message)

    def test_invalid_upgrade_eligibility_error_raise_and_catch(self):
        """Test raising and catching InvalidUpgradeEligibilityError."""
        device_id = "DEV-12345"
        message = f"Device {device_id} upgrade eligibility check failed"

        with self.assertRaisesRegex(InvalidUpgradeEligibilityError, re.escape(message)):
            self.raise_error(message, InvalidUpgradeEligibilityError)

    def test_service_modification_error_basic(self):
        """Test basic ServiceModificationError instantiation."""
        error = ServiceModificationError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, ServiceModificationError)

    def test_service_modification_error_with_message(self):
        """Test ServiceModificationError with custom message."""
        message = "Failed to modify service plan - incompatible features"
        error = ServiceModificationError(message)
        self.assertEqual(str(error), message)

    def test_service_modification_error_raise_and_catch(self):
        """Test raising and catching ServiceModificationError."""
        service_id = "SVC-001"
        message = f"Cannot modify service {service_id} - plan is locked"

        with self.assertRaisesRegex(ServiceModificationError, re.escape(message)):
            self.raise_error(message, ServiceModificationError)

    def test_payment_method_not_found_error_basic(self):
        """Test basic PaymentMethodNotFoundError instantiation."""
        error = PaymentMethodNotFoundError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, PaymentMethodNotFoundError)

    def test_payment_method_not_found_error_with_message(self):
        """Test PaymentMethodNotFoundError with custom message."""
        message = "Payment method ending in 1234 not found"
        error = PaymentMethodNotFoundError(message)
        self.assertEqual(str(error), message)

    def test_payment_method_not_found_error_raise_and_catch(self):
        """Test raising and catching PaymentMethodNotFoundError."""
        payment_id = "PAY-MISSING"
        message = f"Payment method {payment_id} not found for account"

        with self.assertRaisesRegex(PaymentMethodNotFoundError, re.escape(message)):
            self.raise_error(message, PaymentMethodNotFoundError)

    def test_insufficient_funds_error_basic(self):
        """Test basic InsufficientFundsError instantiation."""
        error = InsufficientFundsError()
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, InsufficientFundsError)

    def test_insufficient_funds_error_with_message(self):
        """Test InsufficientFundsError with custom message."""
        message = "Insufficient funds - attempted charge of $99.99 failed"
        error = InsufficientFundsError(message)
        self.assertEqual(str(error), message)

    def test_insufficient_funds_error_raise_and_catch(self):
        """Test raising and catching InsufficientFundsError."""
        amount = 150.00
        available = 50.00
        message = f"Insufficient funds: required ${amount}, available ${available}"

        with self.assertRaisesRegex(InsufficientFundsError, re.escape(message)):
            self.raise_error(message, InsufficientFundsError)

    def test_all_errors_inherit_from_exception(self):
        """Test that all custom errors properly inherit from Exception."""
        error_classes = [
            InvalidRequestError,
            ResourceNotFoundError,
            ValidationError,
            AccountNotFoundError,
            DeviceNotFoundError,
            ServicePlanNotFoundError,
            InsufficientPermissionsError,
            DuplicateAccountError,
            InvalidUpgradeEligibilityError,
            ServiceModificationError,
            PaymentMethodNotFoundError,
            InsufficientFundsError,
        ]

        for error_class in error_classes:
            self.assertTrue(issubclass(error_class, Exception))

    def test_error_classes_are_distinct(self):
        """Test that all error classes are distinct types."""
        error_classes = [
            InvalidRequestError,
            ResourceNotFoundError,
            ValidationError,
            AccountNotFoundError,
            DeviceNotFoundError,
            ServicePlanNotFoundError,
            InsufficientPermissionsError,
            DuplicateAccountError,
            InvalidUpgradeEligibilityError,
            ServiceModificationError,
            PaymentMethodNotFoundError,
            InsufficientFundsError,
        ]

        # Test that each error class is unique
        for i, error_class1 in enumerate(error_classes):
            for j, error_class2 in enumerate(error_classes):
                if i != j:
                    self.assertNotEqual(error_class1, error_class2)
                    self.assertFalse(issubclass(error_class1, error_class2))
                    self.assertFalse(issubclass(error_class2, error_class1))

    def test_multiple_arguments_in_error_messages(self):
        """Test that custom errors can handle multiple arguments."""
        # Test with multiple arguments
        error1 = ValidationError("Field validation failed", "email", "Invalid format")
        self.assertIn("Field validation failed", str(error1))

        error2 = AccountNotFoundError("Account", "ACCT-123", "not found")
        self.assertIn("Account", str(error2))

    def test_error_with_numeric_arguments(self):
        """Test that custom errors can handle numeric arguments."""
        error = InsufficientFundsError("Required: $", 99.99, ", Available: $", 50.00)
        error_str = str(error)
        self.assertIn("99.99", error_str)
        self.assertIn("50.0", error_str)

    def test_error_with_empty_message(self):
        """Test custom errors with empty messages."""
        errors = [
            InvalidRequestError(""),
            ResourceNotFoundError(""),
            ValidationError(""),
            AccountNotFoundError(""),
            DeviceNotFoundError(""),
            ServicePlanNotFoundError(""),
            InsufficientPermissionsError(""),
            DuplicateAccountError(""),
            InvalidUpgradeEligibilityError(""),
            ServiceModificationError(""),
            PaymentMethodNotFoundError(""),
            InsufficientFundsError(""),
        ]

        for error in errors:
            self.assertEqual(str(error), "")

    def test_error_repr_format(self):
        """Test that custom errors have proper repr format."""
        message = "Test error message"
        error = ValidationError(message)

        error_repr = repr(error)
        self.assertIn("ValidationError", error_repr)
        self.assertIn(message, error_repr)

    def test_nested_exception_handling(self):
        """Test that custom errors can be used in nested try-catch blocks."""

        def inner_function():
            raise DeviceNotFoundError("Inner device error")

        def outer_function():
            try:
                inner_function()
            except DeviceNotFoundError as e:
                raise AccountNotFoundError(f"Outer error caused by: {e}")

        with self.assertRaisesRegex(
            AccountNotFoundError, re.escape("Outer error caused by: Inner device error")
        ):
            outer_function()

    def test_error_chaining(self):
        """Test error chaining with custom errors."""
        original_error = ValidationError("Original validation error")

        try:
            raise original_error
        except ValidationError as e:
            chained_error = ServiceModificationError("Service error occurred")
            chained_error.__cause__ = e

            with self.assertRaisesRegex(
                ServiceModificationError, re.escape("Service error occurred")
            ):
                self.raise_error("Service error occurred", ServiceModificationError)

    def test_error_with_exception_context(self):
        """Test custom errors used within exception context managers."""
        errors_caught = []

        error_types_and_messages = [
            (InvalidRequestError, "Invalid request test"),
            (ResourceNotFoundError, "Resource not found test"),
            (ValidationError, "Validation test"),
            (AccountNotFoundError, "Account not found test"),
            (DeviceNotFoundError, "Device not found test"),
        ]

        for error_type, message in error_types_and_messages:
            with self.assertRaisesRegex(error_type, re.escape(message)):
                self.raise_error(message, error_type)
            errors_caught.append((error_type, message))

        # Verify all errors were caught with correct messages
        self.assertEqual(len(errors_caught), 5)
        for i, (error_type, message) in enumerate(error_types_and_messages):
            caught_type, caught_message = errors_caught[i]
            self.assertEqual(caught_type, error_type)
            self.assertEqual(caught_message, message)


if __name__ == "__main__":
    unittest.main()
