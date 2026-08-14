import json
import os
import unittest

from pulse_account_management.SimulationEngine.db import DB, load_state, reset_db, save_state
from pulse_account_management.SimulationEngine.db_models import AccountDetails
from pulse_account_management.tests.account_management_base_exception import (
    AccountManagementBaseTestCase,
)


class TestStateValidation(AccountManagementBaseTestCase):
    """
    Test suite for validating the state of the database.
    """

    def setUp(self):
        super().setUp()
        self.db_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "DBs",
            "PulseAccountManagementDefaultDB.json",
        )
        reset_db()
        load_state(self.db_path)
        self.DB = DB.copy()
        self.temp_db_file = self.db_path + ".temp"

        if os.path.exists(self.temp_db_file):
            os.remove(self.temp_db_file)
        else:
            temp_db = {
                "accountDetails": {},
                "availablePlans": {},
                "use_real_datastore": False,
                "_end_of_conversation_status": {},
            }
            with open(self.temp_db_file, "w") as f:
                json.dump(temp_db, f)

    def tearDown(self):
        super().tearDown()
        reset_db()
        if os.path.exists(self.temp_db_file):
            os.remove(self.temp_db_file)

    def test_load_db_from_file(self):
        """
        Test that the database can be loaded from a file.
        """
        load_state(self.temp_db_file)
        self.assertEqual(len(DB["accountDetails"]), 0)
        self.assertEqual(DB["use_real_datastore"], False)

    def test_save_db_to_file(self):
        """Test save/load round-trip with a valid account."""
        load_state(self.temp_db_file)
        DB["accountDetails"] = {
            "test_account": {
                "accountId": "test_account",
                "isVerified": True,
                "customerName": "Test Customer",
                "contactEmail": "test@example.com",
                "contactPhone": "555-000-0000",
                "billingAddress": {
                    "recipientName": "Test",
                    "streetAddressLine1": "1 Main St",
                    "city": "City",
                    "state": "TX",
                    "zipCode": "10000",
                    "country": "US",
                },
                "serviceAddress": {
                    "recipientName": "Test",
                    "streetAddressLine1": "1 Main St",
                    "city": "City",
                    "state": "TX",
                    "zipCode": "10000",
                    "country": "US",
                },
                "communicationPreferences": {"emailOptIn": True, "smsOptIn": False},
                "services": [],
                "devices": [],
                "securityPinSet": False,
            }
        }
        save_state(self.temp_db_file)
        load_state(self.temp_db_file)
        self.assertEqual(len(DB["accountDetails"]), 1)
        self.assertEqual(DB["accountDetails"]["test_account"]["accountId"], "test_account")


class TestDatabaseValidation(AccountManagementBaseTestCase):
    """
    Test suite for validating the sample database against Pydantic models.
    """

    def test_initial_db_state_validation(self):
        """
        Test that the initial database state loaded in the base case
        conforms to the Account model. This test implicitly runs
        due to the setUpClass logic in the base case.
        """
        try:
            # Validate account details if present
            if "accountDetails" in self._initial_db_state:
                for account in self._initial_db_state["accountDetails"].values():
                    AccountDetails.model_validate(account)
        except Exception as e:
            self.fail(f"Initial DB state validation failed in base class: {e}")

    def test_db_module_harmony(self):
        """
        Test that the database used by the db module is in harmony with the sample DB
        after setup.
        """
        try:
            # Validate account details if present
            if "accountDetails" in DB:
                for account in DB["accountDetails"].values():
                    AccountDetails.model_validate(account)
        except Exception as e:
            self.fail(f"DB module data structure validation failed after setUp: {e}")


if __name__ == "__main__":
    unittest.main()
