from mcp import ClientSession
from mcp.client.sse import sse_client


async def check():
    async with sse_client("http://0.0.0.0:8000/sse") as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()

            # List avail tool
            tools = await session.list_tools()

            print(tools)

            # Call add tool
            result = await session.call_tool("get_all_collections")
            print(result)

            result = await session.call_tool("search",
                                             arguments={"collection_name": "Tài Liệu Giải Pháp Phân Quyền Câu Hỏi.docx",
                                                        "question": "giải pháp là gì"})
            print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(check())
