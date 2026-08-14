"""
Database models for validating the Pulse Account Management database schema.
"""

from typing import Annotated, Dict, List, Optional

from common_utils.db_object_utils import DatabaseObjectMixin, PrimaryKey
from common_utils.models import StrictBaseModel
from pydantic import ConfigDict, Field

from pulse_account_management.SimulationEngine.common_models import (
    AvailablePlansCatalog,
    BaseAccountDetails,
    Order,
)


class AccountDetails(BaseAccountDetails):
    """Account details as stored in the database."""

    accountId: Annotated[str, PrimaryKey()] = Field(
        ...,
        description="Unique identifier for the account.",
        min_length=1,
        max_length=50,
    )
    orders: Dict[str, Order] = Field(
        default_factory=dict,
        description="Orders associated with this account, keyed by order ID.",
    )


class ErrorSimulator(StrictBaseModel):
    """Error simulator configuration"""

    model_config = ConfigDict(populate_by_name=True)

    example_function_name: List[str] = Field(
        default_factory=list,
        alias="_example_function_name",
        description="List of example function names for error simulation.",
    )


class StatusSchema(StrictBaseModel):
    """Common schema for status fields with reason, action, and status"""

    reason: str = Field(
        ...,
        description="Reason for the status.",
        min_length=1,
        max_length=500,
    )
    action: str = Field(
        ...,
        description="Action taken.",
        min_length=1,
        max_length=200,
    )
    status: str = Field(
        ...,
        description="Current status.",
        min_length=1,
        max_length=100,
    )


class EndOfConversationStatus(StrictBaseModel):
    """End of conversation status with structured fields"""

    escalate: Optional[StatusSchema] = Field(
        None,
        description="Escalation status with reason, action, and status.",
    )
    fail: Optional[StatusSchema] = Field(
        None,
        description="Failure status at end of conversation.",
    )
    cancel: Optional[StatusSchema] = Field(
        None,
        description="Cancellation status at end of conversation.",
    )


class PulseAccountManagementStrictBaseModel(StrictBaseModel):
    """Service-specific base model with str_strip_whitespace and populate_by_name."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)


class PulseAccountManagementDB(PulseAccountManagementStrictBaseModel, DatabaseObjectMixin):
    """
    Root model that validates the entire Pulse Account Management database structure.

    This model ensures all data in the database conforms to the defined schemas
    for account details, services, devices, addresses, and communication preferences.
    """

    error_simulator: ErrorSimulator = Field(
        default_factory=ErrorSimulator,
        alias="_error_simulator",
        description="Error simulator configuration for testing purposes.",
    )
    end_of_conversation_status: EndOfConversationStatus = Field(
        default_factory=EndOfConversationStatus,
        alias="_end_of_conversation_status",
        description="Status information at the end of conversation.",
    )
    use_real_datastore: bool = Field(
        default=False,
        description="Whether to use real datastore or simulation.",
    )
    accountDetails: Dict[str, AccountDetails] = Field(
        default_factory=dict,
        description="Dictionary of account details indexed by account ID.",
    )
    availablePlans: AvailablePlansCatalog = Field(
        default_factory=AvailablePlansCatalog,
        description="Available plans and features catalog.",
    )
    orders: Dict[str, Order] = Field(
        default_factory=dict,
        description="Orders at the DB level (used in some test setups).",
    )
    order_id_counter: int = Field(
        default=100000,
        description="Auto-incrementing counter for generating unique order IDs.",
    )
