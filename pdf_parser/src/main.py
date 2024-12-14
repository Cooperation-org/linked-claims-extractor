import argparse
from pathlib import Path
import sys
from pdf_parser import DocumentManager
from pdf_parser import DocumentREPL

def main():
    parser = argparse.ArgumentParser(description='Process and query PDF documents')
    parser.add_argument('--pdf', type=str, default="example.pdf",
                       help='Path to PDF file')
    parser.add_argument('--reset', action='store_true',
                       help='Reset ChromaDB collection before processing')
    args = parser.parse_args()
    
    pdf_path = args.pdf
    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Initialize document manager
    doc_manager = DocumentManager()
    
    # Process PDF
    doc_manager.process_pdf(pdf_path, reset=args.reset)
    
    # Start REPL
    repl = DocumentREPL(doc_manager=doc_manager)
    repl.cmdloop()

if __name__ == "__main__":
    main()
