# openai_processor.py
import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIProcessor:
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    def extract_fields(self, ocr_result):
        """
        Extract fields from OCR result using Azure OpenAI
        
        Args:
            ocr_result: Result from Azure Document Intelligence
            
        Returns:
            JSON object with extracted fields
        """
        # Prepare text content from OCR result
        content = ocr_result
        
        # Define the output schema for the model
        output_schema = {
            "lastName": "",
            "firstName": "",
            "idNumber": "",
            "gender": "",
            "dateOfBirth": {
                "day": "",
                "month": "",
                "year": ""
            },
            "address": {
                "street": "",
                "houseNumber": "",
                "entrance": "",
                "apartment": "",
                "city": "",
                "postalCode": "",
                "poBox": ""
            },
            "landlinePhone": "",
            "mobilePhone": "",
            "jobType": "",
            "dateOfInjury": {
                "day": "",
                "month": "",
                "year": ""
            },
            "timeOfInjury": "",
            "accidentLocation": "",
            "accidentAddress": "",
            "accidentDescription": "",
            "injuredBodyPart": "",
            "signature": "",
            "formFillingDate": {
                "day": "",
                "month": "",
                "year": ""
            },
            "formReceiptDateAtClinic": {
                "day": "",
                "month": "",
                "year": ""
            },
            "medicalInstitutionFields": {
                "healthFundMember": "",
                "natureOfAccident": "",
                "medicalDiagnoses": ""
            }
        }
        
        # Create a prompt for the OpenAI model
        system_prompt = """
        You are tasked with extracting information from ביטוח לאומי (National Insurance Institute) forms.
        You will be given OCR text from a form that may be in Hebrew, English, or mixed.
        Extract all relevant fields according to the output schema.
        For any fields that aren't present or can't be determined, use an empty string.
        The form may have fields related to personal information, accident details, and medical information.
        Return your response in valid JSON format exactly matching the output schema.
        """
        
        user_prompt = f"""
        Here is the OCR text from a ביטוח לאומי form:
        
        {content}
        
        Extract the information into the following JSON schema:
        {json.dumps(output_schema, indent=2, ensure_ascii=False)}
        
        Return only the JSON output.
        """
        
        # Call Azure OpenAI
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            model=self.deployment_name,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the response
        result_text = response.choices[0].message.content
        
        try:
            result_json = json.loads(result_text)
            return result_json
        except json.JSONDecodeError:
            # If there's an issue with the JSON, return the schema with empty values
            # TODO: Probably change this to return an error message
            return output_schema
    