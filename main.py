import argparse
import os
import sys
from src.db_manager import DBManager
from src.document_processor import DocumentProcessor
from src.image_processor import ImageProcessor

def main():
    parser = argparse.ArgumentParser(description="Local Multimodal AI Agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: add_paper
    parser_add = subparsers.add_parser("add_paper", help="Add a PDF paper to the library")
    parser_add.add_argument("path", type=str, help="Path to the PDF file")
    parser_add.add_argument("--topics", type=str, default="", help="Comma-separated topics (e.g., 'CV,NLP'). If empty, will try to extract from text.")

    # Command: batch_add_paper
    parser_batch_add = subparsers.add_parser("batch_add_paper", help="Batch add PDF papers from a directory")
    parser_batch_add.add_argument("dir_path", type=str, help="Path to the directory containing PDF files")

    # Command: search_paper
    parser_search_paper = subparsers.add_parser("search_paper", help="Search for papers using natural language")
    parser_search_paper.add_argument("query", type=str, help="Search query")

    # Command: search_image
    parser_search_image = subparsers.add_parser("search_image", help="Search for images using natural language description")
    parser_search_image.add_argument("query", type=str, help="Image description")
    
    # Command: index_image (Helper to add images for testing)
    parser_index_image = subparsers.add_parser("index_image", help="Index an image file")
    parser_index_image.add_argument("path", type=str, help="Path to the image file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize components
    # 注意：这里每次运行都会加载模型，实际生产中可能需要常驻服务
    try:
        db = DBManager()
    except Exception as e:
        print(f"Failed to initialize DB: {e}")
        return

    if args.command == "add_paper":
        processor = DocumentProcessor(db)
        processor.process_paper(args.path, args.topics)

    elif args.command == "batch_add_paper":
        processor = DocumentProcessor(db)
        processor.process_directory(args.dir_path)

    elif args.command == "search_paper":
        processor = DocumentProcessor(db)
        results = processor.search(args.query)
        print("\n--- Search Results ---")
        if results['ids']:
            for i, doc_id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i]
                dist = results['distances'][0][i]
                print(f"[{i+1}] {meta.get('filename')} (Score: {dist:.4f})")
                print(f"    Path: {meta.get('path')}")
                print(f"    Topics: {meta.get('topics')}")
                print(f"    Snippet: {meta.get('snippet')}...\n")
        else:
            print("No results found.")

    elif args.command == "search_image":
        processor = ImageProcessor(db)
        results = processor.search_by_text(args.query)
        print("\n--- Image Search Results ---")
        if results['ids']:
            for i, img_id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i]
                dist = results['distances'][0][i]
                print(f"[{i+1}] {meta.get('filename')} (Score: {dist:.4f})")
                print(f"    Path: {meta.get('path')}\n")
        else:
            print("No results found.")
            
    elif args.command == "index_image":
        processor = ImageProcessor(db)
        processor.process_image(args.path)

if __name__ == "__main__":
    main()
