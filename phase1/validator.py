import re
from datetime import datetime

class Validator:
    def __init__(self):
        self.hebrew_english_regex = r'^[A-Za-zא-ת\s]+$'
        self.street_regex = r'^[A-Za-zא-ת0-9\s]+$'
        self.landline_regex = r'^0\d\d{7}$'
        self.mobile_regex = r'^05\d\d{7}$'
        self.time_regex = r'^\d{2}:\d{2}$'
        self.health_fund_options = [
            'כללית', 'מאוחדת', 'מכבי', 'לאומית',
            'הנפגע חבר בקופת חולים', 'הנפגע אינו חבר בקופת חולים'
        ]

    def validate_all(self, data):
        results = {}
        
        # Personal Information
        results['lastName'] = self.validate_name(data.get('lastName', ''))
        results['firstName'] = self.validate_name(data.get('firstName', ''))
        results['idNumber'] = self.validate_id_number(data.get('idNumber', ''))
        results['gender'] = self.validate_gender(data.get('gender', ''))
        results['dateOfBirth'] = self.validate_date(data.get('dateOfBirth', {}))
        
        # Address Information
        address = data.get('address', {})
        results['street'] = self.validate_street(address.get('street', ''))
        results['houseNumber'] = self.validate_house_number(address.get('houseNumber', ''))
        results['city'] = self.validate_city(address.get('city', ''))
        results['postalCode'] = self.validate_postal_code(address.get('postalCode', ''))
        results['poBox'] = self.validate_po_box(address.get('poBox', ''))
        
        # Contact Information
        results['landlinePhone'] = self.validate_landline(data.get('landlinePhone', ''))
        results['mobilePhone'] = self.validate_mobile(data.get('mobilePhone', ''))
        results['phoneValidation'] = self.validate_phone_requirement(
            data.get('landlinePhone', ''), data.get('mobilePhone', '')
        )
        
        # Accident Information
        results['dateOfInjury'] = self.validate_date(data.get('dateOfInjury', {}))
        results['timeOfInjury'] = self.validate_time(data.get('timeOfInjury', ''))
        results['accidentLocation'] = self.validate_required(data.get('accidentLocation', ''), 'Accident location')
        results['accidentAddress'] = self.validate_required(data.get('accidentAddress', ''), 'Accident address')
        results['accidentDescription'] = self.validate_required(data.get('accidentDescription', ''), 'Accident description')
        results['injuredBodyPart'] = self.validate_required(data.get('injuredBodyPart', ''), 'Injured body part')
        
        # Dates
        results['formFillingDate'] = self.validate_date(data.get('formFillingDate', {}))
        results['formReceiptDateAtClinic'] = self.validate_date(data.get('formReceiptDateAtClinic', {}))
        
        # Medical Information
        medical = data.get('medicalInstitutionFields', {})
        results['healthFundMember'] = self.validate_health_fund(medical.get('healthFundMember', ''))
        results['natureOfAccident'] = self.validate_optional(medical.get('natureOfAccident', ''), 'Nature of accident')
        results['medicalDiagnoses'] = self.validate_optional(medical.get('medicalDiagnoses', ''), 'Medical diagnoses')
        
        # Signature
        results['signature'] = self.validate_required(data.get('signature', ''), 'Signature')
        
        return results

    def validate_tz(self, tz_number):
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

    def validate_id_number(self, value):
        """
        Validates the ID number (TZ) field.
        """
        if not value:
            return (False, "Required field")
        
        # Use the TZ validation algorithm
        return self.validate_tz(value)

    def validate_phone_requirement(self, landline, mobile):
        """
        Validates that at least one phone number (mobile or landline) is provided.
        """
        if not landline and not mobile:
            return (False, "At least one phone number (mobile or landline) is required")
        return (True, "Valid")

    def validate_health_fund(self, value):
        """
        Validates the health fund field.
        """
        if not value:
            return (False, "Required field")
        if value not in self.health_fund_options:
            return (False, f"Must be one of: {', '.join(self.health_fund_options)}")
        return (True, "Valid")

    def validate_optional(self, value, field_name):
        """
        Validates optional fields.
        """
        if not value:
            return (True, f"{field_name} is optional")
        return (True, "Valid")

    # Other validation methods remain unchanged...
    def validate_name(self, value):
        if not value:
            return (False, "Required field")
        if not re.match(self.hebrew_english_regex, value):
            return (False, "Invalid characters")
        return (True, "Valid")

    def validate_gender(self, value):
        valid = ['male', 'female', 'זכר', 'נקבה']
        if value.lower() not in [v.lower() for v in valid]:
            return (False, f"Must be one of: {', '.join(valid)}")
        return (True, "Valid")

    def validate_date(self, date_dict):
        try:
            day = date_dict.get('day', '')
            month = date_dict.get('month', '')
            year = date_dict.get('year', '')
            
            if not (day and month and year):
                return (False, "Missing components")
                
            datetime(year=int(year), month=int(month), day=int(day))
            return (True, "Valid date")
        except ValueError:
            return (False, "Invalid date")
        except:
            return (False, "Invalid format")

    def validate_street(self, value):
        if not value:
            return (False, "Required field")
        if not re.match(self.street_regex, value):
            return (False, "Invalid characters")
        return (True, "Valid")

    def validate_house_number(self, value):
        if not value:
            return (False, "Required field")
        if not value.isdigit() or int(value) <= 0:
            return (False, "Must be positive number")
        return (True, "Valid")

    def validate_city(self, value):
        if not value:
            return (False, "Required field")
        if not re.match(self.hebrew_english_regex, value):
            return (False, "Invalid characters")
        return (True, "Valid")

    def validate_postal_code(self, value):
        if not value:
            return (False, "Required field")
        if not value.isdigit() or len(value) != 7:
            return (False, "Must be 7 digits")
        return (True, "Valid")

    def validate_po_box(self, value):
        if value and not value.isdigit():
            return (False, "Must be numeric")
        return (True, "Valid") if not value else (True, "Valid (optional)")

    def validate_landline(self, value):
        if value and not re.match(self.landline_regex, value):
            return (False, "Invalid format (e.g., 031234567)")
        return (True, "Valid")

    def validate_mobile(self, value):
        if value and not re.match(self.mobile_regex, value):
            return (False, "Invalid format (e.g., 0501234567)")
        return (True, "Valid")

    def validate_time(self, value):
        if value and not re.match(self.time_regex, value):
            return (False, "Invalid time format (HH:MM)")
        return (True, "Valid")

    def validate_required(self, value, field_name):
        if not value:
            return (False, f"{field_name} is required")
        return (True, "Valid")