
"""
This module defines a Pydantic model for representing an email schema.

Model:
- EmailSchema: Represents the structure of an email including email address, sender's name, and subject.

"""

from pydantic import BaseModel, EmailStr

class EmailSchema(BaseModel):
    """
    Represents the structure of an email.

    Attributes:
    - email (EmailStr): The email address of the recipient.
    - fullname (str): The sender's name (default: "Sender Name").
    - subject (str): The subject of the email (default: "Sender Subject topic").

    """
    email: EmailStr
    fullname: str = "Sender Name"
    subject: str = "Sender Subject topic"

