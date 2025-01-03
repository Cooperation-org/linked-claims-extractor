import cmd
import json
from typing import Optional
from .document_manager import DocumentManager

class DocumentREPL(cmd.Cmd):
    intro = 'Welcome to the Document Query REPL. Type help or ? to list commands.'
    prompt = '(doc) '
    
    def __init__(self, 
                 doc_manager: DocumentManager,
                 default_system_prompt: str = "You are a helpful assistant analyzing documents."):
        super().__init__()
        self.doc_manager = doc_manager
        self.system_prompt = default_system_prompt
    
    def do_query(self, arg):
        """Query the documents: query <your question>"""
        if not arg:
            print("Please provide a query")
            return
        
        results = self.doc_manager.query(arg)
        print("\nResults:")
        for r in results:
            print(f"\nFrom document: {r['metadata']['source_document']}")
            print(f"Content: {r['content']}")
            print(f"Page: {r['metadata']['page']}")
    
    def do_set_prompt(self, arg):
        """Set system prompt: set_prompt <new prompt>"""
        if not arg:
            print("Current system prompt:", self.system_prompt)
            return
        self.system_prompt = arg
        print("System prompt updated")
    
    def do_save_prompt(self, arg):
        """Save current prompt to file: save_prompt <filename>"""
        filename = arg or "prompt.json"
        with open(filename, 'w') as f:
            json.dump({"system_prompt": self.system_prompt}, f)
        print(f"Prompt saved to {filename}")
    
    def do_load_prompt(self, arg):
        """Load prompt from file: load_prompt <filename>"""
        filename = arg or "prompt.json"
        try:
            with open(filename) as f:
                data = json.load(f)
                self.system_prompt = data["system_prompt"]
            print("Prompt loaded successfully")
        except Exception as e:
            print(f"Error loading prompt: {e}")
    
    def do_clear_cache(self, arg):
        """Clear the PDF processing cache: clear_cache [pdf_path]"""
        if arg:
            self.doc_manager.processor.clear_cache(arg)
        else:
            self.doc_manager.processor.clear_cache()
    
    def do_quit(self, arg):
        """Exit the REPL"""
        return True
        
    def default(self, line):
        """Treat any input without a command as a query"""
        self.do_query(line)
    
    # Aliases
    do_q = do_quit
    do_exit = do_quit
