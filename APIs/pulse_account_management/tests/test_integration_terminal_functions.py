import unittest

# Relative imports for the service's terminal functions
from pulse_account_management import cancel, escalate, fail
from pulse_account_management.SimulationEngine import db


# Import the base test case with error handler
class TestTerminalFunctionsIntegration(unittest.TestCase):
    """
    Integration test suite for the terminal functions in 'pulse_account_management' service.

    These functions (escalate, fail, cancel) are terminal actions that end conversations
    and store status information in the database. This test suite validates:
    1. Proper status storage in the database
    2. Correct return value formatting
    3. Error handling for invalid inputs
    4. Database state management across multiple terminal actions
    """

    def setUp(self):
        """
        Set up the in-memory database with a clean state.
        This method is called before each test function execution.
        """
        # Reset the database to ensure a clean state for each test
        db.reset_db()

        # Ensure the conversation status key is properly initialized
        if "_end_of_conversation_status" in db.DB:
            del db.DB["_end_of_conversation_status"]

    def tearDown(self):
        """
        Clean up after each test to ensure no side effects.
        """
        # Clean up the conversation status
        if "_end_of_conversation_status" in db.DB:
            del db.DB["_end_of_conversation_status"]

    def test_escalate_function_integration(self):
        """
        Test the escalate terminal function integration workflow.

        Validates:
        1. Function executes successfully with valid reason
        2. Database stores the escalation reason correctly
        3. Return value contains expected fields and values
        4. Status message is appropriate for user display
        """
        # Test data
        escalation_reason = "User requested to speak with a manager about billing dispute"

        # Execute the escalate function
        result = escalate(reason=escalation_reason)

        # Verify the return value structure and content
        self.assertIsInstance(result, dict, "Escalate should return a dictionary")
        self.assertEqual(result["action"], "escalate", "Action should be 'escalate'")
        self.assertEqual(result["reason"], escalation_reason, "Reason should match input")
        self.assertIn(
            "connected to a human agent",
            result["status"].lower(),
            "Status should indicate human agent connection",
        )

        # Verify database state
        self.assertIn(
            "_end_of_conversation_status", db.DB, "Database should contain conversation status"
        )
        self.assertIn(
            "escalate",
            db.DB["_end_of_conversation_status"],
            "Database should contain escalation status",
        )
        self.assertEqual(
            db.DB["_end_of_conversation_status"]["escalate"]["reason"],
            escalation_reason,
            "Database should store the correct escalation reason",
        )

    def test_fail_function_integration(self):
        """
        Test the fail terminal function integration workflow.

        Validates:
        1. Function executes successfully with valid reason
        2. Database stores the failure reason correctly
        3. Return value contains expected fields and values
        4. Status message is apologetic and user-friendly
        """
        # Test data
        failure_reason = "Unable to understand user request after three clarification attempts"

        # Execute the fail function
        result = fail(reason=failure_reason)

        # Verify the return value structure and content
        self.assertIsInstance(result, dict, "Fail should return a dictionary")
        self.assertEqual(result["action"], "fail", "Action should be 'fail'")
        self.assertEqual(result["reason"], failure_reason, "Reason should match input")
        self.assertIn("sorry", result["status"].lower(), "Status should contain an apology")
        self.assertIn(
            "unable to help", result["status"].lower(), "Status should indicate inability to help"
        )

        # Verify database state
        self.assertIn(
            "_end_of_conversation_status", db.DB, "Database should contain conversation status"
        )
        self.assertIn(
            "fail", db.DB["_end_of_conversation_status"], "Database should contain failure status"
        )
        self.assertEqual(
            db.DB["_end_of_conversation_status"]["fail"]["reason"],
            failure_reason,
            "Database should store the correct failure reason",
        )

    def test_cancel_function_integration(self):
        """
        Test the cancel terminal function integration workflow.

        Validates:
        1. Function executes successfully with valid reason
        2. Database stores the cancellation reason correctly
        3. Return value contains expected fields and values
        4. Status message confirms the cancellation
        """
        # Test data
        cancellation_reason = "User stated they no longer want to proceed with plan change"

        # Execute the cancel function
        result = cancel(reason=cancellation_reason)

        # Verify the return value structure and content
        self.assertIsInstance(result, dict, "Cancel should return a dictionary")
        self.assertEqual(result["action"], "cancel", "Action should be 'cancel'")
        self.assertEqual(result["reason"], cancellation_reason, "Reason should match input")
        self.assertIn("canceled", result["status"].lower(), "Status should confirm cancellation")

        # Verify database state
        self.assertIn(
            "_end_of_conversation_status", db.DB, "Database should contain conversation status"
        )
        self.assertIn(
            "cancel",
            db.DB["_end_of_conversation_status"],
            "Database should contain cancellation status",
        )
        self.assertEqual(
            db.DB["_end_of_conversation_status"]["cancel"]["reason"],
            cancellation_reason,
            "Database should store the correct cancellation reason",
        )

    def test_multiple_terminal_actions_integration(self):
        """
        Test integration workflow where multiple terminal actions are called.

        This simulates a scenario where different terminal functions might be called
        in sequence (though in practice, only one should be used per conversation).

        Validates:
        1. Database can store multiple terminal action statuses
        2. Each function maintains its own status entry
        3. Later calls don't overwrite the entire status structure
        """
        # Execute multiple terminal functions
        escalate_reason = "Technical issue beyond agent capabilities"
        fail_reason = "Could not parse user intent"
        cancel_reason = "User requested to stop the process"

        escalate_result = escalate(reason=escalate_reason)
        fail_result = fail(reason=fail_reason)
        cancel_result = cancel(reason=cancel_reason)

        # Verify all functions returned proper results
        self.assertEqual(escalate_result["action"], "escalate")
        self.assertEqual(fail_result["action"], "fail")
        self.assertEqual(cancel_result["action"], "cancel")

        # Verify database contains all terminal action statuses
        conversation_status = db.DB["_end_of_conversation_status"]
        self.assertIn("escalate", conversation_status)
        self.assertIn("fail", conversation_status)
        self.assertIn("cancel", conversation_status)

        # Verify each status is stored correctly
        self.assertEqual(conversation_status["escalate"]["reason"], escalate_reason)
        self.assertEqual(conversation_status["fail"]["reason"], fail_reason)
        self.assertEqual(conversation_status["cancel"]["reason"], cancel_reason)

    def test_terminal_functions_fallback_handling_integration(self):
        """
        Test fallback handling integration for all terminal functions.

        Validates:
        1. Functions use fallback messages for empty/whitespace inputs
        2. Database state is properly updated with fallback values
        3. Invalid types still raise appropriate errors
        """
        # Test escalate with empty string uses fallback
        result = escalate(reason="")
        self.assertEqual(result["reason"], "<placeholder reason for the escalation>")
        self.assertEqual(result["action"], "escalate")

        # Reset DB for next test
        db.DB.pop("_end_of_conversation_status", None)

        # Test escalate with whitespace uses fallback
        result = escalate(reason="  ")
        self.assertEqual(result["reason"], "<placeholder reason for the escalation>")

        # Reset DB for next test
        db.DB.pop("_end_of_conversation_status", None)

        # Test fail with whitespace uses fallback
        result = fail(reason="   ")
        self.assertEqual(result["reason"], "<placeholder reason for the failure>")
        self.assertEqual(result["action"], "fail")

        # Reset DB for next test
        db.DB.pop("_end_of_conversation_status", None)

        # Test cancel with None uses fallback (reason is now optional)
        result = cancel(reason=None)
        self.assertEqual(result["reason"], "<placeholder reason for the cancellation>")
        self.assertEqual(result["action"], "cancel")

    def test_database_initialization_integration(self):
        """
        Test that terminal functions properly initialize database structures.

        Validates:
        1. Functions create the _end_of_conversation_status key if it doesn't exist
        2. Functions work correctly even when database is in various states
        """
        # Ensure database doesn't have the status key
        self.assertNotIn("_end_of_conversation_status", db.DB)

        # Call escalate - should initialize the database structure
        escalate_reason = "Database initialization test"
        escalate(reason=escalate_reason)

        # Verify database was properly initialized
        self.assertIn("_end_of_conversation_status", db.DB)
        self.assertIsInstance(db.DB["_end_of_conversation_status"], dict)
        self.assertEqual(
            db.DB["_end_of_conversation_status"]["escalate"]["reason"], escalate_reason
        )

        # Call fail - should work with existing structure
        fail_reason = "Working with existing database structure"
        fail(reason=fail_reason)

        # Verify both statuses are preserved
        conversation_status = db.DB["_end_of_conversation_status"]
        self.assertEqual(conversation_status["escalate"]["reason"], escalate_reason)
        self.assertEqual(conversation_status["fail"]["reason"], fail_reason)

    def test_terminal_functions_status_messages_integration(self):
        """
        Test the integration of status messages from terminal functions.

        Validates:
        1. Each function provides appropriate user-facing messages
        2. Messages are distinct and contextually appropriate
        3. Messages maintain consistent formatting
        """
        # Test escalate status message
        escalate_result = escalate(reason="Testing status message")
        escalate_status = escalate_result["status"]
        self.assertIsInstance(escalate_status, str)
        self.assertTrue(len(escalate_status) > 0)
        self.assertIn("human agent", escalate_status.lower())

        # Test fail status message
        fail_result = fail(reason="Testing status message")
        fail_status = fail_result["status"]
        self.assertIsInstance(fail_status, str)
        self.assertTrue(len(fail_status) > 0)
        self.assertIn("sorry", fail_status.lower())

        # Test cancel status message
        cancel_result = cancel(reason="Testing status message")
        cancel_status = cancel_result["status"]
        self.assertIsInstance(cancel_status, str)
        self.assertTrue(len(cancel_status) > 0)
        self.assertIn("canceled", cancel_status.lower())

        # Verify messages are different (each function has its own message)
        self.assertNotEqual(escalate_status, fail_status)
        self.assertNotEqual(escalate_status, cancel_status)
        self.assertNotEqual(fail_status, cancel_status)


if __name__ == "__main__":
    unittest.main()
