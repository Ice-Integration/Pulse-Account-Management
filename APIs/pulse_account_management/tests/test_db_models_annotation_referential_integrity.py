"""Tests for PK/FK annotations and referential integrity on the CES Account
Management DB models, exercising both the construction-time path
(`model_validate`) and the post-construction sweep
(`DatabaseObjectMixin.validate_all_references`).
"""

import copy
import unittest

from common_utils.db_object_utils import (
    DatabaseObjectMixin,
    ForeignKey,
)

from pulse_account_management.SimulationEngine.common_models import (
    AvailablePlansCatalog,
    CatalogFeature,
    CatalogPlan,
    Order,
)
from pulse_account_management.SimulationEngine.db_models import (
    AccountDetails,
    PulseAccountManagementDB,
)


def _valid_account_dict(*, with_order: bool = False, with_service: bool = False):
    """Return a minimal, fully-consistent AccountDetails dict for tests."""
    orders = {}
    if with_order:
        orders["ORD-100"] = {
            "orderId": "ORD-100",
            "status": "Processing",
            "orderDate": "2024-05-15",
            "accountId": "ACC-100",
            "estimatedCompletionDate": "2024-05-30",
            "orderType": "CHANGE_PLAN",
            "statusDescription": "Plan change in progress.",
        }

    services = []
    if with_service:
        services.append({
            "serviceId": "SVC-1",
            "planName": "Test Basic",
            "planId": "PLAN-TEST-1",
            "monthlyCost": 25.00,
            "dataAllowance": "10GB",
            "activeFeatures": [],
        })

    return {
        "accountId": "ACC-100",
        "isVerified": True,
        "customerName": "Jane Doe",
        "contactEmail": "jane@example.com",
        "contactPhone": "555-0100",
        "billingAddress": {
            "recipientName": "Jane Doe",
            "streetAddressLine1": "1 Main St",
            "city": "Anytown",
            "state": "CA",
            "zipCode": "90001",
            "country": "US",
        },
        "serviceAddress": {
            "recipientName": "Jane Doe",
            "streetAddressLine1": "1 Main St",
            "city": "Anytown",
            "state": "CA",
            "zipCode": "90001",
            "country": "US",
        },
        "communicationPreferences": {
            "emailOptIn": True,
            "smsOptIn": False,
        },
        "services": services,
        "devices": [],
        "securityPinSet": True,
        "orders": orders,
    }


def _valid_db_dict(
    *,
    with_order: bool = False,
    with_service: bool = False,
    catalog_location: str = "plans",
):
    """Return a minimal, fully-consistent PulseAccountManagementDB dict for tests."""
    available_plans: dict[str, dict] = {"plans": {}, "old_plans": {}}
    if with_service:
        available_plans[catalog_location]["PLAN-TEST-1"] = {
            "id": "PLAN-TEST-1",
            "type": "PLAN",
            "name": "Test Basic",
            "monthlyCost": 25.00,
            "dataAllowance": "10GB",
        }

    return {
        "accountDetails": {
            "ACC-100": _valid_account_dict(with_order=with_order, with_service=with_service),
        },
        "availablePlans": available_plans,
        "orders": {},
        "use_real_datastore": False,
    }


class TestPrimaryKeyAnnotations(unittest.TestCase):
    """Verify PrimaryKey() metadata is declared on the expected fields."""

    def test_account_details_primary_key(self):
        self.assertEqual(
            DatabaseObjectMixin._get_model_primary_key_field_names(AccountDetails),
            ["accountId"],
        )

    def test_order_primary_key(self):
        self.assertEqual(
            DatabaseObjectMixin._get_model_primary_key_field_names(Order),
            ["orderId"],
        )

    def test_get_instance_primary_keys_returns_value(self):
        order = Order(
            orderId="ORD-100",
            status="Processing",
            orderDate="2024-05-15",
            accountId="ACC-100",
            estimatedCompletionDate="2024-05-30",
            orderType="CHANGE_PLAN",
            statusDescription="Plan change in progress.",
        )
        self.assertEqual(
            DatabaseObjectMixin._get_instance_primary_keys(order),
            {"orderId": "ORD-100"},
        )


