import os
import json
from datetime import datetime
from pathlib import Path
import hashlib
import chromadb

class PDFProcessingCache:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_file_hash(self, filepath: str) -> str:
        """Generate hash of file contents"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    
    def needs_processing(self, filepath: str, pdf_name: str) -> bool:
        """Check if PDF needs to be reprocessed"""
        cache_path = os.path.join(self.cache_dir, f"{pdf_name}_meta.json")
        
        if not os.path.exists(cache_path):
            return True
            
        try:
            with open(cache_path) as f:
                metadata = json.load(f)
            return metadata.get('file_hash') != self.get_file_hash(filepath)
        except:
            return True
    
    def update_metadata(self, filepath: str, pdf_name: str):
        """Save processing metadata"""
        metadata = {
            'file_hash': self.get_file_hash(filepath),
            'last_processed': datetime.now().isoformat(),
            'filepath': filepath
        }
        
        with open(os.path.join(self.cache_dir, f"{pdf_name}_meta.json"), 'w') as f:
            json.dump(metadata, f)

    def reset(self):
        """Reset the entire cache by removing all metadata files"""
        if os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                if file.endswith('_meta.json'):
                    os.remove(os.path.join(self.cache_dir, file))
                    print(f"Removed cache file: {file}")
        print("Cache reset complete")

    def reset_document(self, pdf_name: str):
        """Reset cache for a specific document"""
        cache_path = os.path.join(self.cache_dir, f"{pdf_name}_meta.json")
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"Removed cache for document: {pdf_name}")


class ChromaDBManager:
    def __init__(self, persist_dir: str = ".chromadb"):
        self.client = chromadb.PersistentClient(path=persist_dir)
    
    def get_or_create_collection(self, name: str):
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(name)
            
    def delete_collection(self, name: str):
        try:
            self.client.delete_collection(name)
        except:
            pass
