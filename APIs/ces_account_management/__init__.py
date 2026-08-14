"""
PulseLine Account API Simulation

This package provides a simulation of the PulseLine Account API functionality.
"""

import os

from common_utils.error_handling import get_package_error_mode
from common_utils.init_utils import create_error_simulator, resolve_function_import
from common_utils.service_returns_manager import set_service_returns_exclude_none_mode

from pulseline_account_api.SimulationEngine import utils as utils
from pulseline_account_api.SimulationEngine.db import DB as DB
from pulseline_account_api.SimulationEngine.db import load_state as load_state
from pulseline_account_api.SimulationEngine.db import save_state as save_state

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Configure runtime toggles for this service
set_service_returns_exclude_none_mode("pulseline_account_api", True)

# Function map
_function_map = {
    # Account management functions
    "get_customer_account_details": "pulseline_account_api.account_management.get_customer_account_details",
    "update_account_information": "pulseline_account_api.account_management.update_account_information",
    "check_device_upgrade_eligibility": "pulseline_account_api.account_management.check_device_upgrade_eligibility",
    "modify_service_plan_or_feature": "pulseline_account_api.account_management.modify_service_plan_or_feature",
    "query_available_plans_and_features": "pulseline_account_api.account_management.query_available_plans_and_features",
    "query_account_orders": "pulseline_account_api.account_management.query_account_orders",
    # Terminal functions
    "escalate": "pulseline_account_api.account_management.escalate",
    "fail": "pulseline_account_api.account_management.fail",
    "cancel": "pulseline_account_api.account_management.cancel",
}

# Separate utils map for utility functions
_utils_map = {
    # Query functions
    "query_plans_and_features_infobot": "pulseline_account_api.SimulationEngine.utils.query_plans_and_features_infobot",
    "query_account_orders_infobot": "pulseline_account_api.SimulationEngine.utils.query_account_orders_infobot",
    # Infobot configuration functions
    "get_infobot_config": "pulseline_account_api.SimulationEngine.utils.get_infobot_config",
    "update_infobot_config": "pulseline_account_api.SimulationEngine.utils.update_infobot_config",
    "save_infobot_config": "pulseline_account_api.SimulationEngine.utils.save_infobot_config",
    "load_infobot_config": "pulseline_account_api.SimulationEngine.utils.load_infobot_config",
    "reset_infobot_config": "pulseline_account_api.SimulationEngine.utils.reset_infobot_config",
    "show_infobot_config": "pulseline_account_api.SimulationEngine.utils.show_infobot_config",
    "set_infobot_mode": "pulseline_account_api.SimulationEngine.utils.set_infobot_mode",
    # Device related functions
    "get_device": "pulseline_account_api.SimulationEngine.utils.get_device",
    "get_service_plan": "pulseline_account_api.SimulationEngine.utils.get_service_plan",
    "update_service_plan": "pulseline_account_api.SimulationEngine.utils.update_service_plan",
    # Order related functions
    "create_order": "pulseline_account_api.SimulationEngine.utils.create_order",
    # Account related functions
    "get_account": "pulseline_account_api.SimulationEngine.utils.get_account",
    "create_account": "pulseline_account_api.SimulationEngine.utils.create_account",
    "update_account": "pulseline_account_api.SimulationEngine.utils.update_account",
    "add_service_to_account": "pulseline_account_api.SimulationEngine.utils.add_service_to_account",
    "add_device_to_account": "pulseline_account_api.SimulationEngine.utils.add_device_to_account",
    "search_accounts_by_phone": "pulseline_account_api.SimulationEngine.utils.search_accounts_by_phone",
    "search_accounts_by_email": "pulseline_account_api.SimulationEngine.utils.search_accounts_by_email",
    # Search engine functions
    "search_plans_by_query": "pulseline_account_api.SimulationEngine.utils.search_plans_by_query",
    "search_account_orders_by_query": "pulseline_account_api.SimulationEngine.utils.search_account_orders_by_query",
    "get_all_available_plans_and_features": "pulseline_account_api.SimulationEngine.utils.get_all_available_plans_and_features",
    # Terminal status functions
    "get_end_of_conversation_status": "pulseline_account_api.SimulationEngine.utils.get_end_of_conversation_status",
}


def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)


def __dir__():
    global _function_map
    return sorted(set(globals().keys()) | set(_function_map.keys()))


__all__ = list(_function_map.keys())
