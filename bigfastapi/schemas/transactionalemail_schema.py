import datetime as dt
from pydantic import EmailStr, BaseModel


class InvoiceMail(BaseModel):
    subject: str
    recipient: EmailStr
    title: str
    first_name: str
    amount: str
    due_date: str
    payment_link: str
    invoice_id: str
    description: str

class ReceiptMail(BaseModel):
    subject: str
    recipient: EmailStr
    title: str
    first_name: str
    amount: str
    receipt_id: str
    description: str