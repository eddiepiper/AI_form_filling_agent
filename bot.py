import asyncio
import logging
import re
from playwright.async_api import async_playwright
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from openai import OpenAI
from config import *
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configure OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Validation patterns
PHONE_PATTERN = re.compile(r'^\+\d+$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$')

# States
(
    INITIAL_NAME,
    INITIAL_QUESTION,
    ASK_FOR_CONTACT,
    SALUTATION,
    FULL_NAME,
    CONTACT,
    EMAIL,
    BEST_TIME,
    NATURE_ENQUIRY,
    CONFIRM_DETAILS,
) = range(10)

class OCBCLoanBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                INITIAL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_initial_name)],
                INITIAL_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_initial_question)],
                ASK_FOR_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ask_for_contact)],
                SALUTATION: [CallbackQueryHandler(self.salutation)],
                FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.full_name)],
                CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.contact)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.email)],
                BEST_TIME: [CallbackQueryHandler(self.best_time)],
                NATURE_ENQUIRY: [CallbackQueryHandler(self.nature_enquiry)],
                CONFIRM_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm_details)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            per_message=False
        )

        self.app.add_handler(conv_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation with Kelvin's introduction."""
        await update.message.reply_text(
            "Hi! I am Kelvin from OCBC mortgage, how do I address you? 😊"
        )
        return INITIAL_NAME

    async def get_initial_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get user's name and ask how to help with overseas loan."""
        context.user_data['user_name'] = update.message.text
        await update.message.reply_text(
            f"Nice to meet you, {context.user_data['user_name']}! How can I help you with the overseas loan? 🏠"
        )
        return INITIAL_QUESTION

    async def handle_initial_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the user's initial question and offer to connect with a colleague."""
        user_question = update.message.text
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are Kelvin, an OCBC mortgage specialist. Provide helpful and friendly responses about OCBC overseas property loans."},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.7
            )
            await update.message.reply_text(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            await update.message.reply_text(
                "I apologize, but I'm having trouble providing specific information about that right now. 😕"
            )

        # Ask if they want to be contacted
        await update.message.reply_text(
            "Would you like my colleague to reach out to you for more detailed information? (Yes/No)"
        )
        return ASK_FOR_CONTACT

    async def ask_for_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle whether the user wants to be contacted."""
        response = update.message.text.lower()
        if response in ['yes', 'y', 'sure', 'okay']:
            # Create salutation buttons
            keyboard = [[InlineKeyboardButton(option, callback_data=option)] 
                       for option in SALUTATION_OPTIONS]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Please select your salutation:",
                reply_markup=reply_markup
            )
            return SALUTATION
        else:
            await update.message.reply_text(
                "No problem! Feel free to ask me any other questions about OCBC overseas property loans. "
                "You can also start a new conversation anytime with /start"
            )
            return ConversationHandler.END

    async def salutation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store salutation and ask for full name."""
        query = update.callback_query
        await query.answer()
        context.user_data['salutation'] = query.data
        
        await query.message.reply_text(
            f"Great! Could you please share your full name?"
        )
        return FULL_NAME

    async def full_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store full name and ask for contact number."""
        context.user_data['full_name'] = update.message.text
        await update.message.reply_text(
            f"Nice to meet you, {context.user_data['full_name']}! 😊\n\n"
            "Could you please share your contact number? 📱\n"
            "Please include your country code (e.g., +65xxxxxxxx)"
        )
        return CONTACT

    async def contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Validate and store contact number, then ask for email."""
        contact_number = update.message.text
        
        if not PHONE_PATTERN.match(contact_number):
            await update.message.reply_text(
                "❌ Oops! That doesn't look like a valid phone number.\n\n"
                "Please make sure to:\n"
                "• Start with '+' symbol\n"
                "• Include only numbers after the '+'\n"
                "Example: +6591234567"
            )
            return CONTACT
            
        context.user_data['contact'] = contact_number
        await update.message.reply_text(
            "Great! 👍 Now, what's your email address? 📧\n"
            "Please provide a valid email ending with .com"
        )
        return EMAIL

    async def email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Validate and store email, then ask for best time to contact."""
        email = update.message.text
        
        if not EMAIL_PATTERN.match(email):
            await update.message.reply_text(
                "❌ Hmm, that email address doesn't look quite right.\n\n"
                "Please make sure:\n"
                "• It contains '@'\n"
                "• It ends with '.com'\n"
                "Example: name@example.com"
            )
            return EMAIL
            
        context.user_data['email'] = email
        
        # Create best time buttons
        keyboard = [[InlineKeyboardButton(option, callback_data=option)] 
                   for option in BEST_TIME_OPTIONS]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Perfect! 🎯\n\n"
            "When would be the best time for our representative to contact you? ⏰",
            reply_markup=reply_markup
        )
        return BEST_TIME

    async def best_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store best time and ask for nature of enquiry."""
        query = update.callback_query
        await query.answer()
        context.user_data['best_time'] = query.data

        keyboard = [[InlineKeyboardButton(option, callback_data=option)]
                   for option in NATURE_ENQUIRY_OPTIONS]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "Got it! 📝\n\n"
            "What's the nature of your enquiry? 🤔",
            reply_markup=reply_markup
        )
        return NATURE_ENQUIRY

    async def nature_enquiry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store nature of enquiry and show confirmation."""
        query = update.callback_query
        await query.answer()
        context.user_data['nature_enquiry'] = query.data

        # Format the confirmation message
        confirmation = (
            "🔍 Here's a summary of your details:\n\n"
            f"👤 Salutation: {context.user_data['salutation']}\n"
            f"👤 Name: {context.user_data['full_name']}\n"
            f"📱 Contact: {context.user_data['contact']}\n"
            f"📧 Email: {context.user_data['email']}\n"
            f"⏰ Best Time: {context.user_data['best_time']}\n"
            f"📋 Nature of Enquiry: {context.user_data['nature_enquiry']}\n\n"
            "🔗 Form Reference: https://www.ocbc.com/personal-banking/forms/overseas-property-loan-enquiry\n\n"
            "Please type:\n"
            "• 'submit' to proceed with submission\n"
            "• 'edit' to modify your details\n"
            "• 'cancel' to start over"
        )

        await query.message.reply_text(confirmation)
        return CONFIRM_DETAILS

    async def submit_form(self, user_data: dict) -> str:
        """Fill the form using Playwright with human-like behavior based on recorded interactions."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                )
                
                page = await context.new_page()
                
                # Enable debug logging
                page.on("console", lambda msg: logger.info(f"Browser console: {msg.text}"))
                page.on("pageerror", lambda err: logger.error(f"Browser error: {err}"))
                
                # Navigate to the form
                logger.info("Navigating to form...")
                await page.goto(OCBC_FORM_URL)
                
                # Wait for the page to be fully loaded
                logger.info("Waiting for page to be fully loaded...")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(5000)  # Increased wait time for dynamic content
                
                # Wait for form to be ready
                logger.info("Waiting for form to be ready...")
                await page.wait_for_selector('form', state='visible', timeout=10000)
                
                # Scroll the page slowly to simulate reading
                logger.info("Scrolling through the page...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await page.wait_for_timeout(1000)
                
                # Select salutation
                logger.info(f"Selecting salutation: {user_data['salutation']}")
                try:
                    # Try to find the radio button by role and label
                    salutation_radio = f'//input[@type="radio"][@value="{user_data["salutation"]}"]'
                    await page.wait_for_selector(salutation_radio, timeout=5000)
                    await page.click(salutation_radio)
                except Exception as e:
                    logger.error(f"Failed to select salutation: {str(e)}")
                    # Try alternative selector
                    try:
                        await page.evaluate(f"""
                            const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
                            const radio = radios.find(r => r.value === '{user_data["salutation"]}');
                            if (radio) radio.click();
                        """)
                    except Exception as e:
                        logger.error(f"Alternative salutation selection failed: {str(e)}")
                
                await page.wait_for_timeout(1000)
                
                # Fill in full name
                logger.info(f"Entering full name: {user_data['full_name']}")
                try:
                    # Try to find the name input by placeholder or label
                    name_input = '//input[contains(@placeholder, "name") or contains(@aria-label, "name")]'
                    await page.wait_for_selector(name_input, timeout=5000)
                    await page.click(name_input)
                    await page.fill(name_input, "")
                    await page.type(name_input, user_data['full_name'], delay=100)
                except Exception as e:
                    logger.error(f"Failed to enter name: {str(e)}")
                
                await page.wait_for_timeout(1000)
                
                # Fill in contact number
                logger.info(f"Entering contact number: {user_data['contact']}")
                try:
                    # Try to find the contact input by type or placeholder
                    contact_input = '//input[@type="tel" or contains(@placeholder, "contact") or contains(@placeholder, "phone")]'
                    await page.wait_for_selector(contact_input, timeout=5000)
                    await page.click(contact_input)
                    await page.fill(contact_input, "")
                    await page.type(contact_input, user_data['contact'], delay=100)
                except Exception as e:
                    logger.error(f"Failed to enter contact: {str(e)}")
                
                await page.wait_for_timeout(1000)
                
                # Fill in email
                logger.info(f"Entering email: {user_data['email']}")
                try:
                    # Try to find the email input by type or placeholder
                    email_input = '//input[@type="email" or contains(@placeholder, "email")]'
                    await page.wait_for_selector(email_input, timeout=5000)
                    await page.click(email_input)
                    await page.fill(email_input, "")
                    await page.type(email_input, user_data['email'], delay=100)
                except Exception as e:
                    logger.error(f"Failed to enter email: {str(e)}")
                
                await page.wait_for_timeout(1000)
                
                # Handle Select2 dropdowns
                async def handle_select2(field_name: str, value: str):
                    logger.info(f"Handling {field_name} selection: {value}")
                    try:
                        # Find the Select2 container
                        select_container = f'//label[contains(text(), "{field_name}")]/following::div[contains(@class, "select2-container")]'
                        await page.wait_for_selector(select_container, timeout=5000)
                        
                        # Click to open dropdown
                        await page.click(select_container)
                        await page.wait_for_timeout(1000)
                        
                        # Try to find and click the option
                        option = f'//li[contains(@class, "select2-results__option") and contains(text(), "{value}")]'
                        await page.wait_for_selector(option, timeout=5000)
                        await page.click(option)
                        
                    except Exception as e:
                        logger.error(f"Failed to select {field_name}: {str(e)}")
                        try:
                            # Try alternative method using JavaScript
                            await page.evaluate("""(fieldName, value) => {
                                const select = document.querySelector(`select:has(option:contains("${value}"))`);
                                if (select) {
                                    const option = Array.from(select.options).find(opt => opt.text.includes(value));
                                    if (option) {
                                        select.value = option.value;
                                        select.dispatchEvent(new Event('change', { bubbles: true }));
                                        if (window.jQuery) {
                                            jQuery(select).trigger('change.select2');
                                        }
                                    }
                                }
                            }""", field_name, value)
                        except Exception as e:
                            logger.error(f"Alternative selection for {field_name} failed: {str(e)}")
                
                # Select best time to contact
                await handle_select2("best time", user_data['best_time'])
                await page.wait_for_timeout(1000)
                
                # Select nature of enquiry
                await handle_select2("nature of enquiry", user_data['nature_enquiry'])
                await page.wait_for_timeout(1000)
                
                # Take a screenshot for verification
                logger.info("Taking verification screenshot...")
                screenshots_dir = Path("form_screenshots")
                screenshots_dir.mkdir(exist_ok=True)
                screenshot_path = str(screenshots_dir / f"form_filled_{int(time.time())}.png")
                await page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved to: {screenshot_path}")
                
                # Get the current URL with form data
                filled_url = page.url
                logger.info(f"Form URL: {filled_url}")
                
                # Keep the browser open longer to show the filled form
                await page.wait_for_timeout(10000)
                
                await browser.close()
                return filled_url

        except Exception as e:
            logger.error(f"Form filling error: {str(e)}")
            return None

    async def confirm_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user's confirmation response."""
        user_response = update.message.text.lower()
        
        if user_response == 'submit':
            # Fill form and get pre-filled URL
            prefilled_url = await self.submit_form(context.user_data)
            
            if prefilled_url:
                await update.message.reply_text(
                    "✅ Great! I've prepared your form submission.\n\n"
                    f"🔗 Click here to review and submit your details:\n{prefilled_url}\n\n"
                    "The form has been pre-filled with your information. Please review and submit it on the OCBC website.\n\n"
                    "Feel free to ask me any questions about OCBC overseas property loans! 💬"
                )
            else:
                await update.message.reply_text(
                    "I apologize, but I'm having trouble accessing the form. "
                    "Please try again or contact OCBC directly at +65 6363 3333."
                )
            return ConversationHandler.END
            
        elif user_response == 'edit':
            await update.message.reply_text(
                "No problem! Let's update your information. 📝\n\n"
                "Please enter your full name again:"
            )
            return FULL_NAME
            
        elif user_response == 'cancel':
            await update.message.reply_text(
                "Form submission cancelled. You can start over anytime with /start 🔄"
            )
            return ConversationHandler.END
            
        else:
            await update.message.reply_text(
                "🤔 I didn't quite get that.\n\n"
                "Please type:\n"
                "• 'submit' to proceed\n"
                "• 'edit' to make changes\n"
                "• 'cancel' to start over"
            )
            return CONFIRM_DETAILS

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        await update.message.reply_text(
            "Form submission cancelled. You can start over anytime with /start 🔄"
        )
        return ConversationHandler.END

    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user questions using GPT-4."""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in OCBC overseas property loans. Provide clear, accurate, and friendly responses."},
                    {"role": "user", "content": update.message.text}
                ],
                temperature=0.7
            )
            await update.message.reply_text(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            await update.message.reply_text(
                "I'm having trouble processing your question right now. 😕\n"
                "Please try again later or contact OCBC directly for immediate assistance."
            )

    def run(self):
        """Run the bot."""
        self.app.run_polling()

if __name__ == "__main__":
    bot = OCBCLoanBot()
    bot.run() 