import os
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dotenv
import pandas as pd
from dotenv import load_dotenv

from cuny.cuny import Scrapper
from repository.repository import ScheduleRepository, CourseRepository


class EmailSender:
    def __init__(self, sender_email, sender_password, receiver_email):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def send_email(self, body):
        date_str = pd.Timestamp.today().strftime('%Y-%m-%d')
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = f'Report Cuny - {date_str}'
        msg.attach(MIMEText(body, "html"))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.receiver_email, text)
            server.quit()
            print("Email sent!")
        except Exception as e:
            print("Error: ", e)


def Process():
    print("PROCESS")
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    scheduleRepository = ScheduleRepository(conn)

    course_repository = CourseRepository(conn)

    print(scheduleRepository.get_schedules())
    for schedule in scheduleRepository.get_schedules():
        courses = course_repository.search_courses(schedule['course_name'])
        if len(courses) <= 0:
            print("no courses")
            continue
        html = generate_table(courses[0])

        load_dotenv()
        email_sender = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("SENDER_PASSWORD")
        email = EmailSender(email_sender, sender_password, schedule['user_email'])
        email.send_email(html)


def generate_table(data):
    html = '<html>\n<head>\n<meta charset="utf-8">\n</head>\n<body>\n'
    for item in data:
        html += f'<h2>{item["TableName"]}</h2>\n'
        html += '<table>\n'
        html += '<tr>\n'
        html += '<th>Class</th>\n'
        html += '<th>Section</th>\n'
        html += '<th>Instructor</th>\n'
        html += '<th>Status</th>\n'
        html += '<th>Instruction Mode</th>\n'
        html += '<th>Meeting Dates</th>\n'
        html += '</tr>\n'
        for content in item["content"]:
            html += '<tr>\n'
            html += f'<td>{content["class"]}</td>\n'
            html += f'<td>{content["section"]}</td>\n'
            html += f'<td>{content["instructor"]}</td>\n'
            html += f'<td>{content["status"]}</td>\n'
            html += f'<td>{content["instruction_mode"]}</td>\n'
            html += f'<td>{content["days_and_times"]}</td>\n'
            html += '</tr>\n'
        html += '</table>\n'
    html += '</body>\n</html>'
    return html