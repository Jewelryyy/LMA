<h1>Local Multimodal AI Agent</h1>

这是一个基于本地轻量级模型的智能多模态助手项目。它利用 `SentenceTransformers`、`CLIP` 和 `ChromaDB` 实现了智能文献管理和以文搜图功能，所有数据和模型均在本地运行，保护隐私且无需联网。

## ✨ 功能特性

### 1. 智能文献管理 📄
*   **语义搜索**：支持使用自然语言（如“自然语言处理模型”）搜索 PDF 文献，而非仅限于关键词匹配。
*   **自动分类**：自动提取 PDF 中的关键词（Keywords/Index Terms），并根据提取的主题将文件自动归档到 `docs/<Topic>/` 目录下。
*   **批量整理**：支持一键扫描并整理整个文件夹下的 PDF 文献。

### 2. 智能图像管理 🖼️
*   **以文搜图**：支持通过自然语言描述（如“一只在睡觉的猫”）检索本地图片库。
*   **语义索引**：利用 CLIP 模型理解图像内容。

## 🛠️ 安装指南

### 前置要求
*   Python 3.8+
*   建议使用虚拟环境 (venv 或 conda)

### 安装步骤

1.  **克隆或下载本项目**

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```
    *注意：首次运行时，`sentence-transformers` 会自动下载所需的 AI 模型（`all-MiniLM-L6-v2` 和 `clip-ViT-B-32`），请保持网络连接或提前准备好缓存。*

## 🚀 快速开始

项目通过 `main.py` 提供统一的命令行接口。

### 😊 交互式模式 (推荐)

直接运行 `main.py` 即可进入交互式菜单，支持持久化运行，避免重复加载模型。

```bash
python main.py
```

### 🌐 Web 界面 (Gradio)

如果您更喜欢图形化界面，可以启动 Gradio Web App：

```bash
python gradio_app.py
```
启动后，在浏览器访问终端显示的 URL（通常是 `http://127.0.0.1:7860`）。

### 📚 文献管理 (命令行模式)

#### 1. 添加单个文献
将 PDF 添加到库中。你可以手动指定主题，也可以让系统自动提取。

*   **自动提取主题（推荐）**：
    ```bash
    python main.py add_paper "path/to/paper.pdf"
    ```
    *系统会尝试从文中提取关键词，并将文件移动到 `docs/<Keyword>/`。如果提取失败，将放入 `docs/Uncategorized/`。*

*   **手动指定主题**：
    ```bash
    python main.py add_paper "path/to/paper.pdf" --topics "CV,Transformer"
    ```

#### 2. 批量添加文献
扫描指定目录下的所有 PDF 文件，自动提取关键词并整理归档。

```bash
python main.py batch_add_paper "C:/Downloads/Papers/"
```

#### 3. 搜索文献
使用自然语言提问来查找相关论文。

```bash
python main.py search_paper "how to train large language models"
```

### 🖼️ 图像管理

#### 1. 索引图像
将图片添加到搜索库中（目前仅建立索引，不移动原文件）。

```bash
python main.py index_image "path/to/photo.jpg"
```

#### 2. 批量索引图像
扫描指定目录下的所有图片文件（支持 jpg, png, bmp, gif, webp），建立索引。

```bash
python main.py batch_index_image "path/to/images_folder/"
```

#### 3. 以文搜图
用文字描述来搜索图片。

```bash
python main.py search_image "a dog playing in the park"
```

## 📂 项目结构

```text
LMA/
├── docs/                 # [自动生成] 归档后的 PDF 文献库（按主题分类）
├── images/               # 图片库目录
├── embeddings/           # [自动生成] ChromaDB 向量数据库文件
├── src/                  # 源代码目录
│   ├── db_manager.py         # 数据库管理
│   ├── document_processor.py # 文献处理与自动分类逻辑
│   └── image_processor.py    # 图像处理与 CLIP 模型逻辑
├── main.py               # 程序入口
└── requirements.txt      # 项目依赖
```

## 📝 注意事项

*   **模型加载**：每次运行命令时都会加载 AI 模型，这可能会导致几秒钟的启动延迟。在生产环境中，建议将其改为常驻服务。
*   **PDF 解析**：目前仅支持提取文本层。对于扫描版（图片型）PDF，自动关键词提取可能无法工作。
*   **数据持久化**：所有的索引数据存储在 `embeddings/` 目录下，请勿随意删除该目录，否则需要重新索引所有文件。
