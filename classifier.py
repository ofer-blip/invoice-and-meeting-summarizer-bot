import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional
import config

# Define the Pydantic schema for structured output
class InvoiceClassification(BaseModel):
    is_invoice_or_receipt: bool = Field(
        description="True if the document is a tax invoice, receipt, invoice receipt, transaction invoice, or any billing document (חשבונית מס, קבלה, חשבונית מס קבלה, חשבונית עסקה, דרישת תשלום)."
    )
    document_type: str = Field(
        description="The type of document in Hebrew (e.g., 'חשבונית מס', 'קבלה', 'חשבונית מס קבלה', 'חשבונית עסקה', 'אחר')."
    )
    direction: str = Field(
        description="Must be either 'הכנסה' (Income) or 'הוצאה' (Expense). 'הכנסה' is when Shahaf Michael (שחף מיכאל) is the supplier/issuer of the document. 'הוצאה' is when Shahaf Michael is the customer/recipient receiving the invoice from a third-party supplier."
    )
    supplier_name: str = Field(
        description="The name of the business/supplier issuing the invoice/receipt."
    )
    client_name: str = Field(
        description="The name of the client/recipient of the invoice/receipt."
    )
    document_date: str = Field(
        description="The date of the document in YYYY-MM-DD format. If only DD/MM/YYYY is found, convert to YYYY-MM-DD."
    )
    total_amount: float = Field(
        description="The total amount of the invoice/receipt including VAT."
    )
    invoice_number: str = Field(
        description="The document/invoice/receipt serial number."
    )
    currency: str = Field(
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
    """Classifies a PDF attachment using Gemini, extracting key details and checking if it's an invoice."""
    try:
        # Construct the prompt instructing the model how to classify the document.
        # We mention Shahaf Michael (שחף מיכאל) and Ofer (עופר) as the business entities.
        # When testing on Ofer's email, the same logic applies (Ofer as the recipient).
        prompt = (
            "Analyze the attached PDF document and extract the billing information.\n"
            "Here is the context of the email in which it was received:\n"
            f"Subject: {email_subject}\n"
            f"Sender: {email_sender}\n\n"
            "Guidelines for classification:\n"
            "1. Determine if this document is indeed a financial invoice or receipt (tax invoice, transaction receipt, etc.).\n"
            "   - IMPORTANT: Skip credit card monthly statement notifications/reminders (e.g. from ICC / Cal / כרטיסי אשראי לישראל) and individual public transport ride/recharge receipts (e.g. from Rav-Kav Online / רב-קו אונליין) because they are covered by the main credit card invoice. For these, set 'is_invoice_or_receipt' to False.\n"
            "2. Determine the 'direction' (הכנסה / הוצאה):\n"
            "   - If 'שחף מיכאל' or 'עופר' (or their business names) is the supplier/issuer, it is an 'הכנסה' (Income).\n"
            "   - If 'שחף מיכאל' or 'עופר' is the client/recipient/payer, or if the invoice comes from an external supplier (like Morning, cell providers, hosting, etc.) and is billed to them, it is an 'הוצאה' (Expense).\n"
            "3. Extract the supplier name, client name, date (in YYYY-MM-DD format), total amount, currency (e.g. ILS, USD), and invoice number."
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
            "Analyze the email content below and extract the billing information.\n"
            "Determine if this email body represents a financial invoice, receipt, payment confirmation, billing statement, or notification (tax invoice, transaction receipt, bill, payment receipt, payment confirmation, etc.).\n"
            "Here is the context of the email:\n"
            f"Subject: {email_subject}\n"
            f"Sender: {email_sender}\n\n"
            "Guidelines for classification:\n"
            "1. Determine if this email body is indeed a financial invoice, receipt, payment confirmation, or billing document. Even if there is no physical PDF attachment and the email itself acts as the invoice/receipt notification or payment confirmation (possibly containing a link to view the invoice), classify it as True.\n"
            "   - IMPORTANT: Skip credit card monthly statement notifications/reminders (e.g. from ICC / Cal / כרטיסי אשראי לישראל) and individual public transport ride/recharge receipts (e.g. from Rav-Kav Online / רב-קו אונליין) because they are covered by the main credit card invoice. For these, set 'is_invoice_or_receipt' to False.\n"
            "2. Determine the 'direction' (הכנסה / הוצאה):\n"
            "   - If 'שחף מיכאל' or 'עופר' (or their business names) is the supplier/issuer, it is an 'הכנסה' (Income).\n"
            "   - If 'שחף מיכאל' or 'עופר' is the client/recipient/payer, or if the invoice comes from an external supplier (like Morning, Zoom, SUMIT, Cal, Kvish 6, Google Cloud, etc.) and is billed to them, it is an 'הוצאה' (Expense).\n"
            "3. Extract the supplier name, client name, date (in YYYY-MM-DD format), total amount, currency (e.g. ILS, USD), and invoice number.\n\n"
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
