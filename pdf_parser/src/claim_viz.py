import sys
from pathlib import Path
from claim_extractor import ClaimExtractor
import time
from dotenv import load_dotenv
import argparse
from pdf_parser import DocumentManager


load_dotenv()

MAX_CHUNKS = 20

def create_html_display(page_texts_with_claims):
    """
    Create an HTML page displaying text and claims side by side.
    
    Args:
        page_texts_with_claims: List of tuples (page_text, claims_list)
        
    Returns:
        html: String containing complete HTML document
    """
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Text and Claims</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .page-section {
                margin-bottom: 30px;
                border-bottom: 1px solid #eee;
                padding-bottom: 20px;
            }
            .page-header {
                background-color: #f0f7ff;
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            .display-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .text-panel {
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #4285f4;
            }
            .claims-panel {
                display: flex;
                flex-direction: column;
            }
            .claim-item {
                background-color: #f0f7ff;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                border-left: 4px solid #0f9d58;
            }
            .claim-header {
                font-weight: bold;
                margin-bottom: 5px;
                color: #333;
            }
            .no-claims {
                color: #999;
                font-style: italic;
                padding: 15px;
                text-align: center;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PDF Text and Claims</h1>
    """
    
    # Add each page section
    for i, (page_text, claims) in enumerate(page_texts_with_claims):
        html += f"""
            <div class="page-section">
                <div class="page-header">Page {i+1}</div>
                <div class="display-grid">
                    <div class="text-panel">
                        <pre>{page_text}</pre>
                    </div>
                    <div class="claims-panel">
        """
        
        if claims and len(claims) > 0:
            for claim_idx, claim in enumerate(claims):
                html += f"""
                        <div class="claim-item">
                            <div class="claim-header">Claim {claim_idx+1}</div>
                            <pre>{str(claim)}</pre>
                        </div>
                """
        else:
            html += """
                        <div class="no-claims">No claims found</div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        """
    
    # Close HTML
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

def process_and_visualize_claims(docmgr, pdf_path, output_file: str = "claims_analysis_v2.html", all_output_file: str = "pages_text_claims_v2.html"):
    """Process all chunks and create visualization"""

    # Get all chunks from ChromaDB in order
    print("Getting chunks from ChromaDB...")
    results = docmgr.text_collection.get()
    print(f"Results keys: {results.keys()}")
    print(f"Number of documents: {len(results['documents'])}")
    if len(results['documents']) > 0:
        print(f" document sample: {results['documents'][0][:200]}...")
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
    
    # Start HTML document for chunks view
    chunks_html = """
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
    
    # Extract page by page text
    page_texts = docmgr.process_pdf_all_or_pages(pdf_path, type="pages")
    page_texts_with_claims = []
    
    print("Processing pages and extracting claims...")
    for page_dict in page_texts[:10]:
        page_num = list(page_dict.keys())[0]
        text = list(page_dict.values())[0]
        print(f"Processing page {page_num}...")
        page_text_claims = extractor.extract_claims(text)
        for claim in page_text_claims:
            if 'howKnown' in claim.keys():
                claim['howKnown'] = 'WEB_DOCUMENT'
        page_texts_with_claims.append((text, page_text_claims))
    
    # Generate HTML for pages view
    pages_html = create_html_display(page_texts_with_claims)
    
    # Process chunks
    for i, (text, metadata) in enumerate(chunks_with_metadata):
        print(f"Processing chunk {i+1}/{total_chunks} on page {metadata['page']}...")
        
        # Add page marker if new page
        if metadata['page'] != current_page:
            chunks_html += f"<div class='page-marker'>Page {metadata['page']}</div>"
            current_page = metadata['page']
        
        # Extract claims for this chunk only
        claims = extractor.extract_claims(text)
        has_claims = bool(claims)
        
        # Create side-by-side display
        chunks_html += f"""
        <div class='container'>
            <div class='text-block {("has-claims" if has_claims else "no-claims")}'>
                <div class='metadata'>Page {metadata['page']}</div>
                {text}
            </div>
            <div class='claims-block'>
        """
        
        if has_claims:
            chunks_html += "<ul>"
            for claim in claims:
                chunks_html += f"<li>{claim}</li>"
            chunks_html += "</ul>"
        else:
            chunks_html += "<em>No claims detected</em>"
        
        chunks_html += "</div></div>"
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.1)
    
    chunks_html += "</body></html>"
    
    # Write output for chunks view
    with open(output_file, "w") as f:
        f.write(chunks_html)
    
    print(f"\nChunks visualization saved to {output_file}")

    # Write output for pages view
    with open(all_output_file, "w") as f:
        f.write(pages_html)
    
    print(f"\nPages visualization saved to {all_output_file}")


if __name__ == "__main__":
    path = "../gates/2024-goalkeepers-report_en.pdf" # change to your path
    parser = argparse.ArgumentParser(description='Extract and visualize claims from PDF')
    parser.add_argument('--pdf', type=str, default=path,
                       help='Path to PDF file')
    parser.add_argument('--output', type=str, default="claims_analysis_v2.html",
                       help='Output HTML file path for chunks view')
    parser.add_argument('--pages-output', type=str, default="pages_text_claims_v2.html",
                       help='Output HTML file path for pages view')
    args = parser.parse_args()
    
    # Initialize document manager and processor
    doc_manager = DocumentManager()
    
    # Process PDF if not already processed
    if not Path(args.pdf).exists():
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)
        
    doc_manager.process_pdf(args.pdf)
    
    # Process and visualize claims
    print(f"\nExtracting claims from {args.pdf}...")
    process_and_visualize_claims(doc_manager, args.pdf, args.output, args.pages_output)
    print(f"Done! Open {args.output} to view chunks results")
    print(f"Done! Open {args.pages_output} to view pages results")