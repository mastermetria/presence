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




def close_all_except_first(driver):
    # Sauvegarder la première fenêtre (tabulation)
    first_window = driver.window_handles[0]

    # Parcourir toutes les fenêtres sauf la première et les fermer
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()

    # Revenir à la première fenêtre
    driver.switch_to.window(first_window)

def login(user, passwd, driver):
    ## DEXT LOGIN
    url = "https://app.dext.com/fr/login"


    ##
    url = 'https://afpro1.isp-online.net/procurement/isp_invoice.nsf/xspSearch.xsp'
    driver.get(url)

    username_input = driver.find_element(By.ID, "Username")
    username_input.send_keys(user)

    password_input = driver.find_element(By.ID, 'Password')
    password_input.send_keys(passwd)

    login_button = driver.find_element(By.ID, 'login')
    login_button.click()
    
def run (pdf_name) :
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Activer le mode headless
    # chrome_options.binary_location ='automations/bin/chrome-linux64/chrome'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    if not os.path.isdir('automations/a1/downloads/'):
        os.mkdir('automations/a1/downloads')
    
    # ex document_number'130-70007572'
    document_number = tuple(pdf_name.split('-'))
    base_url = 'https://afpro1.isp-online.net'

    login('sanso', 'KAhRGyeJ6GG9Df', driver)

    ###########################################################################################################
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.ID, 'view:_id1:_id56:InvoiceNumber'))
    )
    root_window = driver.current_window_handle
    assert len(driver.window_handles) == 1

    while True :
        invoice_number_input = driver.find_element(By.ID, 'view:_id1:_id56:InvoiceNumber')
        invoice_number_input.clear()
        invoice_number_input.send_keys('-'.join(document_number))

        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.ID, 'view:_id1:_id56:userEventSearch'))
        )
        search_button = driver.find_element(By.ID, 'view:_id1:_id56:userEventSearch')
        search_button.click()
        driver.switch_to.window(driver.window_handles[-1])
        try :
            WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.ID, 'view:_id1:_id3:_id50:searchResults:0:tr1'))
            )

            result_first_line = driver.find_element(By.ID, 'view:_id1:_id3:_id50:searchResults:0:tr1')
            result_first_line.click()
            driver.switch_to.window(driver.window_handles[-1])
        
            try:
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'embed'))
                )

                embed_element = driver.find_element(By.TAG_NAME, 'embed')
                pdf_path = embed_element.get_attribute('src')
                response = requests.get(pdf_path)
                with open(f"automations/a1/downloads/{'-'.join(document_number)}.pdf", 'wb') as file:
                    file.write(response.content)

            

            except :
                pdf_path = driver.execute_script("return ISP.PDF.url;")
                response = requests.get(base_url+pdf_path)
                with open(f"automations/a1/downloads/{'-'.join(document_number)}.pdf", 'wb') as file:
                    file.write(response.content)


            close_all_except_first(driver=driver)

            document_number = (document_number[0], str(int(document_number[1])+1)) 


        except :
            break

    driver.quit()

if __name__ == '__main__' :
    run(str(130-70007446))