"""
Website Screenshot Capture Module
Captures screenshots of websites for UX analysis
"""

import os
import tempfile
import time
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class WebsiteCapture:
    def __init__(self):
        """Initialize the website capture with Chrome driver"""
        self.driver = None
        
    def _setup_driver(self, mobile: bool = False) -> webdriver.Chrome:
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        
        if mobile:
            # Mobile viewport
            chrome_options.add_argument('--window-size=375,812')
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        else:
            # Desktop viewport
            chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            # Use webdriver-manager to automatically manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            raise Exception(f"Failed to setup Chrome driver: {str(e)}")
    
    def capture_website(self, url: str, mobile: bool = False, wait_time: int = 5) -> Optional[str]:
        """
        Capture a screenshot of a website
        
        Args:
            url: Website URL to capture
            mobile: Whether to capture mobile view
            wait_time: Time to wait for page load
            
        Returns:
            Path to the captured screenshot file, or None if failed
        """
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Setup driver
            self.driver = self._setup_driver(mobile=mobile)
            
            # Navigate to URL
            print(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(wait_time)
            
            # Wait for body element to be present
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                print("Warning: Page may not have loaded completely")
            
            # Get page dimensions and scroll to capture full page
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Set window size to capture full page
            self.driver.set_window_size(1920 if not mobile else 375, total_height)
            time.sleep(2)  # Allow time for resize
            
            # Create temporary file for screenshot
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            screenshot_path = temp_file.name
            temp_file.close()
            
            # Capture screenshot
            success = self.driver.save_screenshot(screenshot_path)
            
            if success and os.path.exists(screenshot_path):
                print(f"Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                print("Failed to save screenshot")
                return None
                
        except WebDriverException as e:
            print(f"WebDriver error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error capturing website: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def capture_both_views(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Capture both desktop and mobile views of a website
        
        Returns:
            Tuple of (desktop_screenshot_path, mobile_screenshot_path)
        """
        desktop_path = self.capture_website(url, mobile=False)
        mobile_path = self.capture_website(url, mobile=True)
        
        return desktop_path, mobile_path
    
    def cleanup_screenshot(self, screenshot_path: str):
        """Clean up temporary screenshot file"""
        try:
            if screenshot_path and os.path.exists(screenshot_path):
                os.unlink(screenshot_path)
        except Exception as e:
            print(f"Error cleaning up screenshot: {e}")

# Test function
def test_capture():
    """Test website capture functionality"""
    capture = WebsiteCapture()
    
    # Test with a simple website
    test_url = "https://example.com"
    print(f"Testing website capture with: {test_url}")
    
    screenshot_path = capture.capture_website(test_url)
    
    if screenshot_path:
        print(f"✅ Screenshot captured successfully: {screenshot_path}")
        print(f"File size: {os.path.getsize(screenshot_path)} bytes")
        
        # Clean up
        capture.cleanup_screenshot(screenshot_path)
        print("✅ Cleanup completed")
    else:
        print("❌ Screenshot capture failed")

if __name__ == "__main__":
    test_capture()

