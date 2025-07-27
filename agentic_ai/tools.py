
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
import time
import json

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
            "merchantName": "String",
            "purchasedAt": "String", // YYYY-MM-DD HH:MM:SS
            "totalAmount": "Number",
            "currency": "String",
            "taxAmount": "Number",
            "purchaseNumber": "String",
            "paymentMethod": "String",
            "items": [
                {
                    "name": "String",
                    "category": "String",
                    "quantity": "Number",
                    "unitPrice": "Number",
                    "totalPrice": "Number",
                    "isSubscription": "Boolean",
                    "tax": "Number",
                }
            ]
        }
        
        tool_context (ToolContext): The tool context containing user and session information.
    Returns:
        str: A success message with the document ID.

    Raises:
        Exception: If the operation failed or input is invalid.
    """
    start_time = time.time()
    try:
        # Validate JSON structure
        if not isinstance(json_data, dict):
            raise ValueError("json_data must be a dictionary")

        user_id = tool_context._invocation_context.user_id
        COLLECTION.add({"user_id": user_id, "data": json_data})
        end_time = time.time()
        print(f"TIME TAKEN TO SAVE DOCUMENT: {end_time - start_time} seconds")
        return json_data
    except Exception as e:
        end_time = time.time()
        print(f"TIME TAKEN TO SAVE DOCUMENT (---ERROR---): {end_time - start_time} seconds")
        raise Exception(f"Failed to store document: {str(e)}")



def get_all_purchases_for_a_user(
    tool_context: ToolContext,
) -> str:
    """
    This function returns all the purchases and its details for a user.
    Purchases contains transaction data and individual items purchased.

    Args:
        tool_context (ToolContext): The tool context containing user and session information.

    Returns:
        JSON string with following structure (List[Dict[str, Any]]): A list of dictionaries containing document information, where each dictionary has the following structure:
            {
            "merchantName": "String",
            "purchasedAt": "String", // YYYY-MM-DD HH:MM:SS
            "totalAmount": "Number",
            "currency": "String",
            "taxAmount": "Number",
            "purchaseNumber": "String",
            "paymentMethod": "String",
            "items": [
                {
                    "name": "String",
                    "category": "String"
                    "quantity": "Number",
                    "unitPrice": "Number",
                    "totalPrice": "Number",
                    "isSubscription": "Boolean",
                    "tax": "Number",
                }
            ]
        }
    Raises:
        Exception: If the search failed or input is invalid.
    """
    start_time = time.time()
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
        end_time = time.time()
        print(f"TIME TAKEN TO GET ALL PURCHASES FOR A USER: {end_time - start_time} seconds")
        
        # stringify the final_results
        return json.dumps(final_results)
    except Exception as e:
        end_time = time.time()
        print(f"TIME TAKEN TO GET ALL PURCHASES FOR A USER (---ERROR---): {end_time - start_time} seconds")
        raise Exception(f"Error filtering receipts: {str(e)}")



# def save_all_the_demo_transactions(
#     tool_context: ToolContext,
# ) -> str:
#     """
#     This function saves all the demo transactions to the database.
#     """
#     import json
#     try:
#         with open("agentic_ai/datasetv2.json", "r") as file:
#             data = json.load(file)
#             for item in data:
#                 COLLECTION.add({"user_id": tool_context._invocation_context.user_id, "data": item})
#         return "All the demo transactions have been saved to the database."
#     except Exception as e:
#         print('got error in save all the demo transactions ------------')
#         raise Exception(f"Error saving demo transactions: {str(e)}")