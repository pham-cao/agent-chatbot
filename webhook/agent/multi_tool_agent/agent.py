import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.memory import InMemoryMemoryService

APP_NAME = "Student Guide"
SESSION_ID = "30041975"

# Example using a local SQLite file:
db_url = "sqlite:///./session.db"
session_service = DatabaseSessionService(db_url=db_url)

x = session_service.get_session(app_name='mcp_maps_app', user_id='7816816', session_id="hello")

load_dotenv()
memory_service = InMemoryMemoryService()


async def get_tools_async():
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(url="http://0.0.0.0:5000/sse",
                                          headers={"Content-Type": "application/json"})
    )
    print("MCP Toolset created successfully.")
    return tools, exit_stack


async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server."""
    tools, exit_stack = await get_tools_async()
    print(f"Fetched {len(tools)} tools from MCP server.")
    root_agent = LlmAgent(
        model='gemini-2.0-flash',  # Adjust if needed
        name='maps_assistant',
        instruction='Help user with mapping and directions using available tools.',
        tools=tools,
    )
    return root_agent, exit_stack


# --- Step 3: Main Execution Logic (modify query) ---
async def async_main(query, user_id):
    try:
        root_agent, exit_stack = await get_agent_async()
    except* Exception as eg:
        for e in eg.exceptions:
            print(f"Sub-exception occurred: {type(e).__name__}: {e}")

    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service
    )

    content = types.Content(role='user', parts=[types.Part(text=query)])

    session = session_service.get_session(app_name=APP_NAME,
                                          user_id=user_id,
                                          session_id=SESSION_ID)

    if not session:
        session = session_service.create_session(app_name=APP_NAME,
                                                 user_id=user_id,
                                                 session_id=SESSION_ID)

    events_async = runner.run_async(
        session_id=session.id, user_id=session.user_id, new_message=content
    )
    print("Closing MCP server connection...")
    await exit_stack.aclose()
    async for event in events_async:
        if event.is_final_response():
            return event.content.parts[0].text


if __name__ == '__main__':
    try:
        query = input("User Query:")
        asyncio.run(async_main(query))
    except Exception as e:
        print(f"An error occurred: {e}")
