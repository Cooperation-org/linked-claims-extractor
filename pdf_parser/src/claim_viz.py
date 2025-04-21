import sys
from pathlib import Path
from claim_extractor import ClaimExtractor
import time
from dotenv import load_dotenv

load_dotenv()

MAX_CHUNKS = 20


def process_and_visualize_claims(docmgr, output_file: str = "claims_analysis.html"):
    """Process all chunks and create visualization, grouping by page"""

    # Get all chunks from ChromaDB in order
    print("Getting chunks from ChromaDB...")
    results = docmgr.text_collection.get()
    print(f"Results keys: {results.keys()}")
    print(f"Number of documents: {len(results['documents'])}")
    if len(results['documents']) > 0:
        print(f"First document sample: {results['documents'][0][:200]}...")
        print(f"First metadata sample: {results['metadatas'][0]}")
    else:
        print("No documents found in collection! Exiting")
        return
    
    # Sort by page and position (if bbox exists)
    chunks_with_metadata = list(zip(
        results['documents'], 
        results['metadatas']
    ))
    
    # Sort by page first, then by y-coordinate (top) if bbox exists
    def sort_key(x):
        metadata = x[1]
        if 'bbox' in metadata:
            return (metadata['page'], metadata['bbox'][1])  # Sort by page, then y-coord
        return (metadata['page'], 0)  # Default y-coord to 0 if no bbox
    
    chunks_with_metadata.sort(key=sort_key)
    
    # Group chunks by page
    pages = {}
    for text, metadata in chunks_with_metadata:
        page_num = metadata['page']
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append((text, metadata))
    
    # Start HTML document
    html = """
    <html>
    <head>
        <style>
            .container { display: flex; margin-bottom: 20px; }
            .text-block { flex: 1; padding: 10px; margin: 5px; }
            .claims-block { flex: 1; padding: 10px; margin: 5px; }
            .has-claims { background-color: #e6ffe6; }
            .no-claims { background-color: #ffe6e6; }
            .page-marker { font-weight: bold; margin: 20px 0; }
            .metadata { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
    """
    
    extractor = ClaimExtractor()
    
    print("Processing pages and extracting claims...")
    for page_num in sorted(pages.keys()):
        print(f"Processing page {page_num}...")
        
        # Add page marker
        html += f"<div class='page-marker'>Page {page_num}</div>"
        
        # Combine all text on this page
        page_text = ""
        for text, metadata in pages[page_num]:
            if metadata.get('type') == 'text':  # Skip images
                page_text += text + "\n\n"
        
        # Extract claims from combined page text
        claims = extractor.extract_claims(page_text)
        has_claims = bool(claims)
        
        # Create side-by-side display
        html += f"""
        <div class='container'>
            <div class='text-block {("has-claims" if has_claims else "no-claims")}'>
                <div class='metadata'>Page {page_num}</div>
                {page_text}
            </div>
            <div class='claims-block'>
        """
        
        if has_claims:
            html += "<ul>"
            for claim in claims:
                html += f"<li>{claim}</li>"
            html += "</ul>"
        else:
            html += "<em>No claims detected</em>"
        
        html += "</div></div>"
    
    html += "</body></html>"
    
    # Write output
    with open(output_file, "w") as f:
        f.write(html)
    
    print(f"\nVisualization saved to {output_file}")


if __name__ == "__main__":
    import argparse
    from pdf_parser import DocumentManager
    
    parser = argparse.ArgumentParser(description='Extract and visualize claims from PDF')
    parser.add_argument('--pdf', type=str, default="example.pdf",
                       help='Path to PDF file')
    parser.add_argument('--output', type=str, default="claims_analysis.html",
                       help='Output HTML file path')
    args = parser.parse_args()
    
    # Initialize document manager
    doc_manager = DocumentManager()
    
    # Process PDF if not already processed
    if not Path(args.pdf).exists():
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)
        
    doc_manager.process_pdf(args.pdf)
    
    # Process and visualize claims
    print(f"\nExtracting claims from {args.pdf}...")
    process_and_visualize_claims(doc_manager, args.output)
    print(f"Done! Open {args.output} to view results")
