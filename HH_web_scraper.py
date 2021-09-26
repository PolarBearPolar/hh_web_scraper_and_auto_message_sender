import re, requests, bs4, time, psycopg2
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Adding values to pandas dataframe
def add_values():
    global df
    regex = re.compile('\d+')
    vacs_dic = {'employer_id':[], 'employer_name':[], 'vacancy':[], 'link':[]}  
    search_res = driver.find_elements_by_class_name("vacancy-serp-item")#"vacancy-serp-item.vacancy-serp-item_premium")
    for vac in search_res:
        # Looking for information on webpage
        try:
            vac_name = vac.find_element_by_css_selector('a[data-qa="vacancy-serp__vacancy-title"]').text
        except:
            vac_name = None
        try:
            vac_link = vac.find_element_by_css_selector('a[data-qa="vacancy-serp__vacancy-title"]').get_attribute("href")
        except:
            vac_link = None
        try:
            emp_name = vac.find_element_by_css_selector('a[data-qa="vacancy-serp__vacancy-employer"]').text
        except:
            emp_name = None
        try:
            emp_id = int(regex.search(vac.find_element_by_css_selector('a[data-qa="vacancy-serp__vacancy-employer"]').get_attribute("href")).group())
        except:
            emp_id = None
        # Saving info to a dictionary
        try:
            vacs_dic['employer_id'] += [emp_id]
            vacs_dic['employer_name'] += [emp_name]
            vacs_dic['vacancy'] += [vac_name]
            vacs_dic['link'] += [vac_link]
        except:
            vacs_dic['employer_id'] = [emp_id]
            vacs_dic['employer_name'] = [emp_name]
            vacs_dic['vacancy'] = [vac_name]
            vacs_dic['link'] = [vac_link]
     
    # Looping through vacancies
    for i in range(len(vacs_dic['link'])):
        driver_2.get(vacs_dic['link'][i])
        # Checking if there is contact button
        try:
            button = driver_2.find_element_by_css_selector("button.bloko-button.bloko-button_stretched.bloko-button_appearance-outlined")
            button.click()
            time.sleep(3)
            contact_info = WebDriverWait(driver_2, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.vacancy-contacts__body'))
                )
            # Checking if there is hr manager name
            try:
                fio = contact_info.find_element_by_css_selector('p[data-qa="vacancy-contacts__fio"]').text
            except:
                fio = None
            # Checking if there is phone number
            try:
                phone = contact_info.find_element_by_css_selector('p[data-qa="vacancy-contacts__phone"]').text
            except:
                phone = None
            # Checking if there is email address
            try:
                email = contact_info.find_element_by_css_selector('a[data-qa="vacancy-contacts__email"]').text
            except:
                continue

            # Adding values to pandas dataframe
            new_row = {'employer_id':vacs_dic['employer_id'][i],'employer_name':vacs_dic['employer_name'][i],
                       'vacancy':vacs_dic['vacancy'][i],'hr_manager':fio,'phone':phone,'email':email}
            df=df.append(new_row, ignore_index = True)
        except:
            continue
            
# Adding values to postgresql database            
def add_values_to_postgres(employer_id, employer_name, vacancy, hr_manager, phone,email):
    global df, dbname, user, password, host
    
    # Adding values to postgresql database
    conn = psycopg2.connect(dbname = dbname, user= user, password = password, host = host)
    cur = conn.cursor()
    
    sql_inquiry = r'INSERT INTO Prospect_Customers(employer_id, employer_name, vacancy, hr_manager, phone, email) VALUES (%s,%s,%s,%s,%s,%s);'    
    cur.execute(sql_inquiry,(employer_id, employer_name, vacancy, hr_manager, phone, email))

    conn.commit()
    cur.close()
    conn.close()

# Creating pandas dataframe
df = pd.DataFrame(columns=['employer_id','employer_name','vacancy','hr_manager',
                           'phone','email'])

# First webdriver for search result pages
path = r'C:\Users\User\AppData\Local\Programs\Python\Python39\chromedriver.exe'
driver = webdriver.Chrome(path)
driver.maximize_window()
# Defining first page and search inquiry
link = 'https://petrozavodsk.hh.ru/search/vacancy?clusters=true&ored_clusters=true&enable_snippets=true&st=searchVacancy&text=%28%D0%90%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9+OR+English%29+NOT+%D0%A3%D1%87%D0%B8%D1%82%D0%B5%D0%BB%D1%8C+NOT+%D0%9F%D1%80%D0%B5%D0%BF%D0%BE%D0%B4%D0%B0%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C+NOT+%D0%9F%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4%D1%87%D0%B8%D0%BA+NOT+%D0%A0%D0%B5%D0%BF%D0%B5%D1%82%D0%B8%D1%82%D0%BE%D1%80+NOT+Teacher+NOT+Tutor&area=113'
driver.get(link)

# Second webdriver for every vacancy
# Verification - step 1
driver_2 = webdriver.Chrome(path)
driver_2.get('https://petrozavodsk.hh.ru/account/login')
login = driver_2.find_element_by_css_selector('input[data-qa="account-signup-email"]')
login.send_keys('filippov.ilia.1991@gmail.com')
login_button = driver_2.find_element_by_css_selector('button[data-qa="account-signup-submit"]')
login_button.click()
time.sleep(2)
# Verification - step 2
verif = driver_2.find_element_by_css_selector('input[data-qa="otp-code-input"]')
verif.send_keys(input('Enter verification code: '))
verif_button = driver_2.find_element_by_css_selector('button[data-qa="otp-code-submit"]')
verif_button.click()
time.sleep(2)

# Connecting to postgresql database
dbname = "English_HH"
user = "postgres"
password = input("Enter the password: ")
host = "localhost"

# Adding values
add_values()
while len(df.index) < 1000:
    try:
        next_button = driver.find_element_by_css_selector('a[data-qa="pager-next"]')
        next_button.click()
        time.sleep(3)
        add_values()
        print(f'{len(df.index)} values have been added to the pandas table')
    except:
        break
    
# Saving distinct results to postgresql
df = df.drop_duplicates(subset=['employer_id', 'email'], keep='first').reset_index(drop=True)
for i in df.index:
    try:
        add_values_to_postgres(df['employer_id'][i], df['employer_name'][i],
                        df['vacancy'][i], df['hr_manager'][i],
                        df['phone'][i], df['email'][i])
    except:
        continue