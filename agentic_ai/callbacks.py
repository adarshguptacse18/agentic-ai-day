# expense_manager_agent/callbacks.py

import hashlib
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest


def modify_image_data_in_history(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    # The following code will modify the request sent to LLM
    # We will only keep image / video data in the last 3 user messages using a reverse and counter approach

    # Count how many user messages we've processed
    user_message_count = 0

    # Process the reversed list
    for content in reversed(llm_request.contents):
        # Only count for user manual query, not function call
        if (content.role == 'model'):
            print("Model output")
            print(content.parts)
        if (content.role == "user") and (content.parts[0].function_response is None):
            user_message_count += 1
            modified_content_parts = []

            # Check any missing image ID placeholder for any image data
            # Then remove image data from conversation history if more than 3 user messages
            for idx, part in enumerate(content.parts):
                if part.inline_data is None:
                    modified_content_parts.append(part)
                    continue
                # Check if it's an image or video based on MIME type
                mime_type = part.inline_data.mime_type
                is_image = mime_type.startswith('image/')
                is_video = mime_type.startswith('video/')
                
                print(f"Attachment is of type ${mime_type}")
                if not (is_image or is_video):
                    modified_content_parts.append(part)
                    continue

                placeholder_prefix = f"[ATTACHMENT-ID "
                if user_message_count <= 3:
                    modified_content_parts.append(part)

            # This will modify the contents inside the llm_request
            content.parts = modified_content_parts
