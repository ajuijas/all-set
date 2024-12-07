import base64
from io import BytesIO
import os
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.openai_helper import generate_interview_questions, evaluate_answers
from .serializers import GenerateQuestionsSerializer, GetResultsSerializer
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from gtts import gTTS
import speech_recognition as sr
from PyPDF2 import PdfReader
import zipfile
from pydub import AudioSegment

from django.shortcuts import render

def upload_page(request):
    return render(request, 'upload_page.html')

def questions_page(request):
    return render(request, 'questions_page.html')



# TTS (Text-to-Speech) function
def tts(question):
    """
    Convert text to speech and return audio buffer.
    :param question: The text to convert to speech.
    :return: BytesIO object containing the audio data.
    """
    try:
        tts_object = gTTS(text=question, lang='en')
        audio_buffer = BytesIO()
        tts_object.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        raise Exception(f"Error in text-to-speech: {str(e)}")


# STT (Speech-to-Text) function
def stt(audio_data):
    """
    Convert speech to text from raw audio data.
    :param audio_data: Raw audio data as bytes.
    :return: Transcribed text from the audio.
    """
    try:
        # Convert audio data to PCM WAV format using pydub
        audio_buffer = BytesIO(audio_data)
        audio_segment = AudioSegment.from_file(audio_buffer)  # Automatically detects format
        wav_buffer = BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Use SpeechRecognition to transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError as e:
        raise Exception(f"Speech recognition error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error in speech-to-text: {str(e)}")

# API View for generating interview questions
class GenerateQuestionsAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)  # Add parsers to handle file uploads

    def post(self, request, *args, **kwargs):
        serializer = GenerateQuestionsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        resume_file = validated_data['resume']
        job_title = validated_data['job_title']
        job_description = validated_data.get('job_description', '')

        try:
            pdf_reader = PdfReader(resume_file)  # resume_file is the uploaded file object
            resume_content = ''.join(
                page.extract_text() for page in pdf_reader.pages if page.extract_text()
            )

            # questions = ['1. Can you describe a specific project where you utilized Python to build a scalable application, and what challenges you faced during the development process?', '', '2. Given your experience with web crawling systems, how do you approach designing a fault-tolerant and scalable architecture for such applications?', '', '3. How have you implemented automated testing procedures in your previous roles, and what tools or frameworks did you find most effective for ensuring application reliability?', '', '4. In your current position, how do you collaborate with infrastructure teams to troubleshoot and resolve issues, and can you provide an example of a significant bug you helped fix?', '', '5. Can you elaborate on your experience with continuous integration (CI) practices, specifically how they have contributed to the efficiency and quality of your software development process?']
            # Generate audio for each question and include titles
            questions = generate_interview_questions(job_title, job_description, resume_content)

            # Prepare zip file response
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, (title, question) in enumerate(questions.items()):
                    if question:
                        # Generate audio for the question
                        audio_buffer = tts(question)
                        # Format the title to make it file-system friendly
                        safe_title = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
                        # Write the audio file to the zip
                        zip_file.writestr(f"{i + 1}_{safe_title}.mp3", audio_buffer.getvalue())

            zip_buffer.seek(0)

            response = FileResponse(
                zip_buffer,
                as_attachment=True,
                content_type='application/zip'
            )
            response['Content-Disposition'] = 'attachment; filename="questions_audio.zip"'

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API View for evaluating answers
class GetResultsAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    def post(self, request, *args, **kwargs):
        serializer = GetResultsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_file = request.FILES.get('audio_answer')
        if not audio_file:
            return Response({"error": "Audio answer file is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            audio_data = audio_file.read()
            answer_text = stt(audio_data)

            question = serializer.validated_data['question']
            result_text = evaluate_answers(question, answer_text)
            # result_text = 'The answer provided is of high quality. The applicant has clearly highlighted a range of relevant strengths including problem-solving, adaptability, teamwork, analytical thinking, quick learning, communication, and organization. They have also given examples of how these strengths are applied, such as breaking down complex tasks and learning new skills. The relevance is high, as these strengths directly relate to the question asked and are valuable in many job roles. The clarity could be improved by using more punctuation to break up the long sentences, but overall, the response is comprehensive and well-structured.'

            audio_response = tts(result_text)

            response = FileResponse(
                audio_response,
                as_attachment=True,
                content_type='audio/mpeg'
            )
            response['Content-Disposition'] = 'attachment; filename="evaluation_result.mp3"'

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)