from mcp.server.fastmcp import FastMCP
from rag.QdrantProcess import ProcessVectorDB
from rag.Generator import Generator

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

@mcp.tool()
def collect_user_info(name:str,phone:str,location:str,interest:str) -> str:
    "hàm lưu thông tin người cần liên hệ  để bộ phận tư vấn có thể liên hệ lại"
    print("Chào bạn! Mình sẽ hỗ trợ bạn kết nối với bộ phận tư vấn. Trước tiên, cho mình xin vài thông tin nhé 😊")

    user_info = {
        "Họ tên": name.strip(),
        "Số điện thoại": phone.strip(),
        "Khu vực": location.strip(),
        "Ngành học quan tâm": interest.strip()
    }

    print("\nCảm ơn bạn! Bộ phận tư vấn sẽ sớm liên hệ với bạn qua số điện thoại đã cung cấp.")
    return user_info


if __name__ == "__main__":
    print("Listening...")
    mcp.run(transport="sse")
