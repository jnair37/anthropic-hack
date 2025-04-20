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