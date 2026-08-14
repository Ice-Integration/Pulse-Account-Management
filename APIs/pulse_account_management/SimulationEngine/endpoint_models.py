"""
Request and Response models for pulse_account_management API endpoints.
"""

from typing import Any, List, Literal, Optional

from common_utils.models import StrictBaseModel
from pydantic import Field, ValidationInfo, field_validator

from pulse_account_management.SimulationEngine.common_models import (
    DeviceIdentifierType,
    ServiceModificationAction,
)
from pulse_account_management.SimulationEngine.custom_errors import ValidationError
from pulse_account_management.SimulationEngine.utils import validate_non_empty_string


class DeviceUpgradeEligibility(StrictBaseModel):
    isEligible: bool = Field(
        ...,
        description="Whether the device is eligible for upgrade.",
    )
    eligibilityDate: Optional[str] = Field(
        None,
        description="Date when device becomes eligible for upgrade.",
    )
    reason: Optional[str] = Field(
        None,
        description="Explanation if not eligible.",
    )
    earlyUpgradeOptions: Optional[str] = Field(
        None,
        description="Early upgrade options if available.",
    )
    remainingDevicePayments: Optional[float] = Field(
        None,
        description="Remaining device payments.",
        ge=0.0,
    )


class ServiceModificationResponse(StrictBaseModel):
    status: str = Field(
        ...,
        description="Success status of the operation",
    )
    effectiveDate: str = Field(
        ...,
        description="Date when the modification becomes effective.",
    )
    message: str = Field(
        ...,
        description="Human-readable confirmation message.",
    )
    nextBillImpactEstimate: str = Field(
        ...,
        description="Estimated impact on next bill.",
    )
    orderId: str = Field(
        ...,
        description="Unique order identifier for tracking.",
    )


class KnowledgeBaseSnippet(StrictBaseModel):
    text: Optional[str] = Field(
        None,
        description="Snippet content",
    )
    title: Optional[str] = Field(
        None,
        description="Source title",
    )
    uri: Optional[str] = Field(
        None,
        description="Reference URL",
    )


class KnowledgeBaseQueryResponse(StrictBaseModel):
    answer: Optional[str] = Field(
        None,
        description="Human-readable answer to the query",
    )
    snippets: List[KnowledgeBaseSnippet] = Field(
        default_factory=list,
        description="List of snippets from the knowledge base.",
    )


class TerminalResponse(StrictBaseModel):
    action: str = Field(
        ...,
        description="The action type (e.g. 'escalate', 'fail', 'cancel').",
    )
    reason: str = Field(
        ...,
        description="The provided reason for the action.",
        min_length=1,
    )
    status: str = Field(
        ...,
        description="Status message for the user.",
        min_length=1,
        max_length=100,
    )


class PlanSearchResult(StrictBaseModel):
    """Individual plan or feature search result."""

    id: Optional[str] = Field(
        None,
        description="Unique identifier for the plan or feature.",
    )
    name: Optional[str] = Field(
        None,
        description="Display name of the plan or feature.",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the plan or feature.",
    )
    type: Optional[str] = Field(
        None,
        description="Type of result: 'PLAN' or 'FEATURE_ADDON'.",
    )
    monthlyCost: Optional[float] = Field(
        None,
        description="Monthly cost in dollars.",
        ge=0.0,
    )
    dataAllowance: Optional[str] = Field(
        None,
        description="Data allowance (e.g., 'Unlimited', '10GB').",
    )
    termsAndConditionsUrl: Optional[str] = Field(
        None,
        description="URL to the terms and conditions page.",
    )
    compatibilityNotes: Optional[str] = Field(
        None,
        description="Notes about compatibility with other plans or devices.",
    )


class CommunicationPreferencesInput(StrictBaseModel):
    """Input parameters for updating communication preferences."""

    emailOptIn: Optional[bool] = Field(
        None, description="Whether the customer wants to receive email communications."
    )
    smsOptIn: Optional[bool] = Field(
        None, description="Whether the customer wants to receive SMS communications."
    )


