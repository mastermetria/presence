import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome  import ChromeDriverManager
import time


#TMZU YJOR CL2P NQID

# Clé secrète brute
secret_raw = "TMZUYJORCL2PNQID"  # Remplace par ta clé réelle

totp = pyotp.TOTP(secret_raw)
code = totp.now()


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url = 'https://app.dext.com/login'

driver.get(url)

mail = driver.find_element(By.ID, "user_login_email")
mail.send_keys('admin@metria.fr')

passwd = driver.find_element(By.ID, 'user_login_password')
passwd.send_keys('metria123*')

login = driver.find_element("css selector", "input.d-button.d-button-primary[value='Se connecter']")

login.click()
time.sleep(3)
driver.quit()


