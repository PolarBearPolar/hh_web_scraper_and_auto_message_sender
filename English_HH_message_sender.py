import re, requests, bs4, time, psycopg2, os, pyperclip
import pyautogui as pa
import pandas as pd

# Adding values to postgresql database            
def postgres_to_pandas():
    global dbname, user, password, host
    
    # Connecting to postgres database
    conn = psycopg2.connect(dbname = dbname, user= user, password = password, host = host)
    cur = conn.cursor()
    # Getting all unsent messages
    sql_inquiry = r'SELECT * FROM Prospect_Customers WHERE email_status IS NULL'    
    cur.execute(sql_inquiry)
    rows = cur.fetchall()

    cur.close()
    columns = [i[0] for i in cur.description]
    conn.close()
    return pd.DataFrame(rows, columns=columns)
            
# Adding values to postgresql database            
def updating_row_postgres(employer_id, email):
    global df, dbname, user, password, host
    
    # Adding values to postgresql database
    conn = psycopg2.connect(dbname = dbname, user= user, password = password, host = host)
    cur = conn.cursor()
    
    sql_inquiry = '''UPDATE Prospect_Customers SET email_status = 'sent' WHERE employer_id = %s AND email = %s;'''    
    cur.execute(sql_inquiry,(employer_id, email))

    conn.commit()
    cur.close()
    conn.close()
    
    
# Sending message.
def sending_message(employer_id, email):
    global body
    # Locating Compose button and clicking it
    pa.hotkey('win', 'up')
    compose_button = r'C:\Users\User\Desktop\Python\EnglishBro\pyautogui\Compose.png'
    error = r'C:\Users\User\Desktop\Python\EnglishBro\pyautogui\Error.png'
    while not pa.locateOnScreen(compose_button):
        time.sleep(sleep_time)
        print('Open your Google account')
        if error:
            pa.typewrite(['enter'])
    pa.click(pa.locateOnScreen(compose_button))
    
    # Writing and sending a message.
    time.sleep(sleep_time*2)
    pa.write(email)
    pa.press(['enter', '\t'], interval = 1)
    pyperclip.copy('English Coach для Вашей компании')
    pa.hotkey('ctrl', 'v')
    pa.press(['\t'])
    pyperclip.copy(body)
    pa.hotkey('ctrl', 'v')
    pa.typewrite(['\t']+['enter'], interval = button_interval)
    time.sleep(sleep_time)
    updating_row_postgres(int(employer_id), email)

    # Setting up the path.
work_dir = r'C:\Users\User\Desktop\Python\EnglishBro'
os.chdir(work_dir)

# Connecting to postgresql database
dbname = "English_HH"
user = "postgres"
password = input("Enter the password: ")
host = "localhost"

# Setting up time intervals.
sleep_time = 5
pa.PAUSE = 1
button_interval = 0.75
count_mes_sent = 0

# Setting up body of message
body = "Your message"

df = postgres_to_pandas()

# Sending messages
for i in df.index:
    sending_message(df['employer_id'][i], df['email'][i])
    pa.moveRel(0, 150)