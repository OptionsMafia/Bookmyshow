from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.common.by import By # type: ignore
import time
import smtplib
from email.mime.text import MIMEText
import os

def check_for_theater(url, theater_name):
    try:
        # Set up Chrome options - optimized for speed
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--disk-cache-size=0")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(10)
        
        driver.get(url)
        
        start_time = time.time()
        max_wait = 5
        body_element = None
        
        while time.time() - start_time < max_wait:
            try:
                body_element = driver.find_element(By.TAG_NAME, 'body')
                if body_element:
                    break
            except:
                time.sleep(0.1)
        
        all_text = body_element.text if body_element else ""
        theater_exists = theater_name in all_text
        
        if not theater_exists and body_element:
            try:
                venue_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-name, .cinema-name')
                for element in venue_elements:
                    if theater_name in element.text:
                        theater_exists = True
                        break
            except:
                pass
        
        driver.quit()
        return theater_exists
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

def send_email_notification(movie, theater):
    """Send an email notification with fixed Gmail settings"""
    try:
        # Hardcoded configuration for Gmail - fixes the nodename error
        smtp_server = "smtp.gmail.com"  # Explicit server name
        smtp_port = 587
        sender_email = "mraghhav1111@gmail.com"
        recipient_email = "nav.vikraman@gmail.com"
        
        # App password (remove spaces if any)
        app_password = "goxsideamqpxmjei"
        
        # Create message
        msg = MIMEText(f"Booking opened for {movie} at {theater}! Check BookMyShow now.")
        msg['Subject'] = f"🎬 BookMyShow Alert: {movie} at {theater}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        
        # Connect with explicit timeout and error handling
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            print("SMTP connection established")
            
            # Start TLS for security
            server.starttls()
            print("TLS started")
            
            # Authentication
            server.login(sender_email, app_password)
            print("Login successful")
            
            # Send email
            server.send_message(msg)
            print("Message sent")
            
            # Quit server
            server.quit()
            print(f"Email notification sent to {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("Authentication failed. Please check your username and app password.")
            return False
        except smtplib.SMTPConnectError:
            print("Failed to connect to the SMTP server. Check your internet connection.")
            return False
        except smtplib.SMTPServerDisconnected:
            print("Server disconnected unexpectedly.")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP error occurred: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def main():
    # Configuration
    url = "https://in.bookmyshow.com/buytickets/good-bad-ugly-chennai/movie-chen-ET00431346-MT/20250410"
    theater_name = "Sathyam"  # Change this as needed
    movie_name = "Good Bad Ugly"
    
    # Check interval in seconds (e.g., check every 15 minutes)
    check_interval = 60
    
    print(f"\nStarting BookMyShow theater checker for {theater_name}")
    print(f"Checking every {check_interval/60} minutes...")
    print(f"Email notifications will be sent to: mraghhav1111@gmail.com")
    
    while True:
        start = time.time()
        result = check_for_theater(url, theater_name)
        end = time.time()
        
        if result is True:
            print(f"FOUND! Theater '{theater_name}' is available for '{movie_name}'")
            print(f"Execution time: {end - start:.2f} seconds")
            
            # Send email notification with reliable method
            send_email_notification(movie_name, theater_name)
            
            # Create a log file with the details
            with open("theater_found.txt", "w") as f:
                f.write(f"Theater '{theater_name}' found for '{movie_name}' at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL: {url}")
            
            # Break the loop once found
            break
        elif result is False:
            print(f"Not found. Theater '{theater_name}' is not available yet. ({time.strftime('%H:%M:%S')})")
            print(f"Execution time: {end - start:.2f} seconds")
        else:
            print("Failed to determine if the theater exists")
            print(f"Execution time: {end - start:.2f} seconds")
        
        # Sleep until next check
        time.sleep(check_interval)

if __name__ == "__main__":
    main()