# import io
# import re
# import spacy
# import phonenumbers
# import pyap
# from typing import Dict, List, Tuple, Optional, BinaryIO, Union
# from PyPDF2 import PdfReader


# def redact_pdf(uploaded_file: Union[BinaryIO, io.BytesIO], 
#                spacy_model_name: str = "en_core_web_sm") -> Tuple[str, Dict[str, str]]:
#     """
#     Redact sensitive information from a PDF file uploaded via Streamlit's file_uploader.
    
#     Args:
#         uploaded_file: The PDF file object from st.file_uploader
#         spacy_model_name: Name of the spaCy model to use for NER
        
#     Returns:
#         Tuple containing (redacted_text, replacements_dict)
#     """
#     # Load spaCy model
#     try:
#         nlp = spacy.load(spacy_model_name)
#     except OSError:
#         # Download the model if not available
#         spacy.cli.download(spacy_model_name)
#         nlp = spacy.load(spacy_model_name)
    
#     # Dictionary to track replacements
#     replacements = {}
    
#     # Extract text from PDF
#     text = extract_text_from_pdf(uploaded_file)
#     if not text:
#         return "", {}
    
#     # Apply redactions in sequence
#     redacted_text = text
#     redacted_text = redact_names(redacted_text, nlp, replacements)
#     redacted_text = redact_email_addresses(redacted_text, replacements)
#     redacted_text = redact_phone_numbers(redacted_text, replacements)
#     redacted_text = redact_addresses(redacted_text, replacements)
    
#     return redacted_text, replacements


# def extract_text_from_pdf(pdf_file: Union[BinaryIO, io.BytesIO]) -> str:
#     """
#     Extract text from a PDF file object.
    
#     Args:
#         pdf_file: The PDF file object
        
#     Returns:
#         Extracted text as a string
#     """
#     try:
#         reader = PdfReader(pdf_file)
#         text = ""
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:  # Make sure we don't add None
#                 # Clean up excessive newlines and whitespace
#                 # # 1. Replace multiple newlines with a single newline
#                 # cleaned_text = re.sub(r'\n{2,}', '\n', page_text)
                
#                 # # 2. Replace newlines that don't represent paragraph breaks with spaces
#                 # # (Usually a paragraph ends with period, question mark, exclamation, or colon)
#                 # cleaned_text = re.sub(r'(?<![.!?:])\n(?=[a-z])', ' ', cleaned_text)
                
#                 # # 3. Clean up multiple spaces
#                 # cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
                
#                 # # 4. Preserve paragraph structure but remove unnecessary line breaks
#                 # cleaned_text = re.sub(r'\n{2,}', '\n\n', cleaned_text)

#                 # Replace all newlines with nothing
#                 cleaned_text = page_text.replace('\n ', ' ')
#                 cleaned_text = cleaned_text.replace('\n', '')
#                 # cleaned_text = re.sub(r'[^\w\s,.+@\-#()]', '', cleaned_text)

#                 # 5. Clean up any trailing/leading whitespace
#                 cleaned_text = cleaned_text.strip()
                
#                 text += cleaned_text

#         return text
    
#     except Exception as e:
#         print(f"Error extracting text from PDF: {e}")
#         return ""


# def redact_names(text: str, nlp, replacements: Dict[str, str]) -> str:
#     """
#     Redact person names using spaCy NER.
    
#     Args:
#         text: The text to redact
#         nlp: spaCy NLP model
#         replacements: Dictionary to store replacements
        
#     Returns:
#         Text with names redacted
#     """
#     doc = nlp(text)
#     redacted = text

#     print("Document:", doc[:500])
#     print("Before name redaction:", redacted[:500])
    
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             if ent.text not in replacements:
#                 replacements[ent.text] = f"[PERSON_{len(replacements) + 1}]"
            
#             # Replace all occurrences with word boundaries
#             pattern = r'\b' + re.escape(ent.text) + r'\b'
#             redacted = re.sub(pattern, replacements[ent.text], redacted)
    
#     print("Names redacted!")
#     print("After name redaction:", redacted[:500])

#     return redacted


# def redact_email_addresses(text: str, replacements: Dict[str, str]) -> str:
#     """
#     Redact email addresses using regex.
    
#     Args:
#         text: The text to redact
#         replacements: Dictionary to store replacements
        
#     Returns:
#         Text with email addresses redacted
#     """
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     redacted = text
    
