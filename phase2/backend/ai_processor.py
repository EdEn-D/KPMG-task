# openai_processor.py
import os
import json
import re
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIProcessor:
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        # Define the schema structure (only used as a template)
        self.schema_template = {
            "personalInfo": {
                "firstName": "",
                "lastName": "",
                "idNumber": "",  # Valid 9-digit number
                "gender": "",  # Male/Female/Other
                "age": "",  # Between 0 and 120
            },
            "healthInsurance": {
                "hmoName": "",  # מכבי | מאוחדת | כללית
                "hmoCardNumber": "",  # 9-digit
                "membershipTier": "",  # זהב | כסף | ארד
            },
        }

    def extract_fields(self, chat_history):
        """Extract all available user information from chat history"""
        system_prompt = f"""
        You are a data extraction model. Your task is to extract specific fields from the conversation history only in Hebrew or English.
        
        
        Extract the information into the following JSON schema:
        {json.dumps(self.schema_template, indent=2, ensure_ascii=False)}

        Return only the JSON output."""

        context = f"""
        Below is the conversation history. Extract the following fields from this conversation:
        {chat_history}
        """
        # Call Azure OpenAI
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context},
            ],
            temperature=0,
            model=self.deployment_name,
            response_format={"type": "json_object"},
        )

        # Extract and parse the response
        result_text = response.choices[0].message.content

        try:
            result_json = json.loads(result_text)
            return result_json
        except json.JSONDecodeError:
            # If there's an issue with the JSON, return the empty schema
            return self.schema_template.copy()

    def validate_fields(self, fields_json):
        """
        Validates the extracted fields from the conversation.
        Returns a dictionary with validation results.

        Does not report errors for missing required fields as this is an iterative process.
        """
        results = {"valid": True, "errors": {}, "warnings": {}}
        validated_data = {"personalInfo": {}, "healthInsurance": {}}

        # Validate personal info
        personal_info = fields_json.get("personalInfo", {})

        # Validate firstName
        first_name = personal_info.get("firstName", "")
        if first_name:
            if self._validate_name(first_name):
                validated_data["personalInfo"]["firstName"] = first_name
            else:
                results["errors"]["firstName"] = "Invalid characters in name"
                results["valid"] = False

        # Validate lastName
        last_name = personal_info.get("lastName", "")
        if last_name:
            if self._validate_name(last_name):
                validated_data["personalInfo"]["lastName"] = last_name
            else:
                results["errors"]["lastName"] = "Invalid characters in name"
                results["valid"] = False

        # Validate ID number
        id_number = personal_info.get("idNumber", "")
        if id_number:
            is_valid, error_msg = self._validate_israeli_id(id_number)
            if is_valid:
                validated_data["personalInfo"]["idNumber"] = id_number
            else:
                results["errors"]["idNumber"] = error_msg
                results["valid"] = False

        # Validate gender
        gender = personal_info.get("gender", "")
        if gender:
            if self._validate_gender(gender):
                validated_data["personalInfo"]["gender"] = gender
            else:
                results["errors"]["gender"] = "Must be Male, Female, or Other"
                results["valid"] = False

        # Validate age
        age = personal_info.get("age", "")
        if age:
            try:
                age_int = int(age)
                if 0 <= age_int <= 120:
                    validated_data["personalInfo"]["age"] = age
                else:
                    results["errors"]["age"] = "Age must be between 0 and 120"
                    results["valid"] = False
            except ValueError:
                results["errors"]["age"] = "Age must be a number"
                results["valid"] = False

        # Validate health insurance
        health_insurance = fields_json.get("healthInsurance", {})

        # Validate HMO name
        hmo_name = health_insurance.get("hmoName", "")
        valid_hmos = ["מכבי", "מאוחדת", "כללית"]
        if hmo_name:
            if hmo_name in valid_hmos:
                validated_data["healthInsurance"]["hmoName"] = hmo_name
            else:
                results["errors"]["hmoName"] = (
                    f"Must be one of: {', '.join(valid_hmos)}"
                )
                results["valid"] = False

        # Validate HMO card number
        hmo_card = health_insurance.get("hmoCardNumber", "")
        if hmo_card:
            if hmo_card.isdigit():
                validated_data["healthInsurance"]["hmoCardNumber"] = hmo_card
            else:
                results["errors"]["hmoCardNumber"] = (
                    "HMO card number must contain only digits"
                )
                results["valid"] = False

        # Validate membership tier
        tier = health_insurance.get("membershipTier", "")
        valid_tiers = ["זהב", "כסף", "ארד"]
        if tier:
            if tier in valid_tiers:
                validated_data["healthInsurance"]["membershipTier"] = tier
            else:
                results["errors"]["membershipTier"] = (
                    f"Must be one of: {', '.join(valid_tiers)}"
                )
                results["valid"] = False

        # Add validated data to results
        results["validated_data"] = validated_data
        return results

    def _validate_israeli_id(self, tz_number):
        """
        Validates an Israeli ID number (TZ) using the official algorithm.
        """
        if not tz_number or not tz_number.isdigit() or len(tz_number) > 9:
            return (False, "Invalid format (must be up to 9 digits)")

        # Pad the number with leading zeros to make it 9 digits
        tz_padded = tz_number.zfill(9)

        # Step 1: Create the alternating 1-2 pattern
        pattern = [1, 2, 1, 2, 1, 2, 1, 2, 1]

        # Step 2: Multiply each digit by its corresponding pattern digit
        multiplied = [int(tz_padded[i]) * pattern[i] for i in range(9)]

        # Step 3: Sum the digits of numbers greater than 9
        summed = []
        for num in multiplied:
            if num > 9:
                summed.append(sum(map(int, str(num))))
            else:
                summed.append(num)

        # Step 4: Check if the total sum is divisible by 10
        total_sum = sum(summed)
        if total_sum % 10 == 0:
            return (True, "Valid TZ number")
        else:
            return (False, "Invalid TZ number (checksum failed)")

    def _validate_name(self, name):
        """Validates a name contains only Hebrew or English letters and spaces"""
        hebrew_english_regex = r"^[A-Za-zא-ת\s]+$"
        return bool(re.match(hebrew_english_regex, name))

    def _validate_gender(self, gender):
        """Validates gender field"""
        valid_genders = ["male", "female", "other", "זכר", "נקבה", "אחר"]
        return gender.lower() in [g.lower() for g in valid_genders]

    def generate_response(self, validation_results, chat_history):
        # Detarmine 
        pass

    def qna_phase(self, validation_results, chat_history):
        pass

    def information_collection_phase(self, validation_results, chat_history):
        """Generate a response based on validation results and chat history"""
        # validated_data = validation_results.get("validated_data", {})

        system_prompt = f"""
        # Role
        You are an service agent that is tasked with collecting user information by chating with them, and asking them for information. You must communicate only in Hebrew or English.

        # Task
        Collect the following user information:
            - First and last name
            - ID number (valid 9-digit number)
            - Gender
            - Age (between 0 and 120)
            - HMO name (מכבי | מאוחדת | כללית)
            - HMO card number (9-digit)
            - Insurance membership tier (זהב | כסף | ארד)

        Based on the current validated data below, consider what information has already been collected and address any errors or warnings:
        {json.dumps(validation_results, indent=2, ensure_ascii=False)}
        
        # Specifics
        - Ask for information and conversate in the language of the user's inital message. 
        - Do not switch languages unless the user asks you to. 
        - Ask questions based on a single field at a time. 
        - Only 


        Once all the information is collected, send the user all the information you have collected and ask for confirmation.
        """

        context = f"""
        Below is the conversation history. Continue the conversation from the last message:

        {chat_history}
        """
        # Call Azure OpenAI
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context},
            ],
            temperature=0,
            model=self.deployment_name,
        )

        # Extract and parse the response
        response_text = response.choices[0].message.content

        return response_text
