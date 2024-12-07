from openai import OpenAI
from django.conf import settings
import json


client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Set the OpenAI API key
def generate_interview_questions(job_title, job_description, resume_content):
    """
    Generate interview questions based on job title, job description, and resume content.

    Args:
        job_title (str): The job title.
        job_description (str): The job description.
        resume_content (str): The content of the candidate's resume.

    Returns:
        list: A list of generated interview questions.
    """
    try:
        # Prepare the prompt
        prompt = f"""
        You are a career coach and recruitment expert. Your task is to generate exactly 5 interview questions tailored to the candidate's profile and the job requirements.

        Details:
        - Job Title: {job_title}
        - Job Description: {job_description}
        - Candidate's Resume content: ----- {resume_content} -----

        Guidelines:
        1. The questions should focus on the candidate's experience, skills, and suitability for the role.
        2. include question relevant to candidate profile and the job role, if the job description provided.
        3. Ensure the questions are specific, relevant, and avoid generic or overly broad queries.
        4. Format the response as list of questions, with each question as a new element.
        5. Each question should be concise and clear.

        Please provide the 3 tailored interview questions.

        The response should be of following format

        {{
            "title for the question 1" : "question 1",
            "title for the question 2" : "question 2",
            "title for the question 3" : "question 3",
        }}
        """

        # Call OpenAI API
        response = client.chat.completions.create(model="gpt-4o-mini",  # Use the desired model
        messages=[
            {"role": "system", "content": "You are an assistant that generates interview questions in a professional format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500  # Increased to allow for five detailed questions
        )

        # Extract the questions from the response
        questions = response.choices[0].message.content.strip().replace('\n', '')
        questions = json.loads(questions)
        return questions

    except Exception as e:
        raise ValueError(f"Error generating questions: {str(e)}")

def evaluate_answers(question, answer):
    """
    Fetch evaluation results for given answers using OpenAI.

    Args:
        answers (list): A list of transcribed answers (strings).

    Returns:
        list: A list of evaluations for the answers.
    """
    try:
        # Prepare the prompt
        prompt = f"""
        You are a professional interview coach. For the answer provided, evaluate the quality, relevance, and clarity of the response.

        Here is the question and the answer:
        question: {question}
        answer: {answer}

        Focus on the improvements that can be added to the answer from an interview prespective.
        Keep the language simple and more easy to understand.
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",  # Use the desired OpenAI model
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates interview answers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Extract the evaluation text
        evaluation = response.choices[0].message.content.strip()
        return evaluation

    except Exception as e:
        raise ValueError(f"Error fetching results from OpenAI: {str(e)}")
