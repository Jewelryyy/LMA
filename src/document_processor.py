import os
import shutil
import re
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from .db_manager import DBManager

class DocumentProcessor:
    def __init__(self, db_manager: DBManager, model_name='all-MiniLM-L6-v2'):
        """
        初始化文献处理器
        """
        self.db = db_manager
        print(f"Loading text embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.docs_root = "docs"

    def extract_text_from_pdf(self, pdf_path):
        """
        从 PDF 提取文本
        """
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def extract_keywords(self, text):
        """
        尝试从文本中提取关键词 (简单的正则匹配)
        """
        # 匹配常见的关键词引导词
        # 匹配模式：Keywords: word1, word2... 直到换行或句号
        patterns = [
            r"(?:Keywords|Key words|Index Terms)\s*[:]\s*(.*?)(?:\n\n|\.|$|\n[A-Z])",
            r"(?:KEYWORDS|KEY WORDS)\s*[:]\s*(.*?)(?:\n\n|\.|$|\n[A-Z])"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                keywords_str = match.group(1)
                # 清理换行符和多余空格
                keywords_str = keywords_str.replace('\n', ' ').strip()
                # 分割
                keywords = [k.strip() for k in re.split(r'[,;]', keywords_str) if k.strip()]
                return keywords
        
        return []

    def process_directory(self, source_dir):
        """
        批量处理目录下的所有 PDF 文件
        """
        if not os.path.exists(source_dir):
            print(f"Error: Directory {source_dir} not found.")
            return

        count = 0
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    print(f"Found PDF: {file_path}")
                    self.process_paper(file_path)
                    count += 1
        print(f"Batch processing complete. Processed {count} files.")

    def process_paper(self, pdf_path, topics_str=None):
        """
        处理单个 PDF：提取文本 -> 生成嵌入 -> 存入 DB -> 移动文件
        """
        if not os.path.exists(pdf_path):
            print(f"Error: File {pdf_path} not found.")
            return

        filename = os.path.basename(pdf_path)
        print(f"Processing {filename}...")

        # 1. 提取文本
        full_text = self.extract_text_from_pdf(pdf_path)
        # 截断文本以适应模型限制 (简单处理，取前500个字符作为摘要用于嵌入，实际可做分块)
        # all-MiniLM-L6-v2 max seq length is 256 tokens. 
        # 这里我们取前 1000 字符作为代表性内容进行嵌入
        text_for_embedding = full_text[:1000]

        # 2. 生成嵌入
        embedding = self.model.encode(text_for_embedding).tolist()

        # 3. 处理 Topics 和文件移动
        if topics_str:
            topics = [t.strip() for t in topics_str.split(',') if t.strip()]
        else:
            # 自动提取
            print("Attempting to extract keywords...")
            topics = self.extract_keywords(full_text[:3000]) # 仅在前3000字符中查找
            if topics:
                print(f"Extracted keywords: {topics}")
                topics_str = ",".join(topics)
            else:
                print("No keywords found. Using 'Uncategorized'.")
                topics = []
                topics_str = ""

        primary_topic = topics[0] if topics else "Uncategorized"
        # 简单的文件名清理，避免非法字符作为文件夹名
        primary_topic = "".join([c for c in primary_topic if c.isalnum() or c in (' ', '_', '-')]).strip()
        if not primary_topic:
            primary_topic = "Uncategorized"
        
        target_dir = os.path.join(self.docs_root, primary_topic)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        target_path = os.path.join(target_dir, filename)
        
        # 移动文件
        try:
            shutil.move(pdf_path, target_path)
            print(f"Moved {filename} to {target_dir}")
        except Exception as e:
            print(f"Error moving file: {e}")
            target_path = pdf_path # 如果移动失败，保持原路径

        # 4. 存入数据库
        metadata = {
            "filename": filename,
            "path": target_path,
            "topics": topics_str,
            "snippet": full_text[:200] # 存储前200字符作为预览
        }
        
        self.db.add_paper(
            doc_id=filename,
            embedding=embedding,
            document_text=text_for_embedding, # 存储用于搜索的文本
            metadata=metadata
        )
        print(f"Successfully indexed {filename}")

    def search(self, query_text, n_results=3):
        """
        搜索文献
        """
        query_embedding = self.model.encode(query_text).tolist()
        results = self.db.search_papers(query_embedding, n_results)
        return results