class TestForeignKeyAnnotations(unittest.TestCase):
    """Verify ForeignKey() metadata is declared on the expected fields."""

    def test_db_inherits_database_object_mixin(self):
        self.assertTrue(issubclass(PulseAccountManagementDB, DatabaseObjectMixin))

    def test_iter_foreign_key_matches_finds_order_account_id(self):
        db = PulseAccountManagementDB(**_valid_db_dict(with_order=True))
        matches = list(DatabaseObjectMixin._iter_foreign_key_matches(db))

        account_matches = [m for m in matches if m.field_name == "accountId"]
        self.assertEqual(len(account_matches), 1)
        self.assertEqual(account_matches[0].value, "ACC-100")
        self.assertIsInstance(account_matches[0].foreign_key, ForeignKey)
        self.assertEqual(account_matches[0].foreign_key.entity, "AccountDetails")
        self.assertEqual(account_matches[0].foreign_key.field, "accountId")

    def test_only_expected_foreign_keys_declared(self):
        """The CES DB should declare exactly two FK fields:
        Order.accountId and ServicePlan.planId."""
        db = PulseAccountManagementDB(**_valid_db_dict(with_order=True, with_service=True))
        matches = list(DatabaseObjectMixin._iter_foreign_key_matches(db))
        self.assertEqual(
            sorted({m.field_name for m in matches}),
            ["accountId", "planId"],
        )


class TestCatalogPlanAnnotations(unittest.TestCase):
    """Verify the discriminated catalog union and `ServicePlan.planId` FK wiring."""

    def test_catalog_plan_has_primary_key(self):
        self.assertEqual(
            DatabaseObjectMixin._get_model_primary_key_field_names(CatalogPlan),
            ["id"],
        )

    def test_catalog_feature_has_no_primary_key(self):
        # nothing FK's to feature ids, so no PK annotation
        self.assertEqual(
            DatabaseObjectMixin._get_model_primary_key_field_names(CatalogFeature),
            [],
        )

    def test_discriminator_routes_to_correct_concrete_class(self):
        catalog = AvailablePlansCatalog(
            plans={
                "PLAN-X": {
                    "id": "PLAN-X",
                    "type": "PLAN",
                    "name": "Plan X",
                    "monthlyCost": 10.0,
                },
                "FEAT-Y": {
                    "id": "FEAT-Y",
                    "type": "FEATURE_ADDON",
                    "name": "Feature Y",
                    "monthlyCost": 5.0,
                },
            },
        )
        self.assertIsInstance(catalog.plans["PLAN-X"], CatalogPlan)
        self.assertIsInstance(catalog.plans["FEAT-Y"], CatalogFeature)

    def test_iter_foreign_key_matches_finds_service_plan_id(self):
        db = PulseAccountManagementDB(**_valid_db_dict(with_service=True))
        matches = list(DatabaseObjectMixin._iter_foreign_key_matches(db))

        plan_matches = [m for m in matches if m.field_name == "planId"]
        self.assertEqual(len(plan_matches), 1)
        self.assertEqual(plan_matches[0].value, "PLAN-TEST-1")
        self.assertEqual(plan_matches[0].foreign_key.entity, "CatalogPlan")
        self.assertEqual(plan_matches[0].foreign_key.field, "id")


