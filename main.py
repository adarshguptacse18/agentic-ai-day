from vertexai.preview import reasoning_engines
from vertexai import agent_engines
import vertexai


PROJECT_ID = "steady-habitat-467108-n7"  # Replace with your actual project ID
REGION = "us-central1"  # Replace with your desired region
STAGING_BUCKET = "gs://run-sources-steady-habitat-467108-n7-us-central1"  # Replace with your actual bucket name

vertexai.init(project=PROJECT_ID, location=REGION, staging_bucket=STAGING_BUCKET)
from agentic_ai.agent import root_agent


app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)


remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)

print(remote_app.resource_name)