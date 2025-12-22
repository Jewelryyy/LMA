import os
from PIL import Image
from sentence_transformers import SentenceTransformer
from .db_manager import DBManager

class ImageProcessor:
    def __init__(self, db_manager: DBManager, model_name='clip-ViT-B-32'):
        """
        初始化图像处理器
        """
        self.db = db_manager
        print(f"Loading CLIP model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.images_root = "images"

    def process_image(self, image_path):
        """
        处理单个图像：加载 -> 生成嵌入 -> 存入 DB
        """
        if not os.path.exists(image_path):
            print(f"Error: File {image_path} not found.")
            return

        filename = os.path.basename(image_path)
        
        # 1. 加载图像
        try:
            img = Image.open(image_path)
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            return

        # 2. 生成嵌入
        embedding = self.model.encode(img).tolist()

        # 3. 存入数据库
        # 假设图像已经存在于 images 目录下，或者我们这里不移动，只索引
        # 如果需要移动，逻辑同 DocumentProcessor
        
        metadata = {
            "filename": filename,
            "path": image_path
        }
        
        self.db.add_image(
            img_id=filename,
            embedding=embedding,
            metadata=metadata
        )
        print(f"Successfully indexed image {filename}")

    def process_directory(self, source_dir):
        """
        批量处理目录下的所有图像文件
        """
        if not os.path.exists(source_dir):
            print(f"Error: Directory {source_dir} not found.")
            return

        count = 0
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if os.path.splitext(file)[1].lower() in valid_extensions:
                    file_path = os.path.join(root, file)
                    print(f"Found Image: {file_path}")
                    self.process_image(file_path)
                    count += 1
        print(f"Batch processing complete. Processed {count} images.")

    def search_by_text(self, query_text, n_results=3):
        """
        以文搜图
        """
        # CLIP 模型可以将文本映射到与图像相同的向量空间
        query_embedding = self.model.encode(query_text).tolist()
        results = self.db.search_images(query_embedding, n_results)
        return results
