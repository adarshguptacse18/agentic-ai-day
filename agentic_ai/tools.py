
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
from google.adk.tools import ToolContext

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
        tool_context (ToolContext): The tool context containing user and session information.
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
        
        user_id = tool_context._invocation_context.user_id
        COLLECTION.add({"user_id": user_id, "data": json_data})

        return json_data
    except Exception as e:
        raise Exception(f"Failed to store document: {str(e)}")



# TODO: This needs to be implemented properly. Please update this to get all via user id 
def get_all_data_for_a_user(
    tool_context: ToolContext,
) -> str:
    """
    This function extracts all the transactions for a user 

    Args:
        tool_context (ToolContext): The tool context containing user and session information.

    Returns:
        json_data (List[Dict[str, Any]]): A list of dictionaries containing document information, where each dictionary has the following structure:
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
    Raises:
        Exception: If the search failed or input is invalid.
    """
    try:
        # Start with the base collection reference
        query = COLLECTION
        user_id = tool_context._invocation_context.user_id

        # Build the composite query by properly chaining conditions
        # Notes that this demo assume 1 user only,
        # need to refactor the query for multiple user
        filters = [
            FieldFilter("user_id", "==", user_id),
        ]


        # Apply the filters
        composite_filter = And(filters=filters)
        query = query.where(filter=composite_filter)

        # Execute the query and collect results
        final_results = []
        for doc in query.stream():
            data = doc.to_dict()
            final_results.append(data["data"])
        return final_results
    except Exception as e:
        raise Exception(f"Error filtering receipts: {str(e)}")

