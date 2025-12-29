import gradio as gr
import os
import shutil
from src.db_manager import DBManager
from src.document_processor import DocumentProcessor
from src.image_processor import ImageProcessor
from PIL import Image

# Initialize System
# Note: Models will be loaded on startup
print("Initializing system components...")
try:
    db = DBManager()
    doc_processor = DocumentProcessor(db)
    img_processor = ImageProcessor(db)
    print("System initialized successfully.")
except Exception as e:
    print(f"Error initializing system: {e}")
    db = None
    doc_processor = None
    img_processor = None

def format_paper_results(results):
    if not results['ids']:
        return "No results found."
    
    output = ""
    for i, doc_id in enumerate(results['ids'][0]):
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        output += f"### {i+1}. {meta.get('filename')}\n"
        output += f"**Score:** {dist:.4f}  \n"
        output += f"**Path:** `{meta.get('path')}`  \n"
        output += f"**Topics:** {meta.get('topics')}  \n"
        output += f"**Snippet:** {meta.get('snippet')}...\n\n"
        output += "---\n"
    return output

def format_image_results(results):
    if not results['ids']:
        return []
    
    images = []
    for i, img_id in enumerate(results['ids'][0]):
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        path = meta.get('path')
        caption = f"{meta.get('filename')} (Score: {dist:.4f})"
        if os.path.exists(path):
            images.append((path, caption))
    return images

# --- Callbacks ---

def add_paper(file, topics):
    if not doc_processor:
        return "System not initialized."
    if file is None:
        return "Please upload a file."
    
    try:
        # Gradio passes a file path for the uploaded file
        # process_paper will move it, so we should copy it first if we want to keep the temp? 
        # Actually process_paper moves the file provided at 'path'. 
        # Gradio temp files are meant to be processed. Moving them is fine.
        doc_processor.process_paper(file, topics)
        return f"Successfully processed and archived paper."
    except Exception as e:
        return f"Error: {str(e)}"

def batch_add_paper(dir_path):
    if not doc_processor:
        return "System not initialized."
    if not os.path.exists(dir_path):
        return "Directory not found."
    
    try:
        # Capture stdout to show progress? Difficult in Gradio. Just run it.
        doc_processor.process_directory(dir_path)
        return f"Batch processing for {dir_path} completed. Check console for details."
    except Exception as e:
        return f"Error: {str(e)}"

def search_paper(query):
    if not doc_processor:
        return "System not initialized."
    if not query:
        return "Please enter a query."
    
    results = doc_processor.search(query)
    return format_paper_results(results)

def index_image_upload(file):
    if not img_processor:
        return "System not initialized."
    if file is None:
        return "Please upload an image."
    
    try:
        # Save to images/ directory to make it persistent
        filename = os.path.basename(file)
        # Ensure images directory exists
        if not os.path.exists("images"):
            os.makedirs("images")
            
        target_path = os.path.join("images", filename)
        # Handle duplicate names
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join("images", f"{base}_{counter}{ext}")
            counter += 1
            
        shutil.copy(file, target_path)
        img_processor.process_image(target_path)
        return f"Saved and indexed image at {target_path}"
    except Exception as e:
        return f"Error: {str(e)}"

def batch_index_image(dir_path):
    if not img_processor:
        return "System not initialized."
    if not os.path.exists(dir_path):
        return "Directory not found."
    
    try:
        img_processor.process_directory(dir_path)
        return f"Batch indexing for {dir_path} completed."
    except Exception as e:
        return f"Error: {str(e)}"

def search_image(query):
    if not img_processor:
        return []
    if not query:
        return []
    
    results = img_processor.search_by_text(query)
    return format_image_results(results)

# --- UI Layout ---

with gr.Blocks(title="Local Multimodal AI Agent") as demo:
    gr.Markdown("# 🤖 Local Multimodal AI Agent")
    
    with gr.Tabs():
        # Tab 1: Papers
        with gr.TabItem("📄 Papers"):
            with gr.Tabs():
                with gr.TabItem("Search"):
                    with gr.Row():
                        paper_query = gr.Textbox(label="Search Query", placeholder="e.g., natural language processing models")
                        paper_search_btn = gr.Button("Search", variant="primary")
                    paper_results = gr.Markdown(label="Results")
                    paper_search_btn.click(search_paper, inputs=paper_query, outputs=paper_results)
                
                with gr.TabItem("Add Single Paper"):
                    paper_file = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
                    paper_topics = gr.Textbox(label="Topics (Optional)", placeholder="e.g., CV, NLP (Leave empty for auto-detection)")
                    paper_add_btn = gr.Button("Add Paper")
                    paper_status = gr.Textbox(label="Status", interactive=False)
                    paper_add_btn.click(add_paper, inputs=[paper_file, paper_topics], outputs=paper_status)
                    
                with gr.TabItem("Batch Add Papers"):
                    paper_dir = gr.Textbox(label="Directory Path", placeholder="Absolute path to folder containing PDFs")
                    paper_batch_btn = gr.Button("Process Directory")
                    paper_batch_status = gr.Textbox(label="Status", interactive=False)
                    paper_batch_btn.click(batch_add_paper, inputs=paper_dir, outputs=paper_batch_status)

        # Tab 2: Images
        with gr.TabItem("🖼️ Images"):
            with gr.Tabs():
                with gr.TabItem("Search"):
                    with gr.Row():
                        image_query = gr.Textbox(label="Image Description", placeholder="e.g., a cute cat sleeping")
                        image_search_btn = gr.Button("Search", variant="primary")
                    image_results = gr.Gallery(label="Results", columns=3, height="auto")
                    image_search_btn.click(search_image, inputs=image_query, outputs=image_results)
                
                with gr.TabItem("Index Single Image"):
                    image_file = gr.Image(label="Upload Image", type="filepath")
                    image_add_btn = gr.Button("Index Image")
                    image_status = gr.Textbox(label="Status", interactive=False)
                    image_add_btn.click(index_image_upload, inputs=image_file, outputs=image_status)
                    
                with gr.TabItem("Batch Index Images"):
                    image_dir = gr.Textbox(label="Directory Path", placeholder="Absolute path to folder containing images")
                    image_batch_btn = gr.Button("Index Directory")
                    image_batch_status = gr.Textbox(label="Status", interactive=False)
                    image_batch_btn.click(batch_index_image, inputs=image_dir, outputs=image_batch_status)

if __name__ == "__main__":
    demo.launch()
