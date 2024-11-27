import requests
import os
import pyotp
import time
import json

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from pathlib import Path
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome  import ChromeDriverManager

from automations.decorator.logs import logs_history_factory


def add_page_with_text_to_pdf(pdf_path, document_number):
    """
    Ajoute une page en bas d'un PDF avec le texte `document_number : <document_number>`
    et sauvegarde les modifications directement dans le fichier d'entrée.

    Args:
        pdf_path (str): Chemin du fichier PDF à modifier.
        document_number (str): Numéro du document à ajouter.
    """
    # Lire le PDF d'entrée
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Copier les pages existantes dans le writer
    for page in reader.pages:
        writer.add_page(page)

    # Créer une nouvelle page avec le texte
    packet = BytesIO()
    c = canvas.Canvas(packet)
    text = f"document_number : {document_number}"
    c.drawString(100, 500, text)  # Position du texte sur la page
    c.save()

    # Charger la nouvelle page créée
    packet.seek(0)
    new_pdf = PdfReader(packet)
    writer.add_page(new_pdf.pages[0])

    # Écrire le fichier PDF modifié au même emplacement
    with open(pdf_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Nouvelle page ajoutée avec le texte : {text}")

def dext_initialize(driver):
    """
    Initializes a Selenium session to log into the Dext application.

    This function performs the following actions:
    1. Generates a One-Time Password (OTP) using a TOTP secret key.
    2. Navigates to the specified URL of the Dext application.
    3. Fills in the email and password fields to log in.
    4. Automatically enters the OTP code into the corresponding input fields.
    5. Clicks the "Ignore" button after a successful login.

    Args:
        driver (selenium.webdriver.Chrome): The active Selenium WebDriver instance controlling the browser.

    Notes:
        - Ensure that `pyotp` is installed and correctly configured to generate the OTP using the provided secret key.
        - Replace the hardcoded email, password, and TOTP secret with secure, environment-specific values.
        - Verify that the "Ignore" button is present on the page after logging in to avoid potential errors.

    Returns:
        None
    """
    secret_raw = "TMZUYJORCL2PNQID"  # Remplace par ta clé réelle

    totp = pyotp.TOTP(secret_raw)
    code = totp.now()


    url = 'https://app.dext.com/delta/clients/7193833621/'

    driver.get(url)

    mail = driver.find_element(By.ID, "user_login_email")
    mail.send_keys('admin@metria.fr')

    passwd = driver.find_element(By.ID, 'user_login_password')
    passwd.send_keys('metria123*')

    login = driver.find_element(By.XPATH, "//input[@type='submit']")
    login.click()

    for i, letter in enumerate(code) :
        otp_entry = driver.find_element(By.ID, f"otp-input-cell-{i}")
        otp_entry.send_keys(letter)
    try :
        button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Ignorer']"))
        )
        button.click()
    except :
        driver.back()

def add_document_in_dext(driver: webdriver.Chrome, path: str) :
    """
    Automates the process of adding a document in the Dext application.

    This function performs the following actions:
    1. Locates and clicks the "Add Documents" button to open the document upload panel.
    2. Waits for the "Owner of the document" input field and selects a specific owner (e.g., "AFPRO FILTERS [Submitter]").
    3. Uploads a document (PDF file) using the file input field.
    4. Closes the document upload panel.

    Args:
        driver (selenium.webdriver.Chrome): The active Selenium WebDriver instance controlling the browser.


    Notes:
        - The file path `'/home/kali/Desktop/invoice.pdf'` is hardcoded and should be replaced with the actual path to the document.
        - Ensure that the "Owner of the document" dropdown contains the specified option ("AFPRO FILTERS [Submitter]").
        - The function includes static waits (`time.sleep`) to handle dynamic elements, but these can be replaced with explicit waits for better reliability.

    Returns:
        None
    """

    add_document_slide = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Ajouter des documents']"))
    )
    add_document_slide.click()

    owner_document_text_hook = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//label[text()='Propriétaire du document']"))
    )
    owner_document_input = owner_document_text_hook.find_element(By.XPATH, "./../span")
    owner_document_input.click()
    time.sleep(3)
    driver.find_element(By.XPATH, "//li[text()='AFPRO FILTERS [Submitter]']").click()

    upload_document = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    upload_document.send_keys(path)

    close_panel = driver.find_element(By.CLASS_NAME, "js-tutorial-target-close-add-documents-panel")
    time.sleep(3)
    close_panel.click()

def wait_document_is_ready(driver: webdriver.Chrome):
    """
    Waits for the document to be ready by monitoring a specific element on the page.

    This function performs the following actions:
    1. Periodically refreshes the page to check the document's status.
    2. Searches for a link with the text "En cours" on the page.
    3. Checks if the located element contains `<aside>` tags:
        - If no `<aside>` tags are found, the function exits the loop, indicating the document is ready.
        - If `<aside>` tags are present, the function waits for 5 seconds before refreshing the page again.
    4. If an error occurs (e.g., element not found), it prints an error message and pauses execution for an extended period (`time.sleep(10000)`).

    Args:
        driver (selenium.webdriver.Chrome): The active Selenium WebDriver instance controlling the browser.

    Notes:
        - This function is blocking and will not return until the document is considered ready.
        - The monitored page must contain a link with the text "En cours" and `<aside>` tags that disappear when the document is ready.
        - In the event of an error, the script enters a long wait state (`time.sleep(10000)`).

    Returns:
        None
    """
    while True :
        driver.refresh()
        try :

            loading_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='En cours']"))
            )

            if len(loading_tab.find_elements(By.TAG_NAME, "aside")) == 0 :
                break

            else : 
                time.sleep(5)    
        except :
            print("pas marché")
            time.sleep(10000)

