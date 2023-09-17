import re
import requests
from bs4 import BeautifulSoup
import json
from repository.repository import CourseRepository


class Scrapper:
    def __init__(self, options, seletecd_subject_name, subject_name):
        self.url = 'https://globalsearch.cuny.edu/CFGlobalSearchTool/CFSearchToolController'
        self.data_for_search_college = options
        self.data_for_search_class = {"selectedSubjectName": seletecd_subject_name.replace(' ', '+'),
                                      'subject_name': subject_name,
                                      'selectedCCareerName': 'Undergraduate',
                                      'courseCareer': 'UGRD',
                                      'selectedCAttrName': "",
                                      'courseAttr': "",
                                      'selectedCAttrVName': "",
                                      'courseAttValue': "",
                                      'selectedReqDName': "",
                                      'reqDesignation': "",
                                      'selectedSessionName': "",
                                      'class_session': "",
                                      'selectedModeInsName': "",
                                      'meetingStart': 'LT',
                                      'selectedMeetingStartName': 'less+than',
                                      'meetingStartText': "",
                                      'AndMeetingStartText': "",
                                      'meetingEnd': 'LE',
                                      'selectedMeetingEndName': 'less+than+or+equal+to',
                                      'meetingEndText': "",
                                      'AndMeetingEndText': "",
                                      'daysOfWeek': 'I',
                                      'selectedDaysOfWeekName': 'include+only+these+day',
                                      'instructor': 'B',
                                      'selectedInstructorName': 'begins+with',
                                      'instructorName': "",
                                      'search_btn_search': 'Search'}

    def __getCollegeSession(self):
        collegeResponse = requests.post(self.url, data=self.data_for_search_college)
        return collegeResponse.cookies.get_dict()

    def __getClassesData(self):
        cookies = {
            'JSESSIONID': self.__getCollegeSession().get('JSESSIONID'),
        }
        headers = {}

        return requests.post(self.url, cookies=cookies,
                             headers=headers, data=self.data_for_search_class)

    def GetData(self):
        soup = BeautifulSoup(self.__getClassesData().text, features='html.parser')
        div = soup.find('div', attrs={'id': 'contentDivImg_inst0'})
        data = []
        try:
            contentDivs = div.find_all('div', id=re.compile(r'^contentDivImg\d+$'))
        except AttributeError as e:
            print(f"Se produjo un AttributeError al buscar los elementos contentDivs: {e}")
            contentDivs = []
        for contentDiv in contentDivs:
            title = contentDiv.find_previous('span').text.strip()
            table_data = []
            rows = contentDiv.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                img = cells[7].find('img')
                table_data.append({
                    "class": cells[0].find('a').text,
                    "section": cells[1].find('a').text,
                    "days_and_times": cells[2].text,
                    "room": cells[3].text,
                    "instructor": cells[4].text,
                    "instruction_mode": cells[5].text,
                    "meeting_dates": cells[6].text,
                    "status": img['title'].strip() if 'title' in img.attrs else "",
                    "course_topic": cells[8].text
                })
            data.append({
                'table_name': title,
                'content': table_data
            })
        return data


def get_hunter_subjects():
    subjects = [
        {"value": "ARTC", "text": "Art Creative"},
        {"value": "ARTH", "text": "Art History"},
        {"value": "ARTL", "text": "Art Liberal Arts"},
        {"value": "ASAM", "text": "Asian/Asian American Studies"},
        {"value": "ASTR", "text": "Astronomy"},
        {"value": "CMSC", "text": "Computer Science"},
        {"value": "MATH", "text": "Mathematics"},
        {"value": "CUTE", "text": "Curriculum and Teaching"},
        {"value": "DANC", "text": "Dance"},
        {"value": "GEOL", "text": "Geology"},
        {"value": "GRSR", "text": "Graduate Social Research"},
        {"value": "EDHP", "text": "Health And Physical Education"},
        {"value": "HUMA", "text": "Humanities"},
        {"value": "INDE", "text": "Independent Study"}
    ]

    return subjects


def Init_hunter_process(repository: CourseRepository):
    options = {
        'selectedInstName': 'Hunter+College+%7C+',
        'inst_selection': 'HTR01',
        'selectedTermName': '2023+Fall+Term',
        'term_value': '1239',
        'next_btn': 'Next',
    }

    for subject in get_hunter_subjects():
        scrapper = Scrapper(options, subject['text'], subject['value'])
        data = scrapper.GetData()
        for d in data:
            repository.create_course("HTR01", d['table_name'], json.dumps(d['content']))
    return


def get_brooklyn_college():
    subjects = [
        {"value": "AFST", "text": "Africana Studies"},
        {"value": "ANTH", "text": "Anthropology"},
        {"value": "LING", "text": "Linguistics"},
        {"value": "MATH", "text": "Mathematics"},
        {"value": "MUSI", "text": "Music"},
        {"value": "PHIL", "text": "Philosophy"},
        {"value": "SCED", "text": "Secondary Education"},
        {"value": "SOCI", "text": "Sociology"},
    ]

    return subjects


def Init_brooklyn_college_process(repository: CourseRepository):
    options = {
        'selectedInstName': 'Brooklyn+College+%7C+',
        'inst_selection': 'BKL01',
        'selectedTermName': '2023+Fall+Term',
        'term_value': '1239',
        'next_btn': 'Next',
    }

    for subject in get_brooklyn_college():
        scrapper = Scrapper(options, subject['text'], subject['value'])
        data = scrapper.GetData()
        for d in data:
            repository.create_course("BKL01", d['table_name'], json.dumps(d['content']))
    return


def get_queens_subjects():
    subjects = [
        {"value": "ACCT", "text": "Accounting"},
        {"value": "AFST", "text": "Africana Studies"},
        {"value": "ASLG", "text": "American Sign Language"},
        {"value": "ANTH", "text": "Anthropology"},
        {"value": "ARTH", "text": "Art History"},
        {"value": "LANG", "text": "Languages"},
        {"value": "LATI", "text": "Latin"},
        {"value": "LAST", "text": "Latin American Studies"},
        {"value": "LIBR", "text": "Library"},
        {"value": "LISC", "text": "Library Science"},
        {"value": "LING", "text": "Linguistics"},
        {"value": "MATH", "text": "Mathematics"},
        {"value": "YIDD", "text": "Yiddish"}
    ]

    return subjects


def Init_queens_college_process(repository: CourseRepository):
    options = {
        'selectedInstName': 'Queens+College+%7C',
        'inst_selection': 'QNS01',
        'selectedTermName': '2023+Fall+Term',
        'term_value': '1239',
        'next_btn': 'Next',
    }

    for subject in get_queens_subjects():
        scrapper = Scrapper(options, subject['text'], subject['value'])
        data = scrapper.GetData()
        for d in data:
            repository.create_course("QNS01", d['table_name'], json.dumps(d['content']))
    return
