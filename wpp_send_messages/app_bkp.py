from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import urllib
import time
import os

service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
browser = webdriver.Chrome(service=service, options=options)

df = pd.read_csv('clients.csv')

list_send_success = []
lista_send_failure = []
for i in df.index:
    name = df.loc[i, 'name']
    message = df.loc[i, 'message']
    file = df.loc[i, 'file']
    phone = df.loc[i, 'phone']

    text = message.replace("fulano", name)
    text = urllib.parse.quote(text)

    url = f"https://web.whatsapp.com/send?phone={phone}&text={text}"
    browser.get(url)
    while len(browser.find_elements(By.ID, 'side')) < 1:
        time.sleep(1)
    time.sleep(2)

    # verificar se numero invalido
    xpath_error = ('//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/'
                   'div[1]')
    if len(browser.find_elements(By.XPATH, xpath_error)) < 1:
        xpath_enter = ('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/'
                       'div[2]/button/span')
        browser.find_element(By.XPATH, xpath_enter).click()

        if file != "N":
            # caminho completo anexo
            full_path = os.path.abspath(file)

            # xpath botao anexar
            xpath_attach = ('//*[@id="main"]/footer/div[1]/div/span[2]/div/'
                            'div[1]/div[2]/div/div/div/span')
            browser.find_element(By.XPATH, xpath_attach).click()

            # xpath opcao documento
            xpath_document = ('//*[@id="main"]/footer/div[1]/div/span[2]/div/'
                              'div[1]/div[2]/div/span/div/ul/div/div[1]/li/'
                              'div/input')
            browser.find_element(By.XPATH, xpath_document).send_keys(
                full_path)

            # tempo carregar anexo
            time.sleep(8)

            # xpath botao enviar anexo
            xpath_send = ('//*[@id="app"]/div/div[2]/div[2]/div[2]/span/div/'
                          'div/div/div[2]/div/div[2]/div[2]/div/div/span')
            browser.find_element(By.XPATH, xpath_send).click()

        list_send_success.append({
            'name': name,
            'phone': phone
        })
    else:
        lista_send_failure.append({
            'name': name,
            'phone': phone
        })

    time.sleep(2)

print('---------------------------------------------')
print('Sent successfully:')
print('---------------------------------------------')
print(list_send_success)

print('---------------------------------------------')
print('Not sent successfully:')
print('---------------------------------------------')
print(lista_send_failure)
