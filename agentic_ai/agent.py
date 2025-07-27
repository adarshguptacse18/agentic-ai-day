# agentic_ai/agent.py

from google.adk.agents import Agent
from agentic_ai.tools import save_attachment_data, get_all_purchases_for_a_user
from agentic_ai.callbacks import modify_image_data_in_history
import os
from settings import get_settings
from google.adk.planners import BuiltInPlanner
from google.genai import types

SETTINGS = get_settings()
os.environ["GOOGLE_CLOUD_PROJECT"] = SETTINGS.GCLOUD_PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = SETTINGS.GCLOUD_LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

# Get the code file directory path and read the task prompt file
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_path = os.path.join(current_dir, "task_prompt.md")
with open(prompt_path, "r") as file:
    task_prompt = file.read()

root_agent = Agent(
    name="expense_manager_agent",
    model="gemini-2.5-flash",
    description=(
        "Personal expense agent to help user track expenses, analyze receipts and purchases, and manage their financial records"
    ),
    instruction=task_prompt,
    tools=[save_attachment_data, get_all_purchases_for_a_user],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=24576,
        )
    ),
    before_model_callback=modify_image_data_in_history,
)