class GetCustomerAccountDetailsInput(StrictBaseModel):
    """Input parameters for retrieving customer account details."""

    accountId: str = Field(
        ...,
        description="""The unique identifier for the customer's account or phone number.
                    Example: "ACC123456789" or "122-334-4556" """,
    )

    _validate_accountId = field_validator("accountId", mode="before")(validate_non_empty_string)


class AddressInput(StrictBaseModel):
    recipientName: Optional[str] = Field(
        None,
        description="Name of the recipient at this address.",
    )
    streetAddressLine1: Optional[str] = Field(
        None,
        description="Primary street address line.",
    )
    streetAddressLine2: Optional[str] = Field(
        None,
        description="Secondary street address line (apartment, suite, etc.).",
    )
    city: Optional[str] = Field(
        None,
        description="City name.",
    )
    state: Optional[str] = Field(
        None,
        description="State or province code.",
    )
    zipCode: Optional[str] = Field(
        None,
        description="ZIP or postal code.",
    )
    country: Optional[str] = Field(
        None,
        description="Country code or name.",
    )

    @field_validator(
        "recipientName",
        "streetAddressLine1",
        "streetAddressLine2",
        "city",
        "state",
        "zipCode",
        "country",
        mode="before",
    )
    @classmethod
    def validate_address_fields(cls, v: Any, info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValidationError(f"{info.field_name} must be a string.")

        lengths = {
            "recipientName": (1, 200),
            "streetAddressLine1": (1, 200),
            "streetAddressLine2": (None, 200),
            "city": (1, 100),
            "state": (2, 10),
            "zipCode": (1, 20),
            "country": (2, 50),
        }

        min_len, max_len = lengths.get(info.field_name, (None, None))
        if min_len is not None and len(v) < min_len:
            raise ValidationError(f"{info.field_name} must be at least {min_len} characters long.")
        if max_len is not None and len(v) > max_len:
            raise ValidationError(f"{info.field_name} must be at most {max_len} characters long.")

        return v


class AccountInformationUpdateInput(StrictBaseModel):
    billingAddress: Optional[AddressInput] = Field(
        None,
        description="The billing address of the customer.",
    )
    serviceAddress: Optional[AddressInput] = Field(
        None,
        description="The service address of the customer.",
    )
    communicationPreferences: Optional[CommunicationPreferencesInput] = Field(
        None,
        description="The communication preferences of the customer.",
    )
    contactEmail: Optional[str] = Field(
        None,
        description="The email address of the customer. Must be a valid email address.",
    )
    contactPhone: Optional[str] = Field(
        None,
        description="New contact phone number in any valid format (e.g., 555-123-4567, (555) 123-4567, 5551234567). Will be normalized.",
    )


class UpdateAccountInformationInput(StrictBaseModel):
    """Input parameters for updating account information."""

    accountId: str = Field(
        ...,
        description="""The unique identifier for the customer's account or phone number.
Example: "ACC888777666" or "222-334-4556" """,
    )
    requestBody: AccountInformationUpdateInput = Field(
        ...,
        description="""Dictionary containing the new information to be updated.
Only include the fields you want to change. Fields with None values will be ignored.""",
    )

    _validate_accountId = field_validator("accountId", mode="before")(validate_non_empty_string)


class CheckDeviceUpgradeEligibilityInput(StrictBaseModel):
    """Input parameters for checking device upgrade eligibility."""

    accountId: str = Field(
        ...,
        description="""The unique identifier for the customer's account or phone number.
Example: "ACC123456789" or "222-334-4556" """,
    )
    identifier: str = Field(
        ...,
        description="""The phone number or device ID to check. Examples:
- For LINE_NUMBER: "555-123-4567"
- For DEVICE_ID: "DEV987654321" """,
    )
    identifierType: Literal["LINE_NUMBER", "DEVICE_ID"] = Field(
        ...,
        description="""Specifies the type of the identifier provided. Must be one of:
- "LINE_NUMBER": Use when searching by phone number
- "DEVICE_ID": Use when searching by device identifier """,
    )

    _validate_strings = field_validator("accountId", "identifier", mode="before")(
        validate_non_empty_string
    )

    @field_validator("identifierType", mode="before")
    @classmethod
    def validate_identifier_type(cls, v: Any) -> str:
        valid_values = [e.value for e in DeviceIdentifierType]
        if v not in valid_values:
            formatted_values = (
                ", ".join(f"'{val}'" for val in valid_values[:-1]) + f" or '{valid_values[-1]}'"
            )
            raise ValidationError(f"Input should be {formatted_values}")
        return v


class ModifyServicePlanOrFeatureInput(StrictBaseModel):
    """Input parameters for modifying service plan or feature."""

    accountId: str = Field(
        ...,
        description="""The unique identifier for the customer's account or phone number.
Example: "ACC123456789" or "222-334-4556" """,
    )
    action: Literal["CHANGE_PLAN", "ADD_FEATURE", "REMOVE_FEATURE"] = Field(
        ...,
        description="""The type of modification to perform:
- "CHANGE_PLAN": Replaces current plan with a new one specified in itemId.
- "ADD_FEATURE": Adds a feature specified in itemId to the current plan.
- "REMOVE_FEATURE": Removes a feature specified in itemId. """,
    )
    itemId: str = Field(
        ...,
        description="""The unique identifier for the plan or feature being actioned.
Examples:
- For a plan: "PLAN_UNL_PRO"
- For a feature: "FEAT_INTL_CALL" """,
    )
    currentPlanId: str = Field(
        ...,
        description="""The ID of the customer's current plan to ensure the correct plan is being replaced or modified.
Example: "PLAN_UNL_PLUS" """,
    )
    customerConfirmationText: Optional[str] = Field(
        default=None,
        description="""A summary of the change that the user has explicitly agreed to.
Used for logging and auditing purposes. """,
    )

    _validate_strings = field_validator("accountId", "itemId", "currentPlanId", mode="before")(
        validate_non_empty_string
    )

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, v: Any) -> str:
        valid_values = [e.value for e in ServiceModificationAction]
        if v not in valid_values:
            formatted_values = (
                ", ".join(f"'{val}'" for val in valid_values[:-1]) + f" or '{valid_values[-1]}'"
            )
            raise ValidationError(f"Input should be {formatted_values}")
        return v


