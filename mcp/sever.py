from mcp.server.fastmcp import FastMCP
from RAG.QdrantProcess import ProcessVectorDB
from RAG.Generator import Generator

db = ProcessVectorDB()
mcp = FastMCP(name="mcp-sever")


@mcp.tool()
def get_all_collections() -> int:
    """ lấy thông tin tên các tài liệu  tất cả  được lưu trữ """
    return db.get_collections()


@mcp.tool()
def search(collection_name: str, question: str) -> str:
    """ Tìm kiếm thông tin trong tài liệu"""
    return Generator.search(collection_name, question)


if __name__ == "__main__":
    print("Listening...")
    mcp.run(transport="sse")
