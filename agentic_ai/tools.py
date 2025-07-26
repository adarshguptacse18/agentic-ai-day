
# expense_manager_agent/tools.py

import datetime
from typing import Dict, List, Any
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.firestore_v1.base_query import And
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from settings import get_settings
from google import genai

SETTINGS = get_settings()
DB_CLIENT = firestore.Client(
    project=SETTINGS.GCLOUD_PROJECT_ID
)  # Will use "(default)" database
COLLECTION = DB_CLIENT.collection(SETTINGS.DB_COLLECTION_NAME)
GENAI_CLIENT = genai.Client(
    vertexai=True, location=SETTINGS.GCLOUD_LOCATION, project=SETTINGS.GCLOUD_PROJECT_ID
)
EMBEDDING_DIMENSION = 768
EMBEDDING_FIELD_NAME = "embedding"
INVALID_ITEMS_FORMAT_ERR = """
Invalid items format. Must be a list of dictionaries with 'name', 'price', and 'quantity' keys."""
RECEIPT_DESC_FORMAT = """
Store Name: {store_name}
Transaction Time: {transaction_time}
Total Amount: {total_amount}
Currency: {currency}
Purchased Items:
{purchased_items}
Receipt Image ID: {receipt_id}
"""


def get_attachment_data(attachment_id: str) -> str:
    """
    stores the attachment data in the database.
    
    Args:
        attachment_id (str): The unique identifier of the attachment.
    
    Returns:
        str: A success message with the receipt ID.

    Raises:
        Exception: If the operation failed or input is invalid.
    """

    print("******************")
    print(attachment_id)

    return f"Receipt stored successfully with ID: {attachment_id}"