class QueryAvailablePlansAndFeaturesInput(StrictBaseModel):
    """Input parameters for querying available plans and features."""

    query: str = Field(
        ...,
        description="""The user's question, phrased as a clear, specific search query.
Examples:
- "details of Unlimited Pro plan data allowance"
- "cost of international calling pass feature"
- "what plans include mobile hotspot" """,
    )

    _validate_query = field_validator("query", mode="before")(validate_non_empty_string)


class QueryAccountOrdersInput(StrictBaseModel):
    """Input parameters for querying account orders."""

    query: str = Field(
        ...,
        description="""The user's question about their orders. Examples:
- "What was the shipping status of my most recent order?"
- "How much did I pay for the phone I bought in May?"
- "Show me my order history for the past 3 months" """,
    )
    filter: str = Field(
        ...,
        description="""An expression to filter the search to the specific customer's
account. The format MUST be "accountId='<customer_account_id>'".
Example: "accountId='ACC123456789'" """,
    )

    _validate_strings = field_validator("query", "filter", mode="before")(validate_non_empty_string)


class EscalateInput(StrictBaseModel):
    """Input parameters for escalate action."""

    reason: Optional[str] = Field(
        default=None,
        description="""A clear and concise explanation for the escalation. This reason will be logged and shown to the human agent. Examples:
- "The user wants to file a formal complaint about their billing"
- "The user is requesting account closure which requires human approval"
- "The user is experiencing technical issues beyond my capabilities" """,
    )


class FailInput(StrictBaseModel):
    """Input parameters for fail action."""

    reason: Optional[str] = Field(
        default=None,
        description="""A clear and concise internal-facing explanation for why the task failed. This is used for logging and improving the agent. Examples:
- "After three attempts, I could not understand the user's request"
- "User provided unclear instructions and did not respond to clarification"
- "Unable to parse the user's intent from their messages" """,
    )


class CancelInput(StrictBaseModel):
    """Input parameters for cancel action."""

    reason: Optional[str] = Field(
        default=None,
        description="""A clear and concise summary of why the task was canceled,
based on the user's request. Examples:
- "The user stated they did not have their account information ready"
- "The user changed their mind and no longer wants to proceed"
- "The user asked to cancel the current operation" """,
    )
