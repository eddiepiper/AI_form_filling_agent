import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Form URL
OCBC_FORM_URL = "https://www.ocbc.com/personal-banking/forms/overseas-property-loan-enquiry"

# Form Options
SALUTATION_OPTIONS = [
    "Mr",
    "Mrs",
    "Mdm",
    "Ms",
    "Dr"
]

BEST_TIME_OPTIONS = [
    "No preference",
    "9am - 1pm",
    "1pm - 6pm"
]

NATURE_ENQUIRY_OPTIONS = [
    "London Property Financing",
    "Australia Property Financing",
    "Malaysia Property Financing",
    "New York Property Financing",
    "Tokyo Property Financing",
    "None of the above"
]

# Form Field IDs
FORM_FIELDS = {
    'salutation': {
        'name': 'radio__f605609a-8c23-4910-8427-6e84be0dbb7d',
        'type': 'radio'
    },
    'full_name': {
        'id': 'text-field__f1d09e9f-a63a-4d5b-b988-0736fe635cb9',
        'type': 'text'
    },
    'contact': {
        'id': 'text-field__fab2839d-2f59-45fe-9a73-af2d9fe4dbd4',
        'type': 'text'
    },
    'email': {
        'id': 'email-field__587763a8-1b35-4b43-87cb-7e2c8fdf35f9',
        'type': 'text'
    },
    'best_time': {
        'id': 'dropdown-field__ba06bb8f-9b74-46ba-a8cc-d46d74e9cb71',
        'type': 'select2'
    },
    'nature_enquiry': {
        'id': 'dropdown-field__5675edb4-f8ed-44f8-a043-a0e9169999e3',
        'type': 'select2'
    }
}

# Response Messages
WELCOME_MESSAGE = """
👋 Hi! I'm your OCBC Overseas Property Loan Assistant.

I can help you:
• Submit an overseas property loan enquiry
• Get information about overseas property financing
• Connect you with our property loan specialists

How may I assist you today? 😊
"""

HELP_MESSAGE = """
Here are the commands you can use:
/start - Start a new conversation
/help - Show this help message
/cancel - Cancel the current operation

You can also just chat with me naturally about overseas property loans!
"""

TIMEOUT_MESSAGE = """
I haven't heard from you in a while. 
Feel free to start a new conversation anytime with /start 🔄
"""

ERROR_MESSAGE = """
I apologize, but I encountered an error. 
Please try again or contact OCBC directly at +65 6363 3333.
"""

FORM_SUBMITTED_MESSAGE = """
✅ Thank you for your enquiry!

I've prepared your form submission. Please review and submit your details using the link below:

{url}

Our property loan specialist will contact you soon.

Is there anything else I can help you with? 💬
"""

CONTACT_LATER_MESSAGE = """
No problem! Feel free to ask me any other questions about OCBC overseas property loans.
You can also start a new conversation anytime with /start 🔄
"""

# Form Field Selectors
FORM_SELECTORS = {
    'salutation': 'input[type="radio"][name="salutation"]',
    'full_name': 'input[type="text"][name="fullName"]',
    'contact': 'input[type="tel"][name="contactNumber"]',
    'email': 'input[type="email"][name="emailAddress"]',
    'best_time': 'select[name="bestTimeToContact"]',
    'nature_enquiry': 'select[name="natureOfEnquiry"]'
}

# Conversation States
(
    FULL_NAME,
    CONTACT,
    EMAIL,
    EMPLOYMENT,
    LOAN_PURPOSE,
    BEST_TIME,
    NATURE_ENQUIRY,
    CONFIRM_DETAILS,
    QUESTIONS
) = range(9)

# Form Options
EMPLOYMENT_OPTIONS = [
    "Full-time Employed",
    "Self-Employed",
    "Part-time Employed",
    "Retired",
    "Not Currently Employed"
]

LOAN_PURPOSE_OPTIONS = [
    "Investment",
    "Own Stay"
]

# Friendly Messages
CONTACT_MESSAGE = """
Thanks, {name}! 📱 Could you share your contact number? 
This will help OCBC's team reach out to you about your loan enquiry.
"""

EMAIL_MESSAGE = """
Perfect! 📧 What's the best email address to reach you at?
I'll make sure OCBC sends all the important information there.
"""

EMPLOYMENT_MESSAGE = """
Great! Now, could you tell me about your employment status? 
This helps us understand your loan eligibility better! 💼
"""

LOAN_PURPOSE_MESSAGE = """
Excellent! 🏠 What's the main purpose for this overseas property loan?
"""

BEST_TIME_MESSAGE = """
Almost there! ⏰ When would be the best time for OCBC to contact you?
"""

NATURE_ENQUIRY_MESSAGE = """
Last question! 🌏 Which region are you interested in for property financing?
"""

CONFIRMATION_MESSAGE = """
Perfect! Here's a summary of your details:

👤 Name: {name}
📱 Contact: {contact}
📧 Email: {email}
💼 Employment: {employment}
🏠 Loan Purpose: {loan_purpose}
⏰ Best Contact Time: {best_time}
🌏 Property Location: {nature_enquiry}

Would you like me to submit this form to OCBC? 
You can also edit any information if needed!

✅ Type 'submit' to proceed
✏️ Type 'edit' to make changes
❌ Type 'cancel' to start over
""" 