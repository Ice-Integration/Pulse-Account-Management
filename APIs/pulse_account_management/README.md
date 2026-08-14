# Pulse-Account-Management

## Pulse Account Management API Simulation

## Overview

This package provides an in-memory simulation of the **inbound Sunday Mobile Account Management** tool surface. It is designed for agent/colab scenarios and tests, simulating customer identity verification, account detail retrieval, account updates, device upgrade checks, service plan/feature modifications, and knowledge base queries (plans/features and order history). It is built for testing and does not integrate with real billing, provisioning, or telephony systems.

## Summary

| Feature | Description |
|---------|-------------|
| **Main Resources** | Account Details, Account Updates, Device Upgrades, Service Modifications, Knowledge Base |
| **Key Operations** | `get_customer_account_details`, `update_account_information`, `check_device_upgrade_eligibility`, `modify_service_plan_or_feature`, `query_available_plans_and_features`, `query_account_orders`, plus terminal helpers `escalate`, `fail`, `cancel` |
| **Database** | Process-local `DB` dict loaded from `DBs/PulseAccountManagementDefaultDB.json` |
| **Gating** | Identity verification (confirming the full name on the account) is required before proceeding with account modifications or detailed inquiries. |
| **Realism Gap** | `query_available_plans_and_features` and `query_account_orders` can use a real datastore/infobot when `use_real_datastore` is `True`, otherwise they return canned responses. |
| **Source of Truth** | [Account Management DI](https://docs.google.com/document/d/1sd3rUtxyJh2NGSuxqL9Lm7kczSTaXP2Rm8DWtbgehts/edit?usp=sharing) for conversational intent. Resolve conflicts per [Open Questions](https://docs.google.com/spreadsheets/d/1jac9EGdOnS2VGH6HZZp_jg0ZfyqtWg4G0JgxrK-FjzM/edit?gid=413345477#gid=413345477) (**gym init / implementation wins** for tool shapes). |

## API Architecture

### Database Structure

The simulation uses a single process-local `DB` dict (`SimulationEngine/db.py`), loaded from `DBs/PulseAccountManagementDefaultDB.json`. The lifecycle and behavior-driving keys are:

```text
DB
├── accountDetails: {...}                  # Dictionary or list of customer accounts, keyed/searchable by accountId.
├── availablePlans: [...]                   # Available service plans and feature add-ons.
├── use_real_datastore: bool               # Toggles whether KB queries hit a real external endpoint or return canned responses.
├── _end_of_conversation_status: {...}     # Side effects of terminal tools (escalate, fail, cancel).
└── _error_simulator: {...}                # Configuration for simulating tool failures.
```

### Model Architecture

The API uses a structured architecture with dataclasses for request/response models:

1. **`account_management.py`**: Core API methods and dataclasses (`CustomerAccountDetails`, `ServicePlan`, `DeviceUpgradeEligibility`, etc.), plus terminal helpers (`escalate`, `fail`, `cancel`).

### Module Structure

```text
pulse_account_management/
├── __init__.py                             # Lazy tool imports (`_function_map`) and error simulator wrapping
├── account_management.py                   # @tool_spec functions: Account/service tools and terminal helpers
└── SimulationEngine/
    ├── db.py                               # DB keys, load/save/reset functionality
    └── utils.py                            # Helpers for external infobot queries
```

## API Methods

### Account Information

#### `get_customer_account_details`
- **Parameters**: `accountId` (string)
- **Behavior**: Retrieves full account details (billing, services, devices). Required as the first step for identity verification and to obtain `currentPlanId` for modifications.

#### `update_account_information`
- **Parameters**: `accountId` (string), `requestBody` (`AccountInformationUpdate`)
- **Behavior**: Updates specific fields (billing address, contact email/phone, communication preferences). Only the fields provided in the request body are updated.

### Upgrades & Modifications

#### `check_device_upgrade_eligibility`
- **Parameters**: `accountId` (string), `identifier` (string), `identifierType` (`LINE_NUMBER` or `DEVICE_ID`)
- **Behavior**: Checks if a specific device has an active payment plan. If not, it is eligible for an upgrade.

#### `modify_service_plan_or_feature`
- **Parameters**: `accountId`, `action` (`CHANGE_PLAN`, `ADD_FEATURE`, `REMOVE_FEATURE`), `itemId`, `currentPlanId`, `customerConfirmationText`
- **Behavior**:
  - **`currentPlanId` is mandatory** for all actions to identify which service plan is being modified.
  - Validates that the `itemId` exists in the `availablePlans` DB and matches the expected type (`PLAN` vs `FEATURE_ADDON`).
  - Returns a `ServiceModificationResponse` with a dynamically calculated `effectiveDate` and estimated bill impact.

### Knowledge Base Queries

#### `query_available_plans_and_features`
- **Parameters**: `query` (string)
- **Behavior**: If `use_real_datastore` is `True`, calls an external infobot endpoint. Otherwise, returns a canned "I don't have any information" response.

#### `query_account_orders`
- **Parameters**: `query` (string), `filter` (string)
- **Behavior**: Requires `filter` to be exactly `"accountId='<customer_account_id>'"`. Like the plans query, relies on `use_real_datastore` for real responses.

### Call Termination

#### Terminal helpers (`escalate`, `fail`, `cancel`)
- **Parameters**: `reason` (string)
- **Behavior**: Updates `DB['_end_of_conversation_status']` with the provided reason and returns a status dictionary to end the conversation flow.

## Behavioral Subtleties & Realism Gaps

*(Note: Several of the implementation details below were resolved from the [Open Questions sheet](https://docs.google.com/spreadsheets/d/1jac9EGdOnS2VGH6HZZp_jg0ZfyqtWg4G0JgxrK-FjzM/edit?gid=413345477#gid=413345477).)*

1. **Plans vs Features**: Plans are baseline phone and internet plans, while features are add-ons. A plan can have any number of features. Compatibility notes exist in the DB but are not strictly enforced by the simulation logic.
2. **Effective Dates**: In reality, feature changes take place immediately/one day, and plan changes take place in a few weeks. The simulation calculates `effectiveDate` dynamically based on the action (e.g., 7 days for plan changes, immediate for adding features).
3. **`currentPlanId` is Mandatory**: Even for `ADD_FEATURE` and `REMOVE_FEATURE`, `currentPlanId` must be provided to determine which of the customer's potentially multiple active plans should be modified.
4. **External Infobot Queries**: The methods `query_account_orders` and `query_available_plans_and_features` use `_query_infobot` which calls an external endpoint requiring credentials. For local simulation without credentials, ensure `use_real_datastore` is `False` or mock the `utils.py` responses.

## Updates

Changelog-style notes for behavior added after the first published gym shape (exact version in git history).

- **Terminal tools**: `escalate`, `fail`, and `cancel` are first-class exported tools (`_function_map` in `__init__.py`). They update **`_end_of_conversation_status`** in the DB with the provided reason and action type.
- **Exclude-none mode**: `set_service_returns_exclude_none_mode("pulse_account_management", True)` in `__init__.py` strips omitted optional fields from serialized tool responses (`common_utils` convention).

## Testing

- **Unit / Integration** (`APIs/pulse_account_management/tests/`): Tests for tool contracts, account updates, plan modifications, and DB validation.
- **Scenario Tests** (`scenario_testing/tests/pulse_account_management/`): Driven by YAML under `scenario_testing/scenarios/pulse_account_management/`.
- **Regression** (`regression_testing/tests/pulse_account_management/`): Aligned with `regression_testing/scenarios/pulse_account_management/`.

Run tests from the repo root:
```bash
pytest APIs/pulse_account_management/tests/ -v
pytest scenario_testing/tests/pulse_account_management/ -v
pytest regression_testing/tests/pulse_account_management/ -v
```

## Dependencies

- `common_utils` (DbManager, error handling, `tool_spec`, validation helpers)
- `dataclasses`
