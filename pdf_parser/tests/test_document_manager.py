import pytest
from pathlib import Path
import shutil
from document_manager import DocumentManager
import tempfile

@pytest.fixture
def test_dirs():
    """Create and clean up test directories for cache and chromadb"""
    with tempfile.TemporaryDirectory() as cache_dir:
        with tempfile.TemporaryDirectory() as chroma_dir:
            yield cache_dir, chroma_dir

@pytest.fixture
def test_pdf(tmp_path):
    """Create a simple test PDF file"""
    pdf_path = tmp_path / "test.pdf"
    # You'll need to create a simple PDF here
    # For now just creating an empty file
    pdf_path.write_bytes(b"%PDF-1.4")  # Minimal PDF header
    return str(pdf_path)

def test_document_manager_caching(test_dirs, test_pdf):
    """Test that document manager correctly uses cache"""
    cache_dir, chroma_dir = test_dirs
    
    # First run - should process PDF
    doc_manager = DocumentManager(
        collection_name="test_collection",
        persist_dir=chroma_dir,
        cache_dir=cache_dir
    )
    
    # Initial processing
    doc_manager.process_pdf(test_pdf)
    
    # Check that cache was created
    cache_files = list(Path(cache_dir).glob("*.json"))
    assert len(cache_files) > 0, "No cache files created"
    
    # Check that ChromaDB has documents
    assert doc_manager.collection.count() > 0, "No documents in ChromaDB"
    
    # Second run - should use cache
    doc_manager2 = DocumentManager(
        collection_name="test_collection",
        persist_dir=chroma_dir,
        cache_dir=cache_dir
    )
    
    # Mock the processor to detect if it's called
    original_process = doc_manager2.processor.process_pdf
    process_called = False
    
    def mock_process(*args, **kwargs):
        nonlocal process_called
        process_called = True