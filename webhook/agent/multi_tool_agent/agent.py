from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv

load_dotenv()  # take environment variables

# Define a tool function
def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    # Replace with actual logic (e.g., API call, database lookup)
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")


# Add the tool to the agent
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Trả lời các câu hỏi của người dùng về thủ đô của một quốc gia nhất định.",
    instruction="""Bạn là một tác nhân cung cấp thủ đô của một quốc gia... (văn bản hướng dẫn trước)""",
    tools=[get_capital_city]  # Provide the function directly
)