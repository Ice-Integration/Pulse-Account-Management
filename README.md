# Pulse-Account-Management

# PulseLine Account API Simulation

## Overview
This package delivers an in-memory simulation of the inbound Sunday Mobile account management tool surface. Use it for agent and colab scenarios and tests. It covers customer identity checks, account detail retrieval, account edits, device upgrade eligibility, service plan and feature changes, and knowledge base lookups for plans, features, and order history. It does not connect to real billing, provisioning, or telephony systems.

## Summary
| Feature | Description |
|---|---|
| Main Resources | Account Details, Account Updates, Device Upgrades, Service Modifications, Knowledge Base |
| Key Operations | get_customer_account_details, update_account_information, check_device_upgrade_eligibility, modify_service_plan_or_feature, query_available_plans_and_features, query_account_orders, plus terminal helpers escalate, fail, cancel |
| Database | Process-local DB dict loaded from DBs/PulseLineAccountDefaultDB.json |
| Gating | The system must confirm the full name on the account before it allows modifications or detailed inquiries. |
| Realism Gap | query_available_plans_and_features and query_account_orders can hit a real datastore or infobot when use_real_datastore is True. Otherwise they return canned responses. |
| Source of Truth | Account Management DI drives conversational intent. Resolve conflicts using the Open Questions sheet (gym init and implementation win for tool shapes). |

## API Architecture

### Database Structure
The simulation runs on a single process-local DB dict (SimulationEngine/db.py), loaded from DBs/PulseLineAccountDefaultDB.json. The keys that drive lifecycle and behavior:

```
DB
├── accountDetails: {...}                  # Customer accounts, keyed or searchable by accountId.
├── availablePlans: [...]                   # Service plans and feature add-ons on offer.
├── use_real_datastore: bool               # Switches KB queries between a real external endpoint and canned responses.
├── _end_of_conversation_status: {...}     # Side effects from terminal tools (escalate, fail, cancel).
└── _error_simulator: {...}                # Config for simulating tool failures.
```

### Model Architecture
The API relies on dataclasses for its request and response models:

- `account_management.py`: core API methods and dataclasses (CustomerAccountDetails, ServicePlan, DeviceUpgradeEligibility, and others), plus terminal helpers (escalate, fail, cancel).

### Module Structure
```
pulseline_account_api/
├── __init__.py                             # Lazy tool imports (`_function_map`) and error simulator wrapping
├── account_management.py                   # @tool_spec functions: account/service tools and terminal helpers
└── SimulationEngine/
    ├── db.py                               # DB keys, load/save/reset functionality
    └── utils.py                            # Helpers for external infobot queries
```

## API Methods

### Account Information

**get_customer_account_details**
- Parameters: accountId (string)
- Behavior: Pulls full account details (billing, services, devices). This is the required first step for identity verification and for getting the currentPlanId needed by later modifications.

**update_account_information**
- Parameters: accountId (string), requestBody (AccountInformationUpdate)
- Behavior: Updates specific fields such as billing address, contact email or phone, and communication preferences. Only the fields included in the request body get changed.

### Upgrades & Modifications

**check_device_upgrade_eligibility**
- Parameters: accountId (string), identifier (string), identifierType (LINE_NUMBER or DEVICE_ID)
- Behavior: Checks whether a given device is still under an active payment plan. If it isn't, the device qualifies for an upgrade.

**modify_service_plan_or_feature**
- Parameters: accountId, action (CHANGE_PLAN, ADD_FEATURE, REMOVE_FEATURE), itemId, currentPlanId, customerConfirmationText
- Behavior:
  - currentPlanId is required for every action, since it identifies which service plan is being changed.
  - The system checks that itemId exists in the availablePlans DB and matches the expected type (PLAN vs FEATURE_ADDON).
  - Returns a ServiceModificationResponse with a dynamically calculated effectiveDate and an estimated bill impact.

### Knowledge Base Queries

**query_available_plans_and_features**
- Parameters: query (string)
- Behavior: Calls an external infobot endpoint when use_real_datastore is True. Otherwise it returns a canned "I don't have any information" response.

**query_account_orders**
- Parameters: query (string), filter (string)
- Behavior: The filter must read exactly `accountId='<customer_account_id>'`. As with the plans query, real responses depend on use_real_datastore.

### Call Termination

**Terminal helpers (escalate, fail, cancel)**
- Parameters: reason (string)
- Behavior: Writes the given reason into DB['_end_of_conversation_status'] and returns a status dictionary that ends the conversation flow.

## Behavioral Subtleties & Realism Gaps
*(Several details below trace back to answers resolved in the Open Questions sheet.)*

- **Plans vs Features**: Plans are the baseline phone and internet offerings, while features are add-ons layered on top. A plan can carry any number of features. The DB holds compatibility notes, but the simulation logic doesn't enforce them strictly.
- **Effective Dates**: In production, feature changes land immediately or within a day, while plan changes take a few weeks. The simulation computes effectiveDate dynamically based on the action, for example 7 days out for plan changes and immediately for added features.
- **currentPlanId Is Mandatory**: Even ADD_FEATURE and REMOVE_FEATURE require currentPlanId, since a customer may hold more than one active plan and the system needs to know which one to touch.
- **External Infobot Queries**: query_account_orders and query_available_plans_and_features route through _query_infobot, which calls an external endpoint that needs credentials. For a local simulation without credentials, keep use_real_datastore set to False or mock the utils.py responses.

## Updates
Changelog-style notes covering behavior added after the first published gym shape (see git history for the exact version).

- Terminal tools escalate, fail, and cancel are now first-class exported tools (_function_map in __init__.py). They write _end_of_conversation_status into the DB along with the reason and action type.
- Exclude-none mode: calling `set_service_returns_exclude_none_mode("pulseline_account_api", True)` in __init__.py strips omitted optional fields from serialized tool responses (following the common_utils convention).

## Testing
- **Unit / Integration** (`APIs/pulseline_account_api/tests/`): covers tool contracts, account updates, plan modifications, and DB validation.
- **Scenario Tests** (`scenario_testing/tests/pulseline_account_api/`): driven by YAML under `scenario_testing/scenarios/pulseline_account_api/`.
- **Regression** (`regression_testing/tests/pulseline_account_api/`): aligned with `regression_testing/scenarios/pulseline_account_api/`.

Run tests from the repo root:

```
pytest APIs/pulseline_account_api/tests/ -v
pytest scenario_testing/tests/pulseline_account_api/ -v
pytest regression_testing/tests/pulseline_account_api/ -v
```

## Dependencies
- common_utils (DbManager, error handling, tool_spec, validation helpers)
- dataclasses
