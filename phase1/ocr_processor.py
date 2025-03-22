# ocr_processor.py
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat
from dotenv import load_dotenv
import tempfile

load_dotenv()

class OCRProcessor:
    def __init__(self):
        # Initialize Document Intelligence client
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        self.client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
    
    def process_document(self, file_path):
        with open(file_path, "rb") as f:
            file_content = f.read()
            poller = self.client.begin_analyze_document(
                "prebuilt-layout", 
                body=file_content,
            )
        result = poller.result()
        print(result.content)
        print("\n\n########################\n")
        for line in result.pages[0].lines:
            print(line.content)
        
        return result
    
    def process_document_md(self, file_path):
        with open(file_path, "rb") as f:
            file_content = f.read()
            poller = self.client.begin_analyze_document(
                "prebuilt-layout", 
                body=file_content,
                output_content_format=DocumentContentFormat.MARKDOWN
            )
        result = poller.result()
        
        return result.content
    
def save_to_file(text, file_path, file_format="txt", suffix="_extracted"):   
    # Get directory and filename components from original file
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    # Create new filename with specified extension
    new_filename = f"{filename_without_ext}{suffix}.{file_format}"
    output_path = os.path.join(directory, new_filename)
    
    # Write content to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    print(f"Text saved to: {output_path}")
    return output_path
    
# file = r"data/phase1_data/283_ex1.pdf"
# ocr = OCRProcessor()
# ocr.process_document(file)