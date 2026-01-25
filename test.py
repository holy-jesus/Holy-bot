import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate  # <--- 1. Импортируем formatdate

smtp_server = "mail.holy-bot.ru"
smtp_port = 587
username = "noreply@holy-bot.ru"
password = "NoW3ekend4reAidCrea7ingF11edOff1cers"

msg = MIMEMultipart()
msg['From'] = username
msg['To'] = "hj@holy-coder.ru"
msg['Subject'] = "Тест с Датой и ID"
msg['Message-ID'] = make_msgid(domain='holy-bot.ru')
msg['Date'] = formatdate(localtime=True) # <--- 2. ОБЯЗАТЕЛЬНО добавляем дату

body = "Привет! Теперь у письма есть и ID, и Дата. Сервер должен его пропустить."
msg.attach(MIMEText(body, 'plain'))

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, msg['To'], msg.as_string())
    server.quit()
    print("Письмо отправлено!")
except Exception as e:
    print(f"Ошибка: {e}")
