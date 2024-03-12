import pdfplumber
import docx
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

# Function to extract text from a docx file


def parse_resume(file_path):
    doc = docx.Document(file_path)
    full_text = [paragraph.text for paragraph in doc.paragraphs]
    return '\n'.join(full_text)

# Function to analyze the presence of key sections


def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def check_standard_sections(text):
    standard_sections = ['Education', 'Experience',
                         'Skills', 'Certifications', 'Work History']
    found_sections = [section for section in standard_sections if re.search(
        section, text, re.IGNORECASE)]
    # Percentage of standard sections found
    return len(found_sections) / len(standard_sections) * 100

# Function to evaluate keyword relevance


def keyword_relevance(text, job_description):
    text_words = nltk.word_tokenize(text.lower())
    job_desc_words = nltk.word_tokenize(job_description.lower())
    stop_words = set(stopwords.words('english'))

    text_words = [word for word in text_words if word.isalnum()
                  and word not in stop_words]
    job_desc_words = [
        word for word in job_desc_words if word.isalnum() and word not in stop_words]

    text_freq = Counter(text_words)
    job_desc_freq = Counter(job_desc_words)

    relevant_keywords = sum(text_freq[word] for word in job_desc_words)
    total_keywords = sum(job_desc_freq.values())
    return relevant_keywords / total_keywords * 100 if total_keywords > 0 else 0

# Function to check overall length and conciseness


def check_length(text):
    word_count = len(nltk.word_tokenize(text))
    return 100 if 250 <= word_count <= 800 else (word_count / 800 * 100 if word_count < 800 else (1600 - word_count) / 800 * 100)

# Function to aggregate the evaluations


def evaluate_resume(file_path, job_description):
    # Check if job description length is at least 50 characters
    if len(job_description) < 50:
        raise ValueError("Job description must be at least 50 characters long")

    # Check file extension
    if file_path.endswith('.pdf'):
        resume_text = parse_pdf(file_path)
    elif file_path.endswith('.docx'):
        resume_text = parse_resume(file_path)
    else:
        raise ValueError("Unsupported file type")

    section_score = check_standard_sections(resume_text)
    keyword_score = keyword_relevance(resume_text, job_description)
    length_score = check_length(resume_text)

    overall_score = (section_score + keyword_score + length_score) / 3
    return overall_score
