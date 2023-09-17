import requests
import re


class School:
    def __init__(self, legacyId=None, name=None, avgRating=None, numRatings=None):
        self.legacyId = legacyId
        self.name = name
        self.avgRating = avgRating
        self.numRatings = numRatings

    def get_school_by_name(self, school_name: str):
        school_name = school_name.replace(' ', '+')
        url = f"https://www.ratemyprofessors.com/search/schools?q={school_name}"

        try:
            page = requests.get(url)
            page.raise_for_status()  # Verificar si la solicitud fue exitosa

            # Utilizar una expresión regular para encontrar la información relevante en la página
            page_text = page.text
            legacy_ids = re.findall(r'"legacyId":(\d+)', page_text)
            names = re.findall(r'"name":"(.*?)"', page_text)
            ratings = re.findall(r'"numRatings":(\d+)', page_text)
            avgRatings = re.findall(r'"avgRatingRounded":(\d+\.\d+|\d+|true|false)', page_text)

            school_list = []

            for i in range(len(legacy_ids)):
                school_list.append(School(int(legacy_ids[i]), names[i], float(avgRatings[i]), int(ratings[i])))
            school_list.sort(key=lambda x: x.numRatings, reverse=True)
            if len(school_list) > 0:
                return school_list[0]
            print("school not found")
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return School


class Professor:
    def __init__(self, name=None, ID=None, legacyId=None, avgRating=None, numRatings=None):
        self.name = name
        self.ID = ID
        self.legacyId = legacyId
        self.avgRating = avgRating
        self.numRatings = numRatings

    def get_professors_by_schoolID_and_name(self, schoolID: int, professor_name: str):
        """
        Gets a list of professors with the specified School and professor name.

        This only returns up to 20 professors, so make sure that the name is specific.
        For instance, searching "Smith" with a school might return more than 20 professors,
        but only the first 20 will be returned.

        :param schoolID: The professor's school.
        :param professor_name: The professor's name.
        :return: List of professors that match the school and name. If no professors are found,
                 this will return an empty list.
        """
        try:

            professor_name = professor_name.replace(' ', '+')
            url = f"https://www.ratemyprofessors.com/search/professors/{schoolID}?q={professor_name}"
            page = requests.get(url)
            page_text = page.text
            legacy_ids = re.findall(r'"legacyId":(\d+)', page_text)
            IDs = re.findall(r'"Teacher","id":"(.*?)"', page_text)
            ratings = re.findall(r'"numRatings":(\d+)', page_text)
            avgRatings = re.findall(r'"avgRating":(\d+\.\d+|\d+|true|false)', page_text)

            professor_list = []

            for i in range(len(legacy_ids)):
                professor_list.append(
                    Professor(professor_name, IDs[i], int(legacy_ids[i]), float(avgRatings[i]), int(ratings[i])))
            professor_list.sort(key=lambda x: x.numRatings, reverse=True)
            if len(professor_list) > 0:
                return professor_list[0]

            print("professors not found")
            return Professor
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return Professor

    def get_reviews_by_ID_and_legacyID(self, name : str, base64ID: str, legacyID: int):
        if id is None or legacyID is None:
            raise ValueError("The 'id' and 'legacyID' arguments cannot be None")

        url = 'https://www.ratemyprofessors.com/graphql'

        headers = {
            'Authorization': 'Basic dGVzdDp0ZXN0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Content-Type': 'application/json',
            'Referer': 'https://www.ratemyprofessors.com/professor/' + str(legacyID),
        }

        query = (
                '{\n'
                '  "query": "query RatingsListQuery($id: ID!) {node(id: $id) { ... on Teacher { ratings { edges { node { comment } } } } } }",\n'
                '  "variables": {\n'
                '    "id": "' + base64ID +
                '"\n'
                '  }\n'
                '}'
        )

        response = requests.post(url, headers=headers, data=query)

        if response.status_code == 200:
            data = response.json()
            result = {
                'name': name,
                'comments': [edge["node"]["comment"] for edge in data["data"]["node"]["ratings"]["edges"]]
            }
            return result

        else:
            raise ValueError("internal server error")

