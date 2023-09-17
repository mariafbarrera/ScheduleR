import json


class UserRepository:
    def __init__(self, db_connection):
        self.connection = db_connection

    def create_user_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                email_sender TEXT PRIMARY KEY,
                username TEXT
            )
        ''')
        self.connection.commit()

    def create_user(self, email, username):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO user (email_sender, username) VALUES (?, ?)', (email, username))
        self.connection.commit()

    def get_user_by_email(self, email):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email_sender = ?', (email,))
        return cursor.fetchone()

    def get_all_users(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM user')
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]
        return users


class ClassRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        self.create_class_table()

    def create_class_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS class (
                id INTEGER PRIMARY KEY,
                name TEXT,
                user_email TEXT,
                FOREIGN KEY (user_email) REFERENCES user (email_sender)
            )
        ''')
        self.connection.commit()

    def create_class(self, id, name, user_email):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO class (id, name, user_email) VALUES (?, ?, ?)', (id, name, user_email))
        self.connection.commit()

    def get_classes_by_user_email(self, user_email):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM class WHERE user_email = ?', (user_email,))
        return cursor.fetchall()


class CourseRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        self.create_course_table()

    def create_course_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college TEXT,
                name TEXT,
                details TEXT
            )
        ''')
        self.connection.commit()

    def create_course(self, college, name, details):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO course (college, name, details) VALUES (?, ?, ?)', (college, name, details))
        self.connection.commit()

    def get_all_courses(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM course')
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]
        return users

    def search_courses(self, query):
        cursor = self.connection.cursor()
        query = f"%{query}%"
        cursor.execute('SELECT * FROM course WHERE name LIKE ? LIMIT 10', (query,))
        rows = cursor.fetchall()
        courses = []
        for row in rows:
            course_data = dict(row)
            if 'details' in course_data:
                course_data['details'] = json.loads(course_data['details'])
            courses.append(course_data)

        return courses


class ScheduleRepository:
    def __init__(self, db_connection):
        self.connection = db_connection
        self.create_schedule_table()

    def create_schedule_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college TEXT,
                course_name TEXT,
                user_email TEXT,
                class_id int
            )
        ''')
        self.connection.commit()

    def create_schedule(self, college, course_name, class_id, user_email):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO schedule (college, course_name, user_email, class_id) VALUES (?,?, ?, ?)',
                       (college, course_name, class_id, user_email))
        self.connection.commit()

    def get_schedules(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM schedule')
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]
        return users
