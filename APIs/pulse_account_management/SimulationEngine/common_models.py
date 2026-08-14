"""
Common models shared between database and endpoint validation.
"""

from enum import Enum
from typing import Annotated, Dict, List, Literal, Optional, Union

from common_utils.db_object_utils import ForeignKey, PrimaryKey
from common_utils.models import StrictBaseModel
from pydantic import Field


class DeviceIdentifierType(str, Enum):
    """Type of identifier used to look up a device."""

    LINE_NUMBER = "LINE_NUMBER"
    DEVICE_ID = "DEVICE_ID"


class ServiceModificationAction(str, Enum):
    """Action to perform when modifying a service plan."""

    CHANGE_PLAN = "CHANGE_PLAN"
    ADD_FEATURE = "ADD_FEATURE"
    REMOVE_FEATURE = "REMOVE_FEATURE"


class Address(StrictBaseModel):
    recipientName: str = Field(
        ...,
        description="Name of the recipient at this address.",
        min_length=1,
        max_length=200,
    )
    streetAddressLine1: str = Field(
        ...,
        description="Primary street address line.",
        min_length=1,
        max_length=200,
    )
    streetAddressLine2: Optional[str] = Field(
        None,
        description="Secondary street address line (apartment, suite, etc.).",
        max_length=200,
    )
    city: str = Field(
        ...,
        description="City name.",
        min_length=1,
        max_length=100,
    )
    state: str = Field(
        ...,
        description="State or province code.",
        min_length=2,
        max_length=10,
    )
    zipCode: str = Field(
        ...,
        description="ZIP or postal code.",
        min_length=1,
        max_length=20,
    )
    country: str = Field(
        ...,
        description="Country code or name.",
        min_length=2,
        max_length=50,
    )


class CommunicationPreferences(StrictBaseModel):
    emailOptIn: bool = Field(
        ...,
        description="Whether the customer wants to receive email communications.",
    )
    smsOptIn: bool = Field(
        ...,
        description="Whether the customer wants to receive SMS communications.",
    )


class Device(StrictBaseModel):
    deviceId: str = Field(
        ...,
        description="Unique device identifier",
        min_length=1,
        max_length=50,
    )
    deviceName: str = Field(
        ...,
        description="Name of the device",
        min_length=1,
        max_length=200,
    )
    lineNumber: str = Field(
        ...,
        description="Phone number associated with the device",
        min_length=1,
        max_length=50,
    )
    upgradeEligibilityDate: str = Field(
        ...,
        description="Date when device becomes eligible for upgrade",
        min_length=1,
        max_length=50,
    )
    paymentPlanActive: bool = Field(
        ...,
        description="Whether device has an active payment plan",
    )
    paymentPlanRemainingMonths: int = Field(
        ...,
        description="Remaining months on payment plan",
        ge=0,
    )


class ActiveFeature(StrictBaseModel):
    featureId: str = Field(
        ...,
        description="Unique identifier for the feature.",
        min_length=1,
        max_length=50,
    )
    featureName: str = Field(
        ...,
        description="Name of the feature.",
        min_length=1,
        max_length=200,
    )
    monthlyCost: float = Field(
        ...,
        description="Monthly cost of the feature.",
        ge=0.0,
    )


class CatalogPlan(StrictBaseModel):
    """A PLAN entry in the `availablePlans` catalog.

    Customer-account `ServicePlan.planId` values are foreign keys against this
    entity's `id`. The discriminator (`type`) ensures the FK resolver only
    matches genuine plan rows, not feature-addon rows that share the catalog
    dictionary.
    """

    type: Literal["PLAN"]
    id: Annotated[str, PrimaryKey()] = Field(
        ...,
        description="Unique identifier for the plan.",
        min_length=1,
        max_length=50,
    )
    name: str = Field(
        ...,
        description="Display name of the plan.",
        min_length=1,
        max_length=200,
    )
    description: Optional[str] = Field(
        None,
        description="Marketing description of the plan.",
    )
    monthlyCost: float = Field(
        ...,
        description="Monthly cost of the plan.",
        ge=0.0,
    )
    dataAllowance: Optional[str] = Field(
        None,
        description="Data allowance label (e.g. 'Unlimited', '10GB').",
    )
    compatibilityNotes: Optional[str] = Field(
        None,
        description="Notes about plan compatibility / restrictions.",
    )
    termsAndConditionsUrl: Optional[str] = Field(
        None,
        description="URL pointing at the plan's terms and conditions.",
    )
    activeFeatures: List[ActiveFeature] = Field(
        default_factory=list,
        description="Bundled features included with this plan template (catalog-side, "
        "not customer-side).",
    )


