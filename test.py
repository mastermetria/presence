import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome  import ChromeDriverManager
import time


#TMZU YJOR CL2P NQID

# Clé secrète brute
def initialize(driver):
        
    secret_raw = "TMZUYJORCL2PNQID"  # Remplace par ta clé réelle

    totp = pyotp.TOTP(secret_raw)
    code = totp.now()


    url = 'https://app.dext.com/login'

    driver.get(url)

    mail = driver.find_element(By.ID, "user_login_email")
    mail.send_keys('admin@metria.fr')

    passwd = driver.find_element(By.ID, 'user_login_password')
    passwd.send_keys('metria123*')

    login = driver.find_element(By.XPATH, "//input[@type='submit']")
    login.click()

    otp_entry = driver.find_element(By.ID, "otp-input-cell-0")
    otp_entry.sendKeys(secret_raw)
    otp_verify = driver.find_element(By.XPATH, "//input[@type='submit']")
    otp_verify.click()
    time.sleep(10)
if "__main__" == __name__ :
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    initialize(driver)