def modify_invoice_number(driver, document_number):
    """
    Modifies the invoice number of the first document in a list.

    This function performs the following actions:
    1. Locates the table body (`<tbody>`) containing the list of invoices.
    2. Selects the first table row (`<tr>`) in the list.
    3. Finds and clicks the first link (`<a>`) within the selected row.
    4. Refreshes the page to ensure the input field is loaded.
    5. Waits for the label with the text "Numéro de facture" and locates the associated input field.
    6. Clears the current value in the input field and replaces it with the provided `document_number`.
    7. Clicks the "Retour" button to return to the previous page.

    Args:
        driver (selenium.webdriver.Chrome): The active Selenium WebDriver instance controlling the browser.
        document_number (str): The new invoice number to be entered into the input field.

    Notes:
        - Ensure that the table structure and labels in the page match the XPath expressions used in this function.
        - The function assumes that the table and input field are dynamically loaded and waits up to 10 seconds for them to appear.
        - The function refreshes the page after clicking the first link to ensure the input field is properly loaded.

    Returns:
        None
    """
    invoice_list_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//tbody"))
    )
    
    first_tr = invoice_list_container.find_element(By.XPATH, "./tr[1]")

    link = first_tr.find_element(By.XPATH, './/a[1]')

    link.click()

    time.sleep(1)

    driver.refresh()

    label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//label[text()='Numéro de facture']"))
    )

    input_field = label.find_element(By.XPATH, "../span/input")
    time.sleep(2)
    input_field.clear()
    time.sleep(2)

    input_field.send_keys(document_number)

    driver.find_element(By.XPATH, "//button[text()='Retour']").click()

def close_all_except_first_two(driver):
    # Sauvegarder les deux premières fenêtres (tabulations)
    first_two_windows = driver.window_handles[:2]

    # Parcourir toutes les fenêtres sauf les deux premières et les fermer
    for handle in driver.window_handles[2:]:
        driver.switch_to.window(handle)
        driver.close()

    # Revenir à la première ou à une des deux premières fenêtres
    driver.switch_to.window(first_two_windows[0])

def login(user, passwd, driver):


    ##
    url = 'https://afpro1.isp-online.net/procurement/isp_invoice.nsf/xspSearch.xsp'
    driver.get(url)

    username_input = driver.find_element(By.ID, "Username")
    username_input.send_keys(user)

    password_input = driver.find_element(By.ID, 'Password')
    password_input.send_keys(passwd)

    login_button = driver.find_element(By.ID, 'login')
    login_button.click()
    
@logs_history_factory(0)
def run (document_number) :
    print("start run 1 !!!!!!!!!!!!!!!!!!!!")
    chrome_options = Options()
    #chrome_options.add_argument('--headless=new')  # Activer le mode headless
    #chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    if not os.path.isdir('automations/a1/downloads/'):
        os.mkdir('automations/a1/downloads')
    
    # ex document_number'130-70007572'
    document_number = tuple(document_number.split('-'))
    base_url = 'https://afpro1.isp-online.net'
    dext_initialize(driver)

    driver.execute_script("window.open('');")
    # Passer au nouvel onglet
    driver.switch_to.window(driver.window_handles[1])

    login('sanso', 'KAhRGyeJ6GG9Df', driver)

    ###########################################################################################################
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.ID, 'view:_id1:_id56:InvoiceNumber'))
    )

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
        
            try: # try download with first pdf viewer type
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'embed'))
                )

                embed_element = driver.find_element(By.TAG_NAME, 'embed')
                pdf_path = embed_element.get_attribute('src')
                response = requests.get(pdf_path)
                with open(f"automations/a1/downloads/{'-'.join(document_number)}.pdf", 'wb') as file:
                    file.write(response.content)

            except : # try download with second pdf viewer type
                pdf_path = driver.execute_script("return ISP.PDF.url;")
                response = requests.get(base_url+pdf_path)
                with open(f"automations/a1/downloads/{'-'.join(document_number)}.pdf", 'wb') as file:
                    file.write(response.content)


            close_all_except_first_two(driver=driver) # and go to [0]
            absolute_path = Path(f'automations/a1/downloads/{'-'.join(document_number)}.pdf').resolve()
            add_page_with_text_to_pdf(absolute_path, '-'.join(document_number))

            add_document_in_dext(driver, str(absolute_path))            
            wait_document_is_ready(driver)
            modify_invoice_number(driver, '-'.join(document_number))
            document_number = (document_number[0], str(int(document_number[1])+1)) 
            driver.switch_to.window(driver.window_handles[1])

            with open('db.json', 'r') as file:
                data = json.load(file)

            data['automations'][0]['last_document_number'] = '-'.join(document_number)

            with open('db.json', 'w') as file:
                json.dump(data, file, indent=4)
            
            os.remove(absolute_path)



        except Exception as e :
            print(e)
            break

    driver.quit()




if __name__ == '__main__' :
    run("130-70007550")