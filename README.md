# Bank Loan Bot (with Form Filling Automation)

A Telegram bot that helps users submit loan enquiries through an automated form-filling process. The bot collects user information through a conversational interface and automatically fills out the online application form.

## Features

- 🤖 Interactive Telegram bot interface
- 💬 Natural language conversation with GPT-4 integration
- 📝 Step-by-step form filling process
- 🔄 Automatic form submission with Playwright
- ✅ Input validation for phone numbers and email addresses
- 📸 Screenshot verification of filled forms
- 🎯 Support for Select2 dropdown interactions

## Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- OpenAI API Key
- Playwright

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Create a `.env` file with your credentials:
```
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

## Usage

1. Start the bot:
```bash
python bot.py
```

2. Open Telegram and start a conversation with your bot:
   - Use `/start` to begin
   - Follow the bot's prompts to provide your information
   - The bot will automatically fill out the online form with your details

## Bot Commands

- `/start` - Start a new conversation
- `/cancel` - Cancel the current operation

## Form Fields

The bot collects the following information:
- Salutation (Mr/Mrs/Mdm/Ms/Dr)
- Full Name
- Contact Number (with country code)
- Email Address
- Best Time to Contact
- Nature of Enquiry

## Error Handling

- Input validation for phone numbers and email addresses
- Multiple fallback methods for form field selection
- Detailed error logging
- Screenshot verification of form filling

## Project Structure

```
├── bot.py              # Main bot implementation
├── config.py           # Configuration and constants
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── form_screenshots/  # Directory for form verification screenshots
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact [Your Contact Information] 