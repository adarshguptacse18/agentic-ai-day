"""Google Wallet pass service for creating and managing generic passes."""

import uuid
from agentic_ai.wallet_pass_service.generic_pass import GenericPass

# Create a demo class instance
# Creates the authenticated HTTP client
generic_pass = GenericPass()


def get_generic_pass_token(title: str, header: str, text_modules: list) -> str:
    """Get a generic pass token for a given title, header, and text modules."""
    object_suffix = str(uuid.uuid4())
    return generic_pass.create_jwt_new_objects(object_suffix=object_suffix, title=title, header=header, text_modules=text_modules)
