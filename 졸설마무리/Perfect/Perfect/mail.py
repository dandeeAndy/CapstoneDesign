import smtplib, ssl
from email.mime.text import MIMEText
import pandas as pd
from datetime import datetime, timedelta

my_account = 'hjm00105@naver.com'
my_password = 'ojlg0010605$!'

excel_path = 'C:\\Users\\Lee\\Shawn\\Capstone\\Perfect\\QR_Data\\qr_data.xlsx'  # 엑셀 파일 경로 설정

def send_email(msg):
    server = smtplib.SMTP('smtp.naver.com', 587)
    server.starttls()
    server.login(my_account, my_password)
    server.send_message(msg)
    server.quit()

def make_mime_text(mail_to, subject, body):
    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['To'] = mail_to
    msg['From'] = my_account
    return msg

def send_logitics_data():
    base_time = datetime.strptime('17:00', '%H:%M')

    for sheet_name in ['Position A', 'Position B']:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        # 'Position' 열을 기준으로 내림차순 정렬
        df_sorted = df.sort_values(by='Position', ascending=False)
        email_addresses = df_sorted['Email'].tolist()

        for i, email in enumerate(email_addresses):
            appointment_time = base_time + timedelta(minutes=10 * i)
            body = f"{{'안녕하세요. JALK3 입니다. 해당 화물의 분류가 완료 되었습니다.'}}{appointment_time.strftime('%H:%M')}에 오시면 되겠습니다. 감사합니다."
            msg = make_mime_text(mail_to=email, subject='이승호', body=body)
            send_email(msg)
            print(f"{appointment_time.strftime('%H:%M')}에 오세요 - {email}로 이메일 전송 완료")


