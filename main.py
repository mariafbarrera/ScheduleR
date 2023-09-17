import json.encoder
import sqlite3

from chatgpt.chatgpt import get_summary_openai
from cuny.cuny import Init_hunter_process, Init_queens_college_process, Init_brooklyn_college_process
from email_sender.email import Process
from repository.repository import UserRepository, ClassRepository, CourseRepository, ScheduleRepository
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, request, jsonify, render_template

from rmp.rmp import School, Professor
from flask_cors import CORS

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))


app = CustomFlask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


c = get_db_connection()
ur = UserRepository(c)
ur.create_user_table()

c = get_db_connection()
cr = CourseRepository(c)
cr.create_course_table()

c = get_db_connection()
sr = ScheduleRepository(c)
sr.create_schedule_table()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    user_repository = UserRepository(conn)
    users = user_repository.get_all_users()
    conn.close()
    return jsonify(users)


@app.route('/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    course_repository = CourseRepository(conn)
    courses = course_repository.get_all_courses()
    conn.close()
    return jsonify(courses)

@app.route('/search-courses', methods=['GET'])
def search_courses():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'invalid "query".'}), 400

    conn = get_db_connection()
    course_repository = CourseRepository(conn)
    courses = course_repository.search_courses(query)
    conn.close()
    return jsonify(courses)

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    email = user_data.get('email_sender')
    username = user_data.get('username')

    if email and username:
        conn = get_db_connection()
        user_repository = UserRepository(conn)
        user_repository.create_user(email, username)
        response = {'message': 'User created'}
        conn.close()
        return jsonify(response), 201
    else:
        response = {'error': 'db user failed'}
        return jsonify(response), 400


@app.route('/get_summary', methods=['POST'])
def get_summary():
    try:
        data = request.get_json()
        professors = data['professors']
        schoolInput = data['school']
        comments = []
        rateAVG = []
        for p in professors:
            newSchool = School()
            school = newSchool.get_school_by_name(schoolInput)
            newProfessor = Professor()
            professor = newProfessor.get_professors_by_schoolID_and_name(school.legacyId, p)
            comment = professor.get_reviews_by_ID_and_legacyID(p, professor.ID, professor.legacyId)
            comments.append(comment)
            rateAVG.append({p.replace(" ", ""): professor.avgRating})
        response = {
            'summaries': json.loads(get_summary_openai(comments)),
            'rating': rateAVG,
        }

        return response, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create-schedule', methods=['POST'])
def create_schedule():
    user_data = request.get_json()
    college = user_data.get('college')
    email = user_data.get('email')
    course_name = user_data.get('course_name')
    class_id = user_data.get('class_id')
    if email and course_name:
        conn = get_db_connection()
        user_repository = ScheduleRepository(conn)
        user_repository.create_schedule(college, course_name, class_id, email)
        response = {'message': 'Schedule created'}
        conn.close()
        return jsonify(response), 201
    else:
        response = {'error': 'not valid data'}
        return jsonify(response), 400


@app.route('/process', methods=['PUT'])
def process():
    conn = get_db_connection()
    course_repository = CourseRepository(conn)
    Init_hunter_process(course_repository)
    Init_brooklyn_college_process(course_repository)
    Init_queens_college_process(course_repository)
    conn.close()
    return jsonify({"status": "OK"}), 200


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(Process, 'interval', minutes=2)
    scheduler.start()
    app.run(debug=True)
