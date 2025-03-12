from playwright.sync_api import sync_playwright
import logging
import json
from datetime import datetime
import signal
import sys
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormAnalyzer:
    def __init__(self):
        self.requests = []
        self.form_state = {}
        self.network_data = []
        self.page = None
        self.should_exit = False
        
        # Create output directory
        self.output_dir = "form_analysis_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C by setting exit flag."""
        logger.info("\nReceived interrupt signal, preparing to save state...")
        self.should_exit = True
        
    def handle_request(self, request):
        """Record all network requests."""
        self.requests.append({
            'url': request.url,
            'method': request.method,
            'headers': request.headers,
            'post_data': request.post_data,
            'timestamp': datetime.now().isoformat()
        })
        
    def handle_response(self, response):
        """Record responses."""
        if response.request.resource_type == "xhr" or response.request.resource_type == "fetch":
            try:
                self.network_data.append({
                    'url': response.url,
                    'status': response.status,
                    'headers': response.headers,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")

    def save_current_state(self):
        """Save the current form state and analysis data."""
        try:
            # Get current form state
            self.form_state = self.page.evaluate("""() => {
                const form = document.querySelector('form');
                if (!form) return {};
                
                // Get all form elements
                const elements = Array.from(form.elements);
                const formData = {};
                
                elements.forEach(element => {
                    if (element.name) {
                        if (element.type === 'radio') {
                            if (element.checked) {
                                formData[element.name] = element.value;
                            }
                        } else if (element.type === 'select-one') {
                            formData[element.name] = {
                                value: element.value,
                                options: Array.from(element.options).map(opt => ({
                                    text: opt.text,
                                    value: opt.value,
                                    selected: opt.selected
                                }))
                            };
                        } else {
                            formData[element.name] = element.value;
                        }
                    }
                });

                // Also capture all input elements regardless of form membership
                const allInputs = document.querySelectorAll('input, select, textarea');
                const allElements = {};
                allInputs.forEach(element => {
                    const id = element.id || element.name;
                    if (id) {
                        allElements[id] = {
                            type: element.type,
                            value: element.value,
                            id: element.id,
                            name: element.name,
                            className: element.className,
                            tagName: element.tagName,
                            xpath: getXPath(element),
                            attributes: getAttributes(element)
                        };
                        if (element.type === 'radio') {
                            allElements[id].checked = element.checked;
                        }
                        if (element.type === 'select-one') {
                            allElements[id].options = Array.from(element.options).map(opt => ({
                                text: opt.text,
                                value: opt.value,
                                selected: opt.selected
                            }));
                        }
                    }
                });
                
                function getAttributes(element) {
                    const attrs = {};
                    for (let i = 0; i < element.attributes.length; i++) {
                        const attr = element.attributes[i];
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
                
                function getXPath(element) {
                    if (element.id !== '')
                        return `//*[@id="${element.id}"]`;
                    if (element === document.body)
                        return element.tagName;

                    let ix = 0;
                    let siblings = element.parentNode.childNodes;

                    for (let i = 0; i < siblings.length; i++) {
                        let sibling = siblings[i];
                        if (sibling === element)
                            return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                            ix++;
                    }
                }
                
                // Get form structure
                function getElementInfo(element) {
                    return {
                        tagName: element.tagName,
                        id: element.id,
                        name: element.name,
                        type: element.type,
                        className: element.className,
                        value: element.value,
                        checked: element.checked,
                        attributes: getAttributes(element),
                        xpath: getXPath(element),
                        children: Array.from(element.children).map(getElementInfo)
                    };
                }
                
                return {
                    formData,
                    allElements,
                    formStructure: getElementInfo(form),
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                };
            }""")
            
            # Save analysis results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save network requests
            with open(os.path.join(self.output_dir, f'form_analysis_requests_{timestamp}.json'), 'w') as f:
                json.dump(self.requests, f, indent=2)
            
            # Save form state
            with open(os.path.join(self.output_dir, f'form_analysis_state_{timestamp}.json'), 'w') as f:
                json.dump(self.form_state, f, indent=2)
            
            # Save network data
            with open(os.path.join(self.output_dir, f'form_analysis_network_{timestamp}.json'), 'w') as f:
                json.dump(self.network_data, f, indent=2)
            
            # Take a screenshot
            screenshot_path = os.path.join(self.output_dir, f'form_screenshot_{timestamp}.png')
            self.page.screenshot(path=screenshot_path)
            
            logger.info(f"\nAnalysis results saved in {self.output_dir}:")
            logger.info(f"- Requests: form_analysis_requests_{timestamp}.json")
            logger.info(f"- Form State: form_analysis_state_{timestamp}.json")
            logger.info(f"- Network Data: form_analysis_network_{timestamp}.json")
            logger.info(f"- Screenshot: form_screenshot_{timestamp}.png")
            
        except Exception as e:
            logger.error(f"Error saving state: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def analyze_form(self):
        """Analyze the form behavior."""
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            # Create a new page and set up listeners
            self.page = context.new_page()
            self.page.on("request", self.handle_request)
            self.page.on("response", self.handle_response)
            
            # Monitor form state changes
            self.page.add_init_script("""
                window.formStateChanges = [];
                const originalPushState = history.pushState;
                const originalReplaceState = history.replaceState;
                
                history.pushState = function() {
                    window.formStateChanges.push({
                        type: 'pushState',
                        arguments: Array.from(arguments),
                        timestamp: new Date().toISOString()
                    });
                    return originalPushState.apply(this, arguments);
                };
                
                history.replaceState = function() {
                    window.formStateChanges.push({
                        type: 'replaceState',
                        arguments: Array.from(arguments),
                        timestamp: new Date().toISOString()
                    });
                    return originalReplaceState.apply(this, arguments);
                };
                
                // Monitor form element changes
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes') {
                            window.formStateChanges.push({
                                type: 'attributeChange',
                                element: mutation.target.tagName,
                                attribute: mutation.attributeName,
                                value: mutation.target.getAttribute(mutation.attributeName),
                                timestamp: new Date().toISOString()
                            });
                        }
                    });
                });
                
                // Start observing once form is loaded
                document.addEventListener('DOMContentLoaded', () => {
                    const form = document.querySelector('form');
                    if (form) {
                        observer.observe(form, {
                            attributes: true,
                            childList: true,
                            subtree: true,
                            attributeOldValue: true
                        });
                    }
                });
            """)
            
            # Navigate to form
            logger.info("Navigating to form...")
            self.page.goto("https://www.ocbc.com/personal-banking/forms/overseas-property-loan-enquiry")
            
            # Wait for form to load
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_load_state("domcontentloaded")
            
            logger.info("\n" + "="*50)
            logger.info("Form Analysis Started!")
            logger.info("Please interact with the form normally.")
            logger.info("Fill out all fields as you normally would.")
            logger.info("Press Ctrl+C when you're done.")
            logger.info("="*50 + "\n")
            
            try:
                # Keep browser open for manual interaction
                while not self.should_exit:
                    time.sleep(1)  # Check exit flag every second
                    # Periodically save state
                    if len(self.requests) > 0 or len(self.network_data) > 0:
                        self.save_current_state()
            except Exception as e:
                logger.error(f"Error during analysis: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                # Save final state
                self.save_current_state()
                browser.close()

def main():
    analyzer = FormAnalyzer()
    analyzer.analyze_form()

if __name__ == "__main__":
    main() 