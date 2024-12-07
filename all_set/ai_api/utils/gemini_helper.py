import vertexai
from vertexai.language_models import ChatModel
# AIzaSyCNxMCZX9b8uhFpbzmaiXAaojEPabtdA-0

#resume@skilled-text-442318-m9.iam.gserviceaccount.com

# Initialize the Vertex AI client
vertexai.init(project="skilled-text-442318-m9", location="us-central1")

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
        - Candidate's Resume: {resume_content}

        Guidelines:
        1. The questions should focus on the candidate's experience, skills, and suitability for the role.
        2. Ensure the questions are specific, relevant, and avoid generic or overly broad queries.
        3. Format the response as a numbered list of questions, with each question on a new line.
        4. Each question should be concise and clear.

        Please provide the 5 tailored interview questions.
        """

        # Use the ChatModel to get a response
        chat_model = ChatModel.from_pretrained("chat-bison@latest")
        chat = chat_model.start_chat()

        response = chat.send_message(
            prompt,
            temperature=0.7,
            max_output_tokens=300
        )

        # Extract the questions from the response
        questions = response.text.strip().split('\n')
        return questions

    except Exception as e:
        raise ValueError(f"Error generating questions: {str(e)}")


def evaluate_answers(answers):
    """
    Fetch evaluation results for given answers using Vertex AI.

    Args:
        answers (list): A list of transcribed answers (strings).

    Returns:
        list: A list of evaluations for the answers.
    """
    try:
        # Prepare the prompt
        prompt = f"""
        You are a professional evaluator for interview responses. For each answer provided, evaluate the quality, relevance, and clarity of the response. Format your response as follows:

        Input:
        [Answer 1]
        Evaluation:
        [Your Evaluation for Answer 1]

        Input:
        [Answer 2]
        Evaluation:
        [Your Evaluation for Answer 2]

        Here are the answers:
        """ + "\n".join([f"[{i + 1}] {answer}" for i, answer in enumerate(answers)])

        # Use the ChatModel to evaluate answers
        chat_model = ChatModel.from_pretrained("chat-bison@latest")
        chat = chat_model.start_chat()

        response = chat.send_message(
            prompt,
            temperature=0.7,
            max_output_tokens=1000
        )

        # Extract the evaluation text
        evaluations = response.text.strip()

        # Parse the evaluations into a structured list
        result_list = []
        for i, answer in enumerate(answers):
            result_list.append({
                "answer": answer,
                "evaluation": f"Evaluation: {evaluations.split('Evaluation:')[i+1].strip()}"
            })

        return result_list

    except Exception as e:
        raise ValueError(f"Error fetching results from Vertex AI: {str(e)}")
