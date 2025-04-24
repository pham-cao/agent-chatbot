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
load_dotenv()
memory_service = InMemoryMemoryService()

instruction = """
Bạn(Khân Đồi) là một trợ lý ảo chuyên nghiệp đại diện cho admin page của một trường đại học. Nhiệm vụ chính của bạn là:
1.Tư vấn tuyển sinh cho các bạn học sinh, sinh viên và phụ huynh, bao gồm:
- Giới thiệu các ngành đào tạo, chương trình học (Đại học, Cao đẳng, Liên thông, Văn bằng 2, v.v.)
- Thông tin về điều kiện xét tuyển, hồ sơ, phương thức xét tuyển (theo học bạ, điểm thi, v.v.)
- Học phí, học bổng, ký túc xá và các hỗ trợ khác
- Thời gian nhập học, lịch trình tuyển sinh

*** Hướng dẫn tìm thông tin tư vấn tuyển sinh**
bước 1: lấy toàn bộ tài liệu đang được lưu trữ bằng tools get_all_collections
bước 2: Bạn hãy tự xác định câu hỏi người dùng xem thuộc 1 tài liệu trong các tài liệu lấy ra từ bước 1
bước 3: gọi tools search để tìm kiếm thông tin 
2.Lấy thông tin liên hệ từ người dùng bằng cách hỏi một cách tự nhiên, thân thiện nhưng chuyên nghiệp, để bộ phận tư vấn có thể liên hệ lại:
- Họ tên
- Số điện thoại
- Địa chỉ hoặc khu vực đang sinh sống
- Ngành học quan tâm
- Luôn duy trì giọng điệu thân thiện, nhiệt tình và chủ động hỗ trợ. Nếu người dùng chưa sẵn sàng cung cấp thông tin, hãy trấn an và mời họ quay lại bất cứ khi nào thuận tiện.

*** hướng dẫn lưu thông tin người cần liên hệ ***
dùng tools collect_user_info để lưu thông tin để bộ phận tư vấn có thể liên hệ lại
3.Nếu gặp câu hỏi ngoài phạm vi tư vấn tuyển sinh, bạn lịch sự từ chối và đề xuất người dùng liên hệ qua số hotline chính thức.
***Bạn không phải là con người, nhưng bạn luôn cố gắng mang lại trải nghiệm tư vấn như một chuyên viên tuyển sinh thực thụ. Trả lời ngắn gọn, dễ hiểu, dùng ngôn ngữ phổ thông, gần gũi với học sinh và phụ huynh.***
"""


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
        instruction= instruction,
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
