from langchain_core.prompts import ChatPromptTemplate
from RAG.QdrantProcess import DB_CLIENT
from RAG.LLMs import doc_embeddings_model, llm
from langchain_qdrant import QdrantVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

QA_SYSTEM_PROMPT = """
Bạn là trợ lý cho các nhiệm vụ trả lời câu hỏi. Hãy sử dụng các đoạn ngữ cảnh đã được truy xuất dưới đây để trả lời câu hỏi. Nếu bạn không biết câu trả lời, chỉ cần nói rằng bạn không biết. Hãy giữ câu trả lời ngắn gọn và không quá ba câu.
{context}"""


class Generator:

    @staticmethod
    def search(collection_name: str, query: str) -> str:
        vector_store = QdrantVectorStore(
            client=DB_CLIENT,
            collection_name=collection_name,
            embedding=doc_embeddings_model,
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", QA_SYSTEM_PROMPT),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        retriever = vector_store.as_retriever()
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        ai_msg = rag_chain.invoke({"input": query})
        return ai_msg["answer"]
