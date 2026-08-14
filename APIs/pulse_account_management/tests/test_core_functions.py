import os
import re
import sys
import unittest
from unittest.mock import patch

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from pulse_account_management.account_management import (
    cancel,
    check_device_upgrade_eligibility,
    escalate,
    fail,
    get_customer_account_details,
    modify_service_plan_or_feature,
    query_account_orders,
    query_available_plans_and_features,
    update_account_information,
)
from pulse_account_management.SimulationEngine.custom_errors import (
    AccountNotFoundError,
    ServicePlanNotFoundError,
)
from pulse_account_management.SimulationEngine.custom_errors import (
    ValidationError as CustomValidationError,
)
from pulse_account_management.SimulationEngine.db import DB
from pulse_account_management.tests.account_management_base_exception import (
    AccountManagementBaseTestCase,
)


class TestAccountManagementCoreFunctions(AccountManagementBaseTestCase):
    """
    Test suite for Account Management core functions.
    Focuses on input validation, output format, error handling, and transformations.
    """

    # Tests for get_customer_account_details
    def test_get_customer_account_details_success(self):
        """Test successful retrieval of customer account details."""
        result = get_customer_account_details("ACC888777666")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["accountId"], "ACC888777666")
        self.assertEqual(result["customerName"], "Jessica Davis")
        self.assertEqual(result["contactEmail"], "jessd@email.com")
        self.assertTrue(result["isVerified"])

        # Test billing address
        self.assertIsInstance(result["billingAddress"], dict)
        self.assertEqual(result["billingAddress"]["city"], "Brooklyn")
        self.assertEqual(result["billingAddress"]["state"], "NY")

        # Test devices
        self.assertIsInstance(result["devices"], list)
        self.assertEqual(len(result["devices"]), 2)
        device_ids = {d["deviceId"] for d in result["devices"]}
        self.assertIn("DEV006A", device_ids)
        dev006a = next(d for d in result["devices"] if d["deviceId"] == "DEV006A")
        self.assertEqual(dev006a["deviceId"], "DEV006A")

    def test_get_customer_account_details_success_by_phone_number(self):
        """Test successful retrieval of customer account details by phone number."""
        result = get_customer_account_details("(555) 555-0101")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["accountId"], "ACC112233445")
        self.assertEqual(result["customerName"], "David Chen")
        self.assertEqual(result["contactEmail"], "d.chen@web.net")
        self.assertTrue(result["isVerified"])

    def test_get_customer_account_details_success_by_unnormalized_phone_number(self):
        """Test successful retrieval of customer account details by phone number."""
        result = get_customer_account_details("(555) 444-5556")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["accountId"], "ACC888777666")
        self.assertEqual(result["customerName"], "Jessica Davis")
        self.assertEqual(result["contactEmail"], "jessd@email.com")
        self.assertTrue(result["isVerified"])

    def test_get_customer_account_details_success_by_normalized_phone_number(self):
        """Test successful retrieval of customer account details by phone number."""
        result = get_customer_account_details("(555) 444-5556")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["accountId"], "ACC888777666")
        self.assertEqual(result["customerName"], "Jessica Davis")
        self.assertEqual(result["contactEmail"], "jessd@email.com")
        self.assertTrue(result["isVerified"])

    def test_get_customer_account_details_failure_by_phone_number(self):
        """Test error handling for invalid phone number."""
        with self.assertRaisesRegex(
            AccountNotFoundError, re.escape("Account +15559999999 not found in the database.")
        ):
            get_customer_account_details(accountId="+15559999999")

    def test_get_customer_account_details_invalid_account(self):
        """Test error handling for invalid account ID."""
        with self.assertRaisesRegex(
            AccountNotFoundError, re.escape("Account INVALID-ACCOUNT not found in the database.")
        ):
            get_customer_account_details(accountId="INVALID-ACCOUNT")

    def test_get_customer_account_details_empty_account_id(self):
        """Test error handling for empty account ID."""
        with self.assertRaisesRegex(
            CustomValidationError, "accountId must be at least 1 characters long."
        ):
            get_customer_account_details(accountId="")

    # Tests for update_account_information
    def test_update_account_information_success(self):
        """Test successful account information update."""
        update_data = {
            "contactEmail": "new.email@example.com",
            "contactPhone": "999-888-7777",
        }

        result = update_account_information("ACC9876543218", update_data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["contactEmail"], "new.email@example.com")
        self.assertEqual(result["contactPhone"], "999-888-7777")

        # Verify the database was updated
        account = DB["accountDetails"]["ACC9876543218"]
        self.assertEqual(account["contactEmail"], "new.email@example.com")
        self.assertEqual(account["contactPhone"], "999-888-7777")

    def test_update_account_information_success_by_phone_number(self):
        """Test successful account information update."""
        update_data = {
            "contactEmail": "new.email@example.com",
            "contactPhone": "999-888-7777",
        }

        result = update_account_information("555-444-5556", update_data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["contactEmail"], "new.email@example.com")
        self.assertEqual(result["contactPhone"], "999-888-7777")

        # Verify the database was updated
        account = DB["accountDetails"]["ACC888777666"]
        self.assertEqual(account["contactEmail"], "new.email@example.com")
        self.assertEqual(account["contactPhone"], "999-888-7777")

    def test_update_account_information_invalid_account(self):
        """Test error handling for invalid account ID in update."""
        requestBody = {"contactEmail": "test@example.com"}

        with self.assertRaisesRegex(
            AccountNotFoundError, re.escape("Account INVALID-ACCOUNT not found in the database.")
        ):
            update_account_information(accountId="INVALID-ACCOUNT", requestBody=requestBody)

    def test_update_account_information_empty_account_id(self):
        """Test error handling for empty account ID in update."""
        requestBody = {"contactEmail": "test@example.com"}

        with self.assertRaisesRegex(
            CustomValidationError, re.escape("accountId must be at least 1 characters long.")
        ):
            update_account_information(accountId="", requestBody=requestBody)

    def test_update_account_information_invalid_phone_number(self):
        """Test error handling for invalid phone number format."""
        requestBody = {"contactPhone": "invalid-phone"}

        with self.assertRaisesRegex(
            CustomValidationError, re.escape("The phone number 'invalid-phone' is not valid.")
        ):
            update_account_information(accountId="ACC888777666", requestBody=requestBody)

    def test_update_account_information_account_id_whitespace(self):
        """Test error handling for empty account ID in update."""
        requestBody = {"contactEmail": "test@example.com"}

        with self.assertRaisesRegex(CustomValidationError, "accountId must be a non-empty string"):
            update_account_information(accountId="  ", requestBody=requestBody)

    # Tests for check_device_upgrade_eligibility
    def test_check_device_upgrade_eligibility_by_line_number(self):
        """Test device upgrade eligibility check by line number."""
        result = check_device_upgrade_eligibility("ACC-343536", "512-555-0110", "LINE_NUMBER")

        self.assertIsInstance(result, dict)
        self.assertFalse(result["isEligible"])
        self.assertEqual(result["remainingDevicePayments"], 19)
        self.assertIn("payment plan is active", result["reason"])

    def test_check_device_upgrade_eligibility_by_phone_number(self):
        """Test device upgrade eligibility check by line number."""
        result = check_device_upgrade_eligibility("555-321-7654", "555-321-7654", "LINE_NUMBER")

        self.assertIsInstance(result, dict)
        self.assertFalse(result["isEligible"])
        self.assertEqual(result["remainingDevicePayments"], 9)
        self.assertIn("payment plan is active", result["reason"])

    def test_check_device_upgrade_eligibility_by_device_id(self):
        """Test device upgrade eligibility check by device ID."""

        result = check_device_upgrade_eligibility("555-321-7654", "DEV007A", "DEVICE_ID")

        self.assertIsInstance(result, dict)
        self.assertFalse(result["isEligible"])

    def test_check_device_upgrade_eligibility_device_not_found(self):
        """Test error when device is not found."""
        with self.assertRaisesRegex(
            CustomValidationError,
            re.escape("Device with DEVICE_ID 'NONEXISTENT-DEVICE' not found on account."),
        ):
            check_device_upgrade_eligibility(
                accountId="ACC888777666",
                identifier="NONEXISTENT-DEVICE",
                identifierType="DEVICE_ID",
            )

    def test_check_device_upgrade_eligibility_invalid_identifier_type(self):
        """Test error for invalid identifier type."""
        with self.assertRaisesRegex(
            CustomValidationError, re.escape("Input should be 'LINE_NUMBER' or 'DEVICE_ID'")
        ):
            check_device_upgrade_eligibility(
                accountId="ACC888777666",
                identifier="some-identifier",
                identifierType="INVALID_TYPE",
            )

    def test_check_device_upgrade_eligibility_empty_account_id(self):
        """Test error for empty account ID."""
        with self.assertRaisesRegex(
            CustomValidationError, "accountId must be at least 1 characters long."
        ):
            check_device_upgrade_eligibility(
                accountId="", identifier="DEV006A", identifierType="DEVICE_ID"
            )

    def test_check_device_upgrade_eligibility_empty_identifier(self):
        """Test error for empty identifier."""
        with self.assertRaisesRegex(
            CustomValidationError, "identifier must be at least 1 characters long."
        ):
            check_device_upgrade_eligibility(
                accountId="ACC888777666", identifier="", identifierType="DEVICE_ID"
            )

    def test_check_device_upgrade_eligibility_invalid_phone_identifier(self):
        """Test error for invalid phone number identifier."""
        with self.assertRaisesRegex(
            CustomValidationError, re.escape("The phone number 'invalid-phone' is not valid.")
        ):
            check_device_upgrade_eligibility(
                accountId="ACC888777666", identifier="invalid-phone", identifierType="LINE_NUMBER"
            )

    def test_check_device_upgrade_eligibility_invalid_account(self):
        """Test error for non-existent account ID."""
        with self.assertRaisesRegex(
            AccountNotFoundError, re.escape("Account INVALID-ACCOUNT not found in the database.")
        ):
            check_device_upgrade_eligibility(
                accountId="INVALID-ACCOUNT", identifier="DEV006A", identifierType="DEVICE_ID"
            )

    def test_check_device_upgrade_eligibility_device_ineligible_payment_plan_active(self):
        """Test device upgrade eligibility check by device ID."""
        result = check_device_upgrade_eligibility("555-867-5309", "DEV005A", "DEVICE_ID")

        self.assertIsInstance(result, dict)
        self.assertFalse(result["isEligible"])
        self.assertIn("payment plan is active", result["reason"])

    def test_check_device_upgrade_eligibility_device_ineligible_by_line_number(self):
        """Test device upgrade eligibility check by line number."""

        DB["accountDetails"]["ACC888777666"]["devices"][0]["lineNumber"] = "n/a"
        result = check_device_upgrade_eligibility("ACC888777666", "DEV006A", "DEVICE_ID")

        self.assertIsInstance(result, dict)
        self.assertFalse(result["isEligible"])
        self.assertIn("lineNumber is n/a", result["reason"])

    def test_check_device_upgrade_eligibility_account_id_whitespace(self):
        """Test error handling for whitespace account ID."""
        with self.assertRaisesRegex(CustomValidationError, "accountId must be a non-empty string."):
            check_device_upgrade_eligibility(
                accountId="   ", identifier="DEV006A", identifierType="DEVICE_ID"
            )

    def test_check_device_upgrade_eligibility_identifier_whitespace(self):
        """Test error handling for whitespace identifier."""
        with self.assertRaisesRegex(
            CustomValidationError, "identifier must be a non-empty string."
        ):
            check_device_upgrade_eligibility(
                accountId="ACC888777666", identifier="   ", identifierType="DEVICE_ID"
            )

    # Tests for modify_service_plan_or_feature
    def test_modify_service_plan_change_plan(self):
        """Test changing service plan."""
        result = modify_service_plan_or_feature("ACC888777666", "CHANGE_PLAN", "P001", "P002")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("Basic Talk & Text", result["message"])

    def test_modify_service_plan_add_feature(self):
        """Test adding a feature to service plan."""
        result = modify_service_plan_or_feature("ACC888777666", "ADD_FEATURE", "F001", "P002")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("International Calling Pack", result["message"])

    def test_modify_service_plan_add_feature_by_phone_number(self):
        """Test adding a feature to service plan."""
        result = modify_service_plan_or_feature("ACC888777666", "ADD_FEATURE", "F001", "P002")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("International Calling Pack", result["message"])

    def test_modify_service_plan_remove_feature(self):
        """Test removing a feature from service plan."""
        result = modify_service_plan_or_feature("555-321-7654", "REMOVE_FEATURE", "F002", "P003")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("removed", result["message"])

    def test_modify_service_plan_invalid_account(self):
        """Test error for invalid account ID."""
        with self.assertRaisesRegex(
            AccountNotFoundError, re.escape("Account INVALID-ACCOUNT not found in the database.")
        ):
            modify_service_plan_or_feature(
                accountId="INVALID-ACCOUNT",
                action="CHANGE_PLAN",
                itemId="P001",
                currentPlanId="P002",
            )

    def test_modify_service_plan_empty_account_id(self):
        """Test error for empty account ID."""
        with self.assertRaisesRegex(
            CustomValidationError, "accountId must be at least 1 characters long."
        ):
            modify_service_plan_or_feature(
                accountId="", action="CHANGE_PLAN", itemId="P001", currentPlanId="P002"
            )

    def test_modify_service_plan_empty_item_id(self):
        """Test error for empty item ID."""
        with self.assertRaisesRegex(
            CustomValidationError, "itemId must be at least 1 characters long."
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666", action="CHANGE_PLAN", itemId="", currentPlanId="P002"
            )

    def test_modify_service_plan_whitespace_account_id_value_error(self):
        """Test ValueError for whitespace-only account ID string."""
        with self.assertRaisesRegex(CustomValidationError, "accountId must be a non-empty string."):
            modify_service_plan_or_feature(
                accountId="   ", action="CHANGE_PLAN", itemId="P001", currentPlanId="P002"
            )

    def test_modify_service_plan_whitespace_item_id_value_error(self):
        """Test ValueError for whitespace-only item ID string."""
        with self.assertRaisesRegex(CustomValidationError, "itemId must be a non-empty string."):
            modify_service_plan_or_feature(
                accountId="ACC888777666", action="CHANGE_PLAN", itemId="   ", currentPlanId="P002"
            )

    def test_modify_service_plan_whitespace_current_plan_id_value_error(self):
        """Test ValueError for whitespace-only currentPlanId string."""
        with self.assertRaisesRegex(
            CustomValidationError, "currentPlanId must be a non-empty string."
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666", action="CHANGE_PLAN", itemId="P001", currentPlanId="   "
            )

    def test_modify_service_plan_plan_not_found_in_account(self):
        """Test error when current plan is not found in account."""
        with self.assertRaisesRegex(
            CustomValidationError, re.escape("Item P999 not found in the database.")
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666", action="CHANGE_PLAN", itemId="P999", currentPlanId="P002"
            )

    def test_modify_service_plan_item_not_found_in_database(self):
        """Test error when item is not found in database."""
        with self.assertRaisesRegex(
            CustomValidationError, re.escape("Item NONEXISTENT-PLAN not found in the database.")
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666",
                action="CHANGE_PLAN",
                itemId="NONEXISTENT-PLAN",
                currentPlanId="P002",
            )

    def test_modify_service_plan_item_not_a_plan(self):
        """Test error when item is not a plan for CHANGE_PLAN action."""
        with self.assertRaisesRegex(
            ServicePlanNotFoundError, re.escape("Plan F001 not found in the account.")
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666", action="CHANGE_PLAN", itemId="P001", currentPlanId="F001"
            )

    def test_modify_service_plan_item_not_a_feature(self):
        """Test error when item is not a feature for ADD_FEATURE action."""
        with self.assertRaisesRegex(
            CustomValidationError, re.escape("Item P002 is not an add-on feature.")
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666", action="ADD_FEATURE", itemId="P002", currentPlanId="P002"
            )

    def test_modify_service_plan_add_feature_with_current_plan_id(self):
        """Test adding a feature to a specific plan using currentPlanId."""
        # First verify the feature is not already present
        account_details = get_customer_account_details("ACC888777666")
        plan_p003 = next((s for s in account_details["services"] if s["planId"] == "P002"), None)
        self.assertIsNotNone(plan_p003)

        # Ensure F001 is not already in the plan
        active_features = plan_p003.get("activeFeatures", [])
        if any(f.get("featureId") == "F001" for f in active_features):
            # Remove it first for clean test
            modify_service_plan_or_feature("ACC888777666", "REMOVE_FEATURE", "F001", "P002")

        # Now add the feature to the specific plan
        result = modify_service_plan_or_feature(
            "ACC888777666", "ADD_FEATURE", "F001", currentPlanId="P002"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("International Calling Pack", result["message"])
        self.assertIn("added to your plan", result["message"])

        # Verify the feature was added to the correct plan
        updated_account_details = get_customer_account_details("ACC888777666")
        updated_plan_p003 = next(
            (s for s in updated_account_details["services"] if s["planId"] == "P002"), None
        )
        self.assertIsNotNone(updated_plan_p003)
        self.assertTrue(
            any(f.get("featureId") == "F001" for f in updated_plan_p003["activeFeatures"])
        )
        fobj = next(f for f in updated_plan_p003["activeFeatures"] if f.get("featureId") == "F001")
        self.assertEqual(fobj["featureName"], "International Calling Pack")

    def test_modify_service_plan_remove_feature_with_current_plan_id(self):
        """Test removing a feature from a specific plan using currentPlanId."""
        # First add a feature to ensure it exists
        modify_service_plan_or_feature("ACC888777666", "ADD_FEATURE", "F001", currentPlanId="P002")

        # Verify the feature was added
        account_details = get_customer_account_details("ACC888777666")
        plan_p003 = next((s for s in account_details["services"] if s["planId"] == "P002"), None)
        self.assertIsNotNone(plan_p003)
        self.assertTrue(any(f.get("featureId") == "F001" for f in plan_p003["activeFeatures"]))

        # Now remove the feature from the specific plan
        result = modify_service_plan_or_feature(
            "ACC888777666", "REMOVE_FEATURE", "F001", currentPlanId="P002"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("F001", result["message"])
        self.assertIn("removed from your plan", result["message"])

        # Verify the feature was removed from the correct plan
        updated_account_details = get_customer_account_details("ACC888777666")
        updated_plan_p003 = next(
            (s for s in updated_account_details["services"] if s["planId"] == "P002"), None
        )
        self.assertIsNotNone(updated_plan_p003)
        active_features = updated_plan_p003.get("activeFeatures", [])
        self.assertFalse(any(f.get("featureId") == "F001" for f in active_features))

    def test_modify_service_plan_remove_feature_not_in_specified_plan(self):
        """Test error when trying to remove a feature that's not in the specified plan."""
        # Ensure F001 is not in P003 but might be in other plans
        account_details = get_customer_account_details("ACC888777666")
        plan_p003 = next((s for s in account_details["services"] if s["planId"] == "P002"), None)
        if plan_p003 and any(
            f.get("featureId") == "F001" for f in plan_p003.get("activeFeatures", [])
        ):
            modify_service_plan_or_feature(
                "ACC888777666", "REMOVE_FEATURE", "F001", currentPlanId="P002"
            )

        # Try to remove F001 from P003 where it doesn't exist
        with self.assertRaisesRegex(
            CustomValidationError,
            re.escape("Feature F001 was not found for the plan P002 and could not be removed."),
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666",
                action="REMOVE_FEATURE",
                itemId="F001",
                currentPlanId="P002",
            )

    def test_modify_service_plan_add_feature_to_plan_without_active_features(self):
        """Test adding a feature to a plan that doesn't have activeFeatures dictionary."""
        # Get account details to check plans
        account_details = get_customer_account_details("ACC888777666")

        # Find a plan or use P003 and ensure it has no activeFeatures
        plan_found = False
        for service in account_details["services"]:
            if service["planId"] == "P002":
                plan_found = True
                break

        if not plan_found:
            self.skipTest("Plan P003 not found in test account")

        # Add feature to the plan
        result = modify_service_plan_or_feature(
            "ACC888777666", "ADD_FEATURE", "F001", currentPlanId="P002"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "Success")
        self.assertIn("International Calling Pack", result["message"])

        # Verify activeFeatures dictionary was created and feature was added
        updated_account_details = get_customer_account_details("ACC888777666")
        updated_plan = next(
            (s for s in updated_account_details["services"] if s["planId"] == "P002"), None
        )
        self.assertIsNotNone(updated_plan)
        self.assertIn("activeFeatures", updated_plan)
        self.assertTrue(any(f.get("featureId") == "F001" for f in updated_plan["activeFeatures"]))

    def test_modify_service_plan_unsupported_action(self):
        """Test error for unsupported action type."""
        with self.assertRaisesRegex(
            CustomValidationError,
            re.escape("Input should be 'CHANGE_PLAN', 'ADD_FEATURE' or 'REMOVE_FEATURE'"),
        ):
            modify_service_plan_or_feature(
                accountId="ACC888777666",
                action="INVALID_ACTION",
                itemId="P001",
                currentPlanId="P002",
            )

    # Tests for query_available_plans_and_features
    @patch("pulse_account_management.SimulationEngine.utils._get_gemini_response")
    def test_query_available_plans_and_features_success(self, mock_get_gemini_response):
        """Test successful query for available plans."""
        # Mock the Gemini response
        mock_get_gemini_response.return_value = '[{"id": "P001", "name": "Basic Talk & Text", "description": "Unlimited talk and text within the country. No data included.", "type": "PLAN", "monthlyCost": 15, "dataAllowance": "0GB", "termsAndConditionsUrl": "https://api.sundaymobile.com/terms/P001", "compatibilityNotes": ""}]'

        result = query_available_plans_and_features("Basic Talk")

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["answer"], str)
        self.assertIn("Basic Talk & Text", result["answer"])
        self.assertIsInstance(result["snippets"], list)

    @patch("pulse_account_management.SimulationEngine.utils._get_gemini_response")
    def test_query_available_plans_and_features_no_match(self, mock_get_gemini_response):
        """Test query with no matching plans."""
        # Mock empty response for no matches
        mock_get_gemini_response.return_value = "[]"

        result = query_available_plans_and_features("NonexistentPlan")

        self.assertIsInstance(result, dict)
        self.assertIn("don't have specific information", result["answer"])

    def test_query_available_plans_empty_query(self):
        """Test error for empty query."""
        with self.assertRaisesRegex(
            CustomValidationError, "query must be at least 1 characters long."
        ):
            query_available_plans_and_features(query="")

    # Tests for query_account_orders

    def test_query_account_orders_success(self):
        """Test successful account orders query."""
        result = query_account_orders("789107", "accountId='ACC-12345'")

        self.assertIsInstance(result, dict)
        self.assertIn("789107", result["answer"])

    def test_query_account_orders_with_status_as_query(self):
        """Test successful account orders query."""
        result = query_account_orders("change", "accountId='ACC-12345'")

        self.assertIsInstance(result, dict)
        self.assertIn("change", result["answer"])

    def test_query_account_orders_no_access_to_order_history(self):
        """Test account orders query when no access to order history."""
        result = query_account_orders("recent order", "accountId='ACC888777666'")

        self.assertIsInstance(result, dict)
        self.assertIn("I don't have access to this order", result["answer"])

    def test_query_account_orders_empty_query(self):
        """Test error for empty query."""
        with self.assertRaisesRegex(
            CustomValidationError, "query must be at least 1 characters long."
        ):
            query_account_orders(query="", filter="accountId='ACC888777666'")

    def test_query_account_orders_empty_filter(self):
        """Test error for empty filter."""
        with self.assertRaisesRegex(
            CustomValidationError, "filter must be at least 1 characters long."
        ):
            query_account_orders(query="test query", filter="")

    def test_query_account_orders_filter_whitespace(self):
        """Test error for whitespace filter."""
        with self.assertRaisesRegex(CustomValidationError, "filter must be a non-empty string."):
            query_account_orders(query="test query", filter="   ")

    def test_query_account_orders_query_whitespace(self):
        """Test error for whitespace query."""
        with self.assertRaisesRegex(CustomValidationError, "query must be a non-empty string."):
            query_account_orders(query="   ", filter="accountId='ACC888777666'")

    # Tests for terminal functions
    def test_escalate_success(self):
        """Test successful escalation."""
        result = escalate("User requests human agent")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "escalate")
        self.assertEqual(result["reason"], "User requests human agent")
        self.assertIn("human agent", result["status"])

        # Verify database update
        self.assertIn("_end_of_conversation_status", DB)
        self.assertEqual(
            DB["_end_of_conversation_status"]["escalate"]["reason"], "User requests human agent"
        )

    def test_escalate_empty_reason_uses_fallback(self):
        """Test that empty escalation reason uses fallback."""
        result = escalate(reason="")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "escalate")
        self.assertEqual(result["reason"], "<placeholder reason for the escalation>")
        self.assertIn("human agent", result["status"])

    def test_fail_success(self):
        """Test successful failure handling."""
        result = fail("Could not understand user request")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "fail")
        self.assertEqual(result["reason"], "Could not understand user request")
        self.assertIn("unable to help", result["status"])

    def test_fail_empty_reason_uses_fallback(self):
        """Test that empty failure reason uses fallback."""
        result = fail(reason="")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "fail")
        self.assertEqual(result["reason"], "<placeholder reason for the failure>")
        self.assertIn("unable to help", result["status"])

    def test_cancel_success(self):
        """Test successful cancellation."""
        result = cancel("User asked to stop")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "cancel")
        self.assertEqual(result["reason"], "User asked to stop")
        self.assertIn("canceled", result["status"])

    def test_cancel_empty_reason_uses_fallback(self):
        """Test that empty cancellation reason uses fallback."""
        result = cancel(reason="")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "cancel")
        self.assertEqual(result["reason"], "<placeholder reason for the cancellation>")
        self.assertIn("canceled", result["status"])

    def test_cancel_whitespace_reason_uses_fallback(self):
        """Test that whitespace cancellation reason uses fallback."""
        result = cancel(reason="   ")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "cancel")
        self.assertEqual(result["reason"], "<placeholder reason for the cancellation>")
        self.assertIn("canceled", result["status"])


if __name__ == "__main__":
    unittest.main()
