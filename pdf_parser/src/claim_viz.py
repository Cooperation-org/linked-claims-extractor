import sys
from pathlib import Path
from claim_extractor import ClaimExtractor
import time
from dotenv import load_dotenv

load_dotenv()

MAX_CHUNKS = 20

def process_and_visualize_claims(docmgr, output_file: str = "claims_analysis.html"):
    """Process all chunks and create visualization"""

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
        exit
    
    # Sort by page and position
    chunks_with_metadata = list(zip(
        results['documents'][0:MAX_CHUNKS], 
        results['metadatas'][0:MAX_CHUNKS]
    ))
    chunks_with_metadata.sort(key=lambda x: (x[1]['page']))
    
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
    current_page = -1
    
    print("Processing chunks and extracting claims...")
    total_chunks = len(chunks_with_metadata)
    
    for i, (text, metadata) in enumerate(chunks_with_metadata):
        print(f"Processing chunk {i+1}/{total_chunks} on page {metadata['page']}...")
        
        # Add page marker if new page
        if metadata['page'] != current_page:
            html += f"<div class='page-marker'>Page {metadata['page']}</div>"
            current_page = metadata['page']
        
        # Extract claims
        claims = extractor.extract_claims(text)
        has_claims = bool(claims)
        
        # Create side-by-side display
        html += f"""
        <div class='container'>
            <div class='text-block {("has-claims" if has_claims else "no-claims")}'>
                <div class='metadata'>Page {metadata['page']}</div>
                {text}
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
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.1)
    
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
