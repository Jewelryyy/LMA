import chromadb
from chromadb.config import Settings
import os

class DBManager:
    def __init__(self, persist_directory="embeddings"):
        """
        初始化 ChromaDB 客户端
        """
        # 确保持久化目录存在
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 获取或创建集合
        self.paper_collection = self.client.get_or_create_collection(
            name="papers",
            metadata={"hnsw:space": "cosine"} # 使用余弦相似度
        )
        
        self.image_collection = self.client.get_or_create_collection(
            name="images",
            metadata={"hnsw:space": "cosine"}
        )

    def add_paper(self, doc_id, embedding, document_text, metadata):
        """
        添加文献嵌入到数据库
        """
        self.paper_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[document_text],
            metadatas=[metadata]
        )

    def search_papers(self, query_embedding, n_results=5):
        """
        搜索文献
        """
        results = self.paper_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    def add_image(self, img_id, embedding, metadata):
        """
        添加图像嵌入到数据库
        """
        self.image_collection.add(
            ids=[img_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search_images(self, query_embedding, n_results=5):
        """
        搜索图像
        """
        results = self.image_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