class CatalogFeature(StrictBaseModel):
    """A FEATURE_ADDON entry in the `availablePlans` catalog.

    Modelled as the second arm of the catalog discriminated union so that
    Pydantic can validate plan and feature catalog entries cohabiting the same
    dictionary without confusing one for the other.
    """

    type: Literal["FEATURE_ADDON"]
    id: str = Field(
        ...,
        description="Unique identifier for the feature add-on.",
        min_length=1,
        max_length=50,
    )
    name: str = Field(
        ...,
        description="Display name of the feature.",
        min_length=1,
        max_length=200,
    )
    description: Optional[str] = Field(
        None,
        description="Marketing description of the feature.",
    )
    monthlyCost: float = Field(
        ...,
        description="Monthly cost of the feature.",
        ge=0.0,
    )
    dataAllowance: Optional[str] = Field(
        None,
        description="Data allowance label, if applicable.",
    )
    compatibilityNotes: Optional[str] = Field(
        None,
        description="Notes about feature compatibility / restrictions.",
    )
    termsAndConditionsUrl: Optional[str] = Field(
        None,
        description="URL pointing at the feature's terms and conditions.",
    )


CatalogEntry = Annotated[
    Union[CatalogPlan, CatalogFeature],
    Field(discriminator="type"),
]


class AvailablePlansCatalog(StrictBaseModel):
    """The `availablePlans` catalog, split into current and historical buckets.

    Both `plans` and `old_plans` are heterogeneous in production: each contains
    a mix of PLAN and FEATURE_ADDON entries. The discriminator on `CatalogEntry`
    keeps that valid while still letting the FK resolver pick out only PLAN
    rows when matching `ServicePlan.planId`.
    """

    plans: Dict[str, CatalogEntry] = Field(
        default_factory=dict,
        description="Currently offered plans and feature add-ons, keyed by id.",
    )
    old_plans: Dict[str, CatalogEntry] = Field(
        default_factory=dict,
        description="Historical / grandfathered plans and feature add-ons, keyed by id.",
    )


class ServicePlan(StrictBaseModel):
    serviceId: str = Field(
        ...,
        description="Unique identifier for the service.",
    )
    planName: str = Field(
        ...,
        description="Name of the service plan.",
    )
    planId: Annotated[str, ForeignKey("CatalogPlan", field="id")] = Field(
        ...,
        description="Unique identifier for the plan; references CatalogPlan.id.",
    )
    monthlyCost: float = Field(
        ...,
        description="Monthly cost of the service.",
        ge=0.0,
    )
    dataAllowance: Optional[str] = Field(
        None,
        description="Data allowance for the service (e.g., 'Unlimited', '10GB').",
    )
    activeFeatures: List[ActiveFeature] = Field(
        default_factory=list,
        description="List of active features for this service.",
    )


class Order(StrictBaseModel):
    orderId: Annotated[str, PrimaryKey()] = Field(
        ...,
        description="Unique order identifier for tracking.",
        min_length=1,
    )
    status: str = Field(
        ...,
        description="Current status of the order (e.g., 'Processing', 'Shipped', 'Completed').",
        min_length=1,
    )
    orderDate: str = Field(
        ...,
        description="Date the order was placed in ISO 8601 format.",
        min_length=1,
    )
    accountId: Annotated[str, ForeignKey("AccountDetails", field="accountId")] = Field(
        ...,
        description="Account ID associated with this order.",
        min_length=1,
    )
    estimatedCompletionDate: str = Field(
        ...,
        description="Estimated date for order completion in ISO 8601 format.",
        min_length=1,
    )
    orderType: str = Field(
        ...,
        description="Type of order (e.g., 'CHANGE_PLAN', 'ADD_FEATURE', 'REMOVE_FEATURE').",
        min_length=1,
    )
    statusDescription: str = Field(
        ...,
        description="Human-readable description of the order status.",
        min_length=1,
    )


class BaseAccountDetails(StrictBaseModel):
    """Base account details shared between endpoint responses and database storage."""

    accountId: str = Field(
        ...,
        description="Unique identifier for the account.",
        min_length=1,
        max_length=50,
    )
    isVerified: bool = Field(
        ...,
        description="Whether the account is verified.",
    )
    customerName: str = Field(
        ...,
        description="Full name of the customer.",
        min_length=1,
        max_length=200,
    )
    contactEmail: str = Field(
        ...,
        description="Contact email address for the customer.",
        min_length=1,
        max_length=200,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    )
    contactPhone: str = Field(
        ...,
        description="Contact phone number for the customer.",
        min_length=1,
        max_length=20,
    )
    billingAddress: Address = Field(
        ...,
        description="Billing address for the account.",
    )
    serviceAddress: Address = Field(
        ...,
        description="Service address for the account.",
    )
    communicationPreferences: CommunicationPreferences = Field(
        ...,
        description="Communication preferences for the customer.",
    )
    services: List[ServicePlan] = Field(
        default_factory=list,
        description="List of services associated with the account.",
    )
    devices: List[Device] = Field(
        default_factory=list,
        description="List of devices associated with the account.",
    )
    securityPinSet: bool = Field(
        ...,
        description="Whether a security PIN has been set for the account.",
    )