#     for match in re.finditer(email_pattern, redacted):
#         email = match.group()
#         if email not in replacements:
#             replacements[email] = f"[EMAIL_{len(replacements) + 1}]"
        
#         # Replace the specific match
#         start, end = match.span()
#         redacted = redacted[:start] + replacements[email] + redacted[end:]
    
#     print("Emails redacted!")

#     return redacted


# def redact_phone_numbers(text: str, replacements: Dict[str, str]) -> str:
#     """
#     Redact phone numbers using the phonenumbers library.
    
#     Args:
#         text: The text to redact
#         replacements: Dictionary to store replacements
        
#     Returns:
#         Text with phone numbers redacted
#     """
#     redacted = text
    
#     # Search for phone numbers in multiple regions
#     for region in ["US", "GB", "CA", "AU", "IN"]:
#         for match in phonenumbers.PhoneNumberMatcher(redacted, region):
#             phone_number = match.raw_string
#             if phone_number not in replacements:
#                 replacements[phone_number] = f"[PHONE_{len(replacements) + 1}]"
            
#             # Replace the specific match
#             start, end = match.start, match.end
#             redacted = redacted[:start] + replacements[phone_number] + redacted[end:]
    
#     print("Phone numbers redacted!")

#     return redacted


# def redact_addresses(text: str, replacements: Dict[str, str]) -> str:
#     """
#     Redact postal addresses using pyap.
    
#     Args:
#         text: The text to redact
#         replacements: Dictionary to store replacements
        
#     Returns:
#         Text with addresses redacted
#     """
#     # redacted = text

#     # # Find addresses for multiple countries
#     # for country in ["US", "CA", "GB"]:
#     #     addresses = pyap.parse(redacted, country=country)
        
#     #     for address in addresses:
#     #         address_text = address.full_address
#     #         if address_text not in replacements:
#     #             replacements[address_text] = f"[ADDRESS_{len(replacements) + 1}]"
           
#     #         start = address.as_dict()['match_start']
#     #         end = start + len(address_text)
#     #         print(replacements[address_text])
#     #         # Replace in the text - need to be careful with special chars in addresses
#     #         # pattern = re.escape(address_text)
#     #         redacted = redacted[:start + 1] + replacements[address_text] + redacted[end:]
    
#     # print("Addresses redacted!")
#     # return redacted

#     redacted = text
    
#     # First, create a normalized version for address detection
#     # Replace special characters with spaces
#     normalized_text = re.sub(r'[^\w\s,.]', ' ', text)
    
#     # Find addresses for multiple countries
#     for country in ["US", "CA", "GB"]:
#         # Try with both original and normalized versions
#         for process_text in [normalized_text, normalized_text.title()]:
#             addresses = pyap.parse(process_text, country=country)
            
#             for address in addresses:
#                 address_text = address.full_address
                
#                 # Find the address in the original text
#                 # This can be tricky since we normalized the text for detection
#                 original_address = find_original_address(text, address_text)
                
#                 if original_address and original_address not in replacements:
#                     replacements[original_address] = f"[ADDRESS_{len(replacements) + 1}]"
                
#                 # Replace in the text - need to be careful with special chars in addresses
#                 if original_address:
#                     pattern = re.escape(original_address)
#                     redacted = re.sub(pattern, replacements[original_address], redacted)
    
#     return redacted

# def find_original_address(original_text, normalized_address):
#     """
#     Try to find the original address in the text based on the normalized version.
#     This is a simplistic approach and might need improvement for edge cases.
#     """
#     # Create a pattern from normalized address, allowing for different separators
#     parts = re.split(r'[\s,]+', normalized_address)
#     pattern = r'[^\w]*'.join(re.escape(part) for part in parts if part)
    
#     matches = re.search(pattern, original_text, re.IGNORECASE)
#     if matches:
#         return matches.group(0)
#     return None

import io
import re
import spacy
import phonenumbers
import pyap
from typing import BinaryIO, Union, Optional
from PyPDF2 import PdfReader


