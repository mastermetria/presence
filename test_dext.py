import requests
import os
import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome  import ChromeDriverManager

if '__main__' == __name__ :
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

