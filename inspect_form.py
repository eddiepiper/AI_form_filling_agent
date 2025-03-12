from playwright.sync_api import sync_playwright

def inspect_form():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Launch in non-headless mode to see the page
        page = browser.new_page()
        
        print("Navigating to form...")
        page.goto('https://www.ocbc.com/personal-banking/forms/overseas-property-loan-enquiry')
        
        # Wait for form elements to load
        page.wait_for_selector('form', timeout=10000)
        
        # Get all form elements
        form_elements = page.query_selector_all('form input, form select')
        
        print("\nForm Elements Found:")
        for element in form_elements:
            element_id = element.get_attribute('id')
            element_name = element.get_attribute('name')
            element_type = element.get_attribute('type')
            print(f"ID: {element_id}, Name: {element_name}, Type: {element_type}")
        
        # Keep browser open for 10 seconds to inspect
        page.wait_for_timeout(10000)
        browser.close()

if __name__ == "__main__":
    inspect_form() 