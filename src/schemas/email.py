from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr
    fullname: str = "Sender Name"
    subject: str = "Sender Subject topic"

