import os
from dotenv import load_dotenv
import openai

load_dotenv()


# Prompt example
# Based on all comments available, provide a summary for each professor where you begin with 'students say that'
# and then summarize what they like OR dislike the most about each professor. Be sure to include as much detail as possible,
# whether it's positive or negative, and fix any grammatical errors in the process. DO NOT ADD ANYTHING BEFORE 'STUDENTS SAY'.
#
# Students say that Profesor A: Comentario 1
#
# Comentario 2
#
# Comentario 3
#
# Students say that Profesor B: Comentario 4
#
# Comentario 5
#
# Comentario 6

def get_summary_openai(data):
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = """Based on all comments available, provide a VALID JSON OUTPUT ARRAY OBJECT WHERE THE KEY IS THE NAME AND VALUE THE SUMMARY. summary for each professor where you begin with 'students say that' and then summarize what they like OR dislike the most about each professor. Be sure to include as much detail as possible, whether it's positive or negative, and fix any grammatical errors in the process. DO NOT ADD ANYTHING BEFORE 'STUDENTS SAY.'.\n\n"""

    for professor_data in data:
        name = professor_data["name"]
        comments = professor_data["comments"]
        comments = comments[:3]
        comments_text = "\n\n".join(comments)
        prompt += f"Students say that {name}: {comments_text}\n\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2000,
        api_key=api_key
    )

    summaries = response.choices[0].text.strip()
    return summaries
