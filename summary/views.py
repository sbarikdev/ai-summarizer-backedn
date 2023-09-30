from rest_framework import viewsets
from .models import Document
from .serializers import DocumentSerializer
from django.http import JsonResponse
import pdf2image
from PIL import Image
import openai
import tempfile
import os
from dotenv import load_dotenv
from rest_framework.viewsets import ModelViewSet
import fitz  # PyMuPDF

load_dotenv()

def split_text(text):
    max_chunk_size = 2048
    chunks = []
    current_chunk = ""
    
    sentences = text.split(". ")  # Split at period + space to maintain sentence structure
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

import random  # Import the random module

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        pdf_file = request.FILES["pdf_file"]
        max_word = int(request.GET.get("max_word", 50))  # Convert max_word to an integer

        # Extract text from the PDF file using PyMuPDF (Fitz)
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        pdf_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pdf_text += page.get_text()

        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Check if the total tokens in the prompt and completion exceed the model's limit
        text_chunks = split_text(pdf_text)

        # Initialize the summary and MCQs
        summary = ""
        mcqs = ""

        # Generate a summary and MCQs using OpenAI (adjusted length)
        for chunk in text_chunks:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=(f"Please summarize the following text:\n{chunk}\n\nSummary:"),
                max_tokens=500,
                temperature=0.5,
                stop=None  # You can specify words to stop the summary generation if needed
            )
            chunk_summary = response.choices[0].text
            summary += chunk_summary

            # Generate MCQs for the chunk
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=(f"Generate 2 MCQ Questions from the following text:\n{chunk}\n\n"),  # Generate more MCQs
                max_tokens=1500,  # Adjust the max_tokens as needed
                temperature=0.5,
                stop=None  # You can specify words to stop the MCQ generation if needed
            )
            chunk_mcqs = response.choices[0].text
            mcqs += chunk_mcqs

        # Split the generated MCQs into a list of individual questions
        mcq_list = mcqs.split("Q.")

        # Filter out empty questions
        mcq_list = [question.strip() for question in mcq_list if question.strip()]

        # Shuffle the list of questions and select 2 random questions
        random.shuffle(mcq_list)
        selected_mcqs = mcq_list[:2]

        # Save the document, summary, and selected MCQs to the database
        document = Document(pdf_file=None, summary=summary, mcqs="\n".join(selected_mcqs))
        document.save()
        # mcqs_dict = {"Question 1": selected_mcqs[0], "Question 2": selected_mcqs[1]}

        return JsonResponse({'message': 'Document uploaded and summary and MCQs generated successfully.', 'summary': document.summary, 'mcqs': document.mcqs}, status=200)