def redact_pdf(uploaded_file: Union[BinaryIO, io.BytesIO], 
               spacy_model_name: str = "en_core_web_sm") -> str:
    """
    Remove sensitive information from a PDF file uploaded via Streamlit's file_uploader.
    
    Args:
        uploaded_file: The PDF file object from st.file_uploader
        spacy_model_name: Name of the spaCy model to use for NER
        
    Returns:
        Text with sensitive information removed
    """
    # Load spaCy model
    try:
        nlp = spacy.load(spacy_model_name)
    except OSError:
        # Download the model if not available
        spacy.cli.download(spacy_model_name)
        nlp = spacy.load(spacy_model_name)
    
    # Extract text from PDF
    text = extract_text_from_pdf(uploaded_file)
    if not text:
        return "no text"
    
    # Apply redactions in sequence
    redacted_text = text
    redacted_text = remove_names(redacted_text, nlp)
    redacted_text = remove_email_addresses(redacted_text)
    redacted_text = remove_phone_numbers(redacted_text)
    redacted_text = remove_addresses(redacted_text)
    
    return redacted_text


def extract_text_from_pdf(pdf_file: Union[BinaryIO, io.BytesIO]) -> str:
    """
    Extract text from a PDF file object.
    
    Args:
        pdf_file: The PDF file object
        
    Returns:
        Extracted text as a string
    """
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text: 
                cleaned_text = page_text.replace('\n ', ' ')
                cleaned_text = cleaned_text.replace('\n', '')
                cleaned_text = cleaned_text.strip()
                text += cleaned_text
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def remove_names(text: str, nlp) -> str:
    """
    Remove person names using spaCy NER.
    
    Args:
        text: The text to process
        nlp: spaCy NLP model
        
    Returns:
        Text with names removed
    """
    doc = nlp(text)
    redacted = text
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Remove all occurrences with word boundaries
            pattern = r'\b' + re.escape(ent.text) + r'\b'
            redacted = re.sub(pattern, "", redacted)
    
    return redacted


def remove_email_addresses(text: str) -> str:
    """
    Remove email addresses using regex.
    
    Args:
        text: The text to process
        
    Returns:
        Text with email addresses removed
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    redacted = re.sub(email_pattern, "", text)
    return redacted


def remove_phone_numbers(text: str) -> str:
    """
    Remove phone numbers using the phonenumbers library.
    
    Args:
        text: The text to process
        
    Returns:
        Text with phone numbers removed
    """
    redacted = text
    
    # Search for phone numbers in multiple regions
    for region in ["US", "GB", "CA", "AU", "IN"]:
        for match in phonenumbers.PhoneNumberMatcher(redacted, region):
            phone_number = match.raw_string
            # Remove the specific match
            start, end = match.start, match.end
            redacted = redacted[:start] + redacted[end:]
    
    return redacted


# def remove_addresses(text: str) -> str:
#     """
#     Remove postal addresses using pyap.
    
#     Args:
#         text: The text to process
        
#     Returns:
#         Text with addresses removed
#     """
#     redacted = text
    
#     # Find addresses for multiple countries
#     for country in ["US", "CA", "GB"]:
#         addresses = pyap.parse(redacted, country=country)
        
#         for address in addresses:
#             address_text = address.full_address
#             # Remove the address from the text
#             pattern = re.escape(address_text)
#             redacted = re.sub(pattern, "", redacted)
    
#     return redacted

def remove_addresses(text: str) -> str:
    """
    Redact postal addresses using pyap.
    
    Args:
        text: The text to redact
        replacements: Dictionary to store replacements
        
    Returns:
        Text with addresses redacted
    """

    redacted = text
    
    # First, create a normalized version for address detection
    # Replace special characters with spaces
    normalized_text = re.sub(r'[^\w\s,.]', ' ', text)
    
    # Find addresses for multiple countries
    for country in ["US", "CA", "GB"]:
        # Try with both original and normalized versions
        for process_text in [normalized_text, normalized_text.title()]:
            addresses = pyap.parse(process_text, country=country)
            
            for address in addresses:
                address_text = address.full_address
                
                # Find the address in the original text
                # This can be tricky since we normalized the text for detection
                original_address = find_original_address(text, address_text)
                
                # Replace in the text - need to be careful with special chars in addresses
                if original_address:
                    pattern = re.escape(original_address)
                    redacted = re.sub(pattern, "", redacted)
    
    return redacted

def find_original_address(original_text, normalized_address):
    """
    Try to find the original address in the text based on the normalized version.
    This is a simplistic approach and might need improvement for edge cases.
    """
    # Create a pattern from normalized address, allowing for different separators
    parts = re.split(r'[\s,]+', normalized_address)
    pattern = r'[^\w]*'.join(re.escape(part) for part in parts if part)
    
    matches = re.search(pattern, original_text, re.IGNORECASE)
    if matches:
        return matches.group(0)
    return None