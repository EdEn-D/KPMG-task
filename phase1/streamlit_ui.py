# app.py
import streamlit as st
import tempfile
import os
import time
from ocr_processor import OCRProcessor
from openai_processor import OpenAIProcessor
from validator import Validator

# Initialize processors
ocr = OCRProcessor()
ai = OpenAIProcessor()
validator = Validator()

def main():
    st.title("ביטוח לאומי Form Processor")
    st.markdown("Upload a National Insurance Institute form (PDF/JPG) for processing")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # OCR Processing
            with st.spinner("Extracting text from document..."):
                start_time = time.time()
                extracted_text = ocr.process_document_md(tmp_path)
                ocr_time = time.time() - start_time
            
            # AI Processing
            with st.spinner("Extracting structured data..."):
                start_time = time.time()
                extracted_data = ai.extract_fields(extracted_text)
                ai_time = time.time() - start_time
            
            # Validation
            validation_results = validator.validate_all(extracted_data)
            
            # Display results
            st.success("Processing completed successfully!")
            
            # Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("OCR Processing Time", f"{ocr_time:.2f}s")
            with col2:
                st.metric("AI Processing Time", f"{ai_time:.2f}s")
            
            # Results columns
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.subheader("Extracted Data")
                st.json(extracted_data)
            
            with col_right:
                st.subheader("Validation Results")
                for field, (is_valid, message) in validation_results.items():
                    if not is_valid:
                        st.error(f"{field}: {message}")
            
            # Raw Extracted Text
            with st.expander("View Raw Extracted Text"):
                st.code(extracted_text)
                
        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)

if __name__ == "__main__":
    main()