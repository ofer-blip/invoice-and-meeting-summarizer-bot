import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional
import config

# Define the Pydantic schema for structured output
class InvoiceClassification(BaseModel):
    is_invoice_or_receipt: bool = Field(
        default=True,
        description="True for any financial document, invoice, receipt, transaction slip, payment confirmation, debit note, or credit memo."
    )
    document_type: str = Field(
        default="מסמך חשבונאי",
        description="The type of document in Hebrew (e.g., 'חשבונית מס', 'קבלה', 'חשבונית מס קבלה', 'חשבונית עסקה', 'אישור תשלום', 'הודעת זיכוי', 'חיוב אשראי', 'דרישת תשלום', 'אחר')."
    )
    direction: str = Field(
        default="לבדיקה",
        description="Must be 'הכנסה' (Income), 'הוצאה' (Expense), or 'לבדיקה' (Uncertain/Review). 'הכנסה' is when Shahaf Michael (שחף מיכאל) or Ofer (עופר) is the supplier/issuer. 'הוצאה' is when they are the customer/recipient. 'לבדיקה' when unclear."
    )
    supplier_name: str = Field(
        default="",
        description="The name of the business/supplier issuing the invoice/receipt/notice."
    )
    client_name: str = Field(
        default="",
        description="The name of the client/recipient of the invoice/receipt."
    )
    document_date: str = Field(
        default="",
        description="The date of the document in YYYY-MM-DD format. If only DD/MM/YYYY is found, convert to YYYY-MM-DD."
    )
    total_amount: float = Field(
        default=0.0,
        description="The total amount of the document including VAT (positive, or negative for credit/refund)."
    )
    invoice_number: str = Field(
        default="",
        description="The document/invoice/receipt/reference serial number."
    )
    currency: str = Field(
        default="ILS",
        description="The currency of the invoice (e.g. 'ILS' for shekels, 'USD' for US dollars, 'EUR' for euros)."
    )

def get_gemini_client():
    """Initializes the Gemini client using the API key in config or environment."""
    api_key = config.GEMINI_API_KEY or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Please set the GEMINI_API_KEY environment variable "
            "or configure it in config.py."
        )
    return genai.Client(api_key=api_key)

def classify_invoice(client, pdf_bytes, email_subject="", email_sender=""):
    """Classifies a PDF attachment using Gemini, extracting key details without dropping files."""
    try:
        prompt = (
            "Analyze the attached PDF document and extract the financial/billing information.\n"
            "Here is the context of the email in which it was received:\n"
            f"Subject: {email_subject}\n"
            f"Sender: {email_sender}\n\n"
            "CRITICAL GUIDELINES:\n"
            "1. DO NOT reject or drop any document. Every financial document, receipt, confirmation, or bill must be parsed.\n"
            "2. Determine the 'direction' ('הכנסה' | 'הוצאה' | 'לבדיקה'):\n"
            "   - If 'שחף מיכאל' or 'עופר' is the supplier/payee receiving payment, set to 'הכנסה'.\n"
            "   - If 'שחף מיכאל' or 'עופר' is the client/recipient/payer, or if from an external supplier (Morning, Google, Zoom, Cal, Kvish 6, etc.), set to 'הוצאה'.\n"
            "   - If unclear, set to 'לבדיקה'.\n"
            "3. Identify the document_type in Hebrew (e.g. 'חשבונית מס', 'קבלה', 'הודעת זיכוי', 'אישור תשלום', 'חיוב אשראי', 'דרישת תשלום', 'אחר').\n"
            "4. Extract supplier_name, client_name, document_date (YYYY-MM-DD), total_amount, currency, and invoice_number."
        )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type='application/pdf',
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InvoiceClassification,
                temperature=0.1
            ),
        )
        
        # Parse the structured JSON response into Pydantic model
        result = InvoiceClassification.model_validate_json(response.text)
        return result
    except Exception as e:
        print(f"Error classifying invoice: {e}")
        return None

def classify_invoice_body(client, email_body, email_subject="", email_sender=""):
    """Classifies an email body (text/html) using Gemini, extracting key details and checking if it's an invoice."""
    try:
        prompt = (
            "Analyze the email content below and extract the financial/billing information.\n"
            "This email represents a financial invoice, receipt, payment confirmation, billing statement, debit note, or transaction notice.\n"
            "Here is the context of the email:\n"
            f"Subject: {email_subject}\n"
            f"Sender: {email_sender}\n\n"
            "CRITICAL GUIDELINES:\n"
            "1. DO NOT reject or drop any document. Every document must be processed.\n"
            "2. Determine the 'direction' ('הכנסה' | 'הוצאה' | 'לבדיקה'):\n"
            "   - If 'שחף מיכאל' or 'עופר' is the supplier/payee receiving payment, set to 'הכנסה'.\n"
            "   - If 'שחף מיכאל' or 'עופר' is the client/recipient/payer, or if from an external supplier, set to 'הוצאה'.\n"
            "   - If unclear, set to 'לבדיקה'.\n"
            "3. Identify the document_type in Hebrew (e.g. 'אישור תשלום במייל', 'קבלה', 'חשבונית מס', 'דרישת תשלום', 'הודעת זיכוי', 'חיוב אשראי').\n"
            "4. Extract supplier_name, client_name, date (YYYY-MM-DD), total_amount, currency, and invoice_number.\n\n"
            f"Email Body Content:\n{email_body}"
        )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InvoiceClassification,
                temperature=0.1
            ),
        )
        
        result = InvoiceClassification.model_validate_json(response.text)
        return result
    except Exception as e:
        print(f"Error classifying invoice body: {e}")
        return None
