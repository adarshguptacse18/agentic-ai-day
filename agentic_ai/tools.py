
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



def save_attachment_data(
    json_data: Dict[str, Any],
    tool_context: ToolContext,
) -> str:
    """
    Store document data in the database from JSON format.

    Args:
        json_data (Dict[str, Any]): JSON data containing document information with the following structure:
            {
                "documentType": "String", // "Receipt", "Product", "Warranty", "Other"
                "isPartialReceipt": "Boolean", // Only for "Receipt"
                "extractedData": {
                    "receiptDetails": {
                        "merchantName": "String",
                        "purchaseDate": "String", // YYYY-MM-DD
                        "purchaseTime": "String", // HH:MM:SS
                        "totalAmount": "Number",
                        "currency": "String",
                        "taxAmount": "Number",
                        "discountAmount": "Number",
                        "paymentMethod": "String",
                        "receiptNumber": "String",
                        "items": [
                            {
                                "name": "String",
                                "quantity": "Number",
                                "unitPrice": "Number",
                                "lineTotal": "Number",
                                "category": "String"
                            }
                        ]
                    },
                    "productDetails": { ... },
                    "warrantyDetails": { ... }
                }
            }

    Returns:
        str: A success message with the document ID.

    Raises:
        Exception: If the operation failed or input is invalid.
    """
    try:
        # Validate JSON structure
        if not isinstance(json_data, dict):
            raise ValueError("json_data must be a dictionary")

        if "documentType" not in json_data:
            raise ValueError("documentType is required in json_data")

        if "extractedData" not in json_data:
            raise ValueError("extractedData is required in json_data")

        COLLECTION.add({"user_id": user_id, "data": json_data})

        return json_data
    except Exception as e:
        raise Exception(f"Failed to store document: {str(e)}")



# TODO: This needs to be implemented properly. Please update this to get all via user id 
def get_all_receipts_data_for_a_user(
) -> str:
    """
    Filter receipts by metadata within a specific time range and optionally by amount.

    Args:
        start_time (str): The start datetime for the filter (in ISO format, e.g. 'YYYY-MM-DDTHH:MM:SS.ssssssZ').
        end_time (str): The end datetime for the filter (in ISO format, e.g. 'YYYY-MM-DDTHH:MM:SS.ssssssZ').
        min_total_amount (float): The minimum total amount for the filter (inclusive). Defaults to -1.
        max_total_amount (float): The maximum total amount for the filter (inclusive). Defaults to -1.

    Returns:
        str: A string containing the list of receipt data matching all applied filters.

    Raises:
        Exception: If the search failed or input is invalid.
    """
    try:
        # Validate start and end times
        if not isinstance(start_time, str) or not isinstance(end_time, str):
            raise ValueError("start_time and end_time must be strings in ISO format")
        try:
            datetime.datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            datetime.datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("start_time and end_time must be strings in ISO format")

        # Start with the base collection reference
        query = COLLECTION

        # Build the composite query by properly chaining conditions
        # Notes that this demo assume 1 user only,
        # need to refactor the query for multiple user
        filters = [
            FieldFilter("transaction_time", ">=", start_time),
            FieldFilter("transaction_time", "<=", end_time),
        ]

        # Add optional filters
        if min_total_amount != -1:
            filters.append(FieldFilter("total_amount", ">=", min_total_amount))

        if max_total_amount != -1:
            filters.append(FieldFilter("total_amount", "<=", max_total_amount))

        # Apply the filters
        composite_filter = And(filters=filters)
        query = query.where(filter=composite_filter)

        # Execute the query and collect results
        search_result_description = "Search by Metadata Results:\n"
        for doc in query.stream():
            data = doc.to_dict()
            data.pop(
                EMBEDDING_FIELD_NAME, None
            )  # Remove embedding as it's not needed for display

            search_result_description += f"\n{RECEIPT_DESC_FORMAT.format(**data)}"

        return search_result_description
    except Exception as e:
        raise Exception(f"Error filtering receipts: {str(e)}")


# def generate_insights: calls above function and then passes it to llm. 