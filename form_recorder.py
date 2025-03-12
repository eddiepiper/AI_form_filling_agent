from playwright.sync_api import sync_playwright
import json
import logging
import time
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FormRecorder:
    def __init__(self):
        self.interactions = []
        self.form_url = "https://www.ocbc.com/personal-banking/forms/overseas-property-loan-enquiry"
        self.session_id = int(time.time())
        self.backup_dir = Path("recorded_interactions")
        self.backup_dir.mkdir(exist_ok=True)
        self.current_file = self.backup_dir / f"form_interactions_{self.session_id}.json"
        self.backup_count = 0
        
        # Create initial empty file
        self.save_interactions(initial=True)
    
    def record_interaction(self, interaction_type, selector=None, value=None, details=None):
        """Record a user interaction with the form."""
        interaction = {
            'type': interaction_type,
            'selector': selector,
            'value': value,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.interactions.append(interaction)
        logger.info(f"Recorded interaction: {interaction}")
        
        # Save after every 5 interactions
        self.backup_count += 1
        if self.backup_count >= 5:
            self.save_interactions()
            self.backup_count = 0
    
    def save_interactions(self, initial=False):
        """Save recorded interactions to a file."""
        try:
            if initial:
                data = []
            else:
                data = self.interactions
            
            with open(self.current_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            if not initial:
                logger.info(f"Saved {len(data)} interactions to {self.current_file}")
        except Exception as e:
            logger.error(f"Error saving interactions: {str(e)}")
            # Try to save to a backup file
            backup_file = self.backup_dir / f"form_interactions_{self.session_id}_backup_{int(time.time())}.json"
            try:
                with open(backup_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved backup to {backup_file}")
            except Exception as e2:
                logger.error(f"Failed to save backup: {str(e2)}")
    
    def start_recording(self):
        """Start recording user interactions with the form."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Set up interaction listeners
            page.on("click", lambda e: self.record_interaction("click", str(e)))
            page.on("input", lambda e: self.record_interaction("input", None, None, str(e)))
            page.on("change", lambda e: self.record_interaction("change", None, None, str(e)))
            
            # Add more detailed event listeners using JavaScript
            page.add_init_script("""
                window.addEventListener('click', function(e) {
                    const element = e.target;
                    const details = {
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className,
                        type: element.type,
                        name: element.name,
                        value: element.value,
                        xpath: getXPath(element)
                    };
                    window.reportInteraction('click', details);
                }, true);

                window.addEventListener('input', function(e) {
                    const element = e.target;
                    const details = {
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className,
                        type: element.type,
                        name: element.name,
                        value: element.value,
                        xpath: getXPath(element)
                    };
                    window.reportInteraction('input', details);
                }, true);

                // Add focus and blur events
                window.addEventListener('focus', function(e) {
                    const element = e.target;
                    const details = {
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className,
                        type: element.type,
                        name: element.name,
                        xpath: getXPath(element)
                    };
                    window.reportInteraction('focus', details);
                }, true);

                window.addEventListener('blur', function(e) {
                    const element = e.target;
                    const details = {
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className,
                        type: element.type,
                        name: element.name,
                        xpath: getXPath(element)
                    };
                    window.reportInteraction('blur', details);
                }, true);

                function getXPath(element) {
                    if (element.id !== '')
                        return 'id("' + element.id + '")';
                    if (element === document.body)
                        return element.tagName;

                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element)
                            return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                            ix++;
                    }
                }
            """)
            
            # Expose function to receive events from JavaScript
            page.expose_function("reportInteraction", 
                lambda type, details: self.record_interaction(type, None, None, details))
            
            # Navigate to form
            logger.info("Navigating to form...")
            page.goto(self.form_url)
            
            # Wait for form to be fully loaded
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")
            
            # Take initial screenshot
            screenshots_dir = Path("form_screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            page.screenshot(path=str(screenshots_dir / f"form_initial_{self.session_id}.png"))
            
            logger.info("\n" + "="*50)
            logger.info("Form Recorder Started!")
            logger.info("Please interact with the form normally.")
            logger.info("Fill out all fields as you normally would.")
            logger.info("Press Ctrl+C when you're done.")
            logger.info(f"Your interactions are being saved to: {self.current_file}")
            logger.info("Screenshots will be saved to: form_screenshots/")
            logger.info("="*50 + "\n")
            
            try:
                # Keep browser open until user is done
                page.wait_for_timeout(3600000)  # 1 hour timeout
            except KeyboardInterrupt:
                logger.info("\nRecording stopped by user.")
            except Exception as e:
                logger.error(f"Recording error: {str(e)}")
            finally:
                # Take final screenshot
                try:
                    page.screenshot(path=str(screenshots_dir / f"form_final_{self.session_id}.png"))
                except Exception as e:
                    logger.error(f"Error taking final screenshot: {str(e)}")
                
                # Save final interactions
                self.save_interactions()
                
                try:
                    browser.close()
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")
                
                logger.info(f"\nRecording session completed. Total interactions: {len(self.interactions)}")
                logger.info(f"Interactions saved to: {self.current_file}")
                logger.info(f"Screenshots saved in: {screenshots_dir}/")

def main():
    logger.info("Starting form interaction recorder...")
    recorder = FormRecorder()
    recorder.start_recording()

if __name__ == "__main__":
    main() 