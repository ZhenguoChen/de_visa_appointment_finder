import os
import yagmail

from time import sleep
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()
URL = "https://visa.vfsglobal.com/ind/en/deu/login"
VFS_USERNAME = os.environ['VFS_USERNAME']
VFS_PASSWORD = os.environ['VFS_PASSWORD']

SENDER_EMAIL = os.environ['SENDER_EMAIL']
APP_PASSWORD = os.environ['APP_PASSWORD']
RECEIVER_EMAIL = os.environ['RECEIVER_EMAIL']


def login():
    wait = WebDriverWait(driver, 20)

    wait.until(EC.title_contains('Login'))

    # reject all cookies
    wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

    # fill up username & pwd in the text fields
    email_elem = driver.find_element_by_id('mat-input-0')
    email_elem.send_keys(VFS_USERNAME)

    pwd_elem = driver.find_element_by_id('mat-input-1')
    pwd_elem.send_keys(VFS_PASSWORD)

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-button-wrapper')))

    # wait for sometime before clicking the sign in button
    sleep(2)

    sign_in_button = driver.find_element_by_class_name('mat-button-wrapper')
    sign_in_button.click()


def go_to_homepage():
    # it's not possible to refresh the page. So, click on the top left VFS Global image to go to homepage
    home_elem = driver.find_element_by_xpath('/html/body/app-root/header/div[1]/div/a/img')
    home_elem.click()
    sleep(3)


def find_appointment_info():
    global driver, n
    sleep(5)
    wait = WebDriverWait(driver, 20)
    # new booking
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.d-none > span:nth-child(1)'))).click()

    # choose New Delhi
    sleep(2)
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="mat-select-value-{n}"]'))).click()
    driver.find_elements_by_class_name('mat-option-text')[12].click()

    n += 2
    # schengen visa
    sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="mat-select-value-{n}"]'))).click()
    driver.find_elements_by_class_name('mat-option-text')[-1].click()

    n += 2

    # family & friends
    sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="mat-select-value-{n}"]'))).click()
    driver.find_elements_by_class_name('mat-option-text')[-1].click()

    n += 2

    sleep(3)

    # grab appointment info from the alert box
    alert_box = driver.find_element_by_css_selector('.alert')
    text = alert_box.text

    return text


def send_email(text):
    subject = 'UK VISA Appointment vacancy alert'
    content = [f'Appointment for UK VISA: {text}']

    with yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD) as yag:
        yag.send(RECEIVER_EMAIL, subject, content)


if __name__ == "__main__":
    STATUS = False
    # restart the service if it crashes unexpectedly and stop finally when the appointment is found. 
    while True:
        if STATUS: break
        try:
            driver = webdriver.Firefox()
            driver.get(URL)

            login()
            sleep(5)

            # for some reason, the select value keeps incrementing by 2 for every selection. So, keep track of it with `n`
            n = 1

            while True:
                text = find_appointment_info()
                if text.startswith('No appointment'):
                    go_to_homepage()
                else:
                    send_email(text)
                    STATUS = True
                    break
        except Exception as e:
            print(f'error encountered: {e}')
        finally:        
            driver.quit()