class TestValidateAllReferences(unittest.TestCase):
    """Cover the post-construction validate_all_references() path."""

    def test_passes_on_clean_db(self):
        db = PulseAccountManagementDB(**_valid_db_dict(with_order=True))
        db.validate_all_references()

    def test_passes_on_db_without_orders(self):
        db = PulseAccountManagementDB(**_valid_db_dict())
        db.validate_all_references()

    def test_passes_with_plan_in_current_catalog(self):
        db = PulseAccountManagementDB(**_valid_db_dict(with_service=True, catalog_location="plans"))
        db.validate_all_references()

    def test_passes_with_plan_in_old_plans_catalog(self):
        """Grandfathered plans live in old_plans; FK must resolve there too."""
        db = PulseAccountManagementDB(
            **_valid_db_dict(with_service=True, catalog_location="old_plans")
        )
        db.validate_all_references()

    def test_detects_dangling_plan_id(self):
        """A planId not present in either plans or old_plans must fail."""
        db = PulseAccountManagementDB(**_valid_db_dict(with_service=True))
        db.accountDetails["ACC-100"].services[0].__dict__["planId"] = "GHOST-PLAN"
        with self.assertRaises(ValueError) as cm:
            db.validate_all_references()
        self.assertIn("non-existent record GHOST-PLAN", str(cm.exception))

    def test_detects_plan_id_pointing_at_feature(self):
        """planId resolving to a FEATURE_ADDON row is rejected by the discriminator."""
        data = _valid_db_dict(with_service=True)
        # feature entry shares the dict with plans; only the discriminator gates the FK
        data["availablePlans"]["plans"]["FEAT-ONLY"] = {
            "id": "FEAT-ONLY",
            "type": "FEATURE_ADDON",
            "name": "Decoy Feature",
            "monthlyCost": 5.0,
        }
        db = PulseAccountManagementDB(**data)
        db.accountDetails["ACC-100"].services[0].__dict__["planId"] = "FEAT-ONLY"
        with self.assertRaises(ValueError) as cm:
            db.validate_all_references()
        self.assertIn("non-existent record FEAT-ONLY", str(cm.exception))

    def test_detects_dangling_account_id_in_account_order(self):
        """Mutating an Order.accountId to a non-existent value should be caught."""
        db = PulseAccountManagementDB(**_valid_db_dict(with_order=True))
        db.accountDetails["ACC-100"].orders["ORD-100"].__dict__["accountId"] = "GHOST_ACCOUNT"
        with self.assertRaises(ValueError) as cm:
            db.validate_all_references()
        self.assertIn("non-existent record GHOST_ACCOUNT", str(cm.exception))

    def test_detects_dangling_account_id_in_top_level_order(self):
        """Top-level Order with bad accountId should also be caught."""
        data = _valid_db_dict()
        data["orders"]["ORD-200"] = {
            "orderId": "ORD-200",
            "status": "Processing",
            "orderDate": "2024-05-15",
            "accountId": "ACC-100",
            "estimatedCompletionDate": "2024-05-30",
            "orderType": "ADD_FEATURE",
            "statusDescription": "Adding feature.",
        }
        db = PulseAccountManagementDB(**data)
        # Mutate after construction so the FK violation only surfaces in
        # validate_all_references.
        db.orders["ORD-200"].__dict__["accountId"] = "DOES_NOT_EXIST"
        with self.assertRaises(ValueError) as cm:
            db.validate_all_references()
        self.assertIn("non-existent record DOES_NOT_EXIST", str(cm.exception))


class TestMixinHelpers(unittest.TestCase):
    """Smoke-test the helpers DatabaseObjectMixin contributes to the DB model."""

    def test_from_dict_round_trip(self):
        original = _valid_db_dict(with_order=True)
        db = PulseAccountManagementDB.from_dict(copy.deepcopy(original))
        self.assertIsInstance(db, PulseAccountManagementDB)
        self.assertIn("ACC-100", db.accountDetails)
        self.assertIn("ORD-100", db.accountDetails["ACC-100"].orders)

    def test_update_dict_serializes_back(self):
        db = PulseAccountManagementDB(**_valid_db_dict(with_order=True))
        target = {"junk": "to-be-cleared"}
        db.update_dict(target)
        self.assertNotIn("junk", target)
        self.assertIn("accountDetails", target)
        self.assertIn("ACC-100", target["accountDetails"])


if __name__ == "__main__":
    unittest.main()
