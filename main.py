import argparse
import os
import sys
from src.db_manager import DBManager
from src.document_processor import DocumentProcessor
from src.image_processor import ImageProcessor

def print_paper_results(results):
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

def print_image_results(results):
    print("\n--- Image Search Results ---")
    if results['ids']:
        for i, img_id in enumerate(results['ids'][0]):
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i]
            print(f"[{i+1}] {meta.get('filename')} (Score: {dist:.4f})")
            print(f"    Path: {meta.get('path')}\n")
    else:
        print("No results found.")

def get_doc_processor(db, processor_instance):
    if processor_instance is None:
        print("\nInitializing Document Processor (loading models)...")
        return DocumentProcessor(db)
    return processor_instance

def get_img_processor(db, processor_instance):
    if processor_instance is None:
        print("\nInitializing Image Processor (loading models)...")
        return ImageProcessor(db)
    return processor_instance

def run_interactive_mode(db):
    doc_processor = None
    img_processor = None

    while True:
        print("\n==========================================")
        print("      Local Multimodal AI Agent           ")
        print("==========================================")
        print("1. Add Paper (Single File)")
        print("2. Add Paper (Batch Directory)")
        print("3. Search Paper")
        print("4. Index Image (Single File)")
        print("5. Index Image (Batch Directory)")
        print("6. Search Image")
        print("0. Exit")
        print("==========================================")
        
        choice = input("Select an option [0-6]: ").strip()

        if choice == '0':
            print("Exiting...")
            break

        elif choice == '1':
            path = input("Enter PDF path: ").strip()
            # Remove quotes if user dragged and dropped file
            path = path.strip('"').strip("'")
            topics = input("Enter topics (comma-separated, optional): ").strip()
            
            doc_processor = get_doc_processor(db, doc_processor)
            doc_processor.process_paper(path, topics)

        elif choice == '2':
            path = input("Enter directory path: ").strip()
            path = path.strip('"').strip("'")
            
            doc_processor = get_doc_processor(db, doc_processor)
            doc_processor.process_directory(path)

        elif choice == '3':
            query = input("Enter search query: ").strip()
            if query:
                doc_processor = get_doc_processor(db, doc_processor)
                results = doc_processor.search(query)
                print_paper_results(results)

        elif choice == '4':
            path = input("Enter image path: ").strip()
            path = path.strip('"').strip("'")
            
            img_processor = get_img_processor(db, img_processor)
            img_processor.process_image(path)

        elif choice == '5':
            path = input("Enter directory path: ").strip()
            path = path.strip('"').strip("'")
            
            img_processor = get_img_processor(db, img_processor)
            img_processor.process_directory(path)

        elif choice == '6':
            query = input("Enter image description: ").strip()
            if query:
                img_processor = get_img_processor(db, img_processor)
                results = img_processor.search_by_text(query)
                print_image_results(results)

        else:
            print("Invalid option, please try again.")

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

    # Command: batch_index_image
    parser_batch_index_image = subparsers.add_parser("batch_index_image", help="Batch index images from a directory")
    parser_batch_index_image.add_argument("dir_path", type=str, help="Path to the directory containing image files")

    args = parser.parse_args()

    # Initialize DB
    try:
        db = DBManager()
    except Exception as e:
        print(f"Failed to initialize DB: {e}")
        return

    if not args.command:
        # No arguments provided, enter interactive mode
        run_interactive_mode(db)
        return

    # CLI Mode Execution
    if args.command == "add_paper":
        processor = DocumentProcessor(db)
        processor.process_paper(args.path, args.topics)

    elif args.command == "batch_add_paper":
        processor = DocumentProcessor(db)
        processor.process_directory(args.dir_path)

    elif args.command == "search_paper":
        processor = DocumentProcessor(db)
        results = processor.search(args.query)
        print_paper_results(results)

    elif args.command == "search_image":
        processor = ImageProcessor(db)
        results = processor.search_by_text(args.query)
        print_image_results(results)
            
    elif args.command == "index_image":
        processor = ImageProcessor(db)
        processor.process_image(args.path)

    elif args.command == "batch_index_image":
        processor = ImageProcessor(db)
        processor.process_directory(args.dir_path)

if __name__ == "__main__":
    main()
