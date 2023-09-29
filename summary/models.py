from django.db import models

class Document(models.Model):
    pdf_file = models.FileField(upload_to='pdfs/')
    summary = models.TextField(null=True, blank=True)
