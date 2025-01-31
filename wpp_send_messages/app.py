from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import urllib
import time
import os
from quickstart import main

service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
browser = webdriver.Chrome(service=service, options=options)

# df = pd.read_csv('clients.csv')
df, clients_send, month, year = main()

list_send_success = []
lista_send_failure = []


for i in clients_send:
    row = df[df['document'] == i['document']]
    name = row.name.iloc[0]
    message = row.message.iloc[0]
    link = i['link']
    phone = row.phone.iloc[0]

    text = (message
            .replace("<name>", name)
            .replace("<month>", month)
            .replace("<year>", year)
            .replace("<link>", link))
    text = urllib.parse.quote(text)
    text = text.replace("%7C", "\n")

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
