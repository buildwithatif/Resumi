
import requests
from fpdf import FPDF
import os

# Create dummy PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="John Doe", ln=1, align="C")
pdf.cell(200, 10, txt="Software Engineer", ln=2, align="C")
pdf.cell(200, 10, txt="Experience: 5 years of Python and JavaScript development.", ln=3, align="L")
pdf.cell(200, 10, txt="Education: Bachelor of Science in Computer Science", ln=4, align="L")
pdf.output("test_resume.pdf")

# Upload
url = "http://localhost:8000/api/upload-resume"
files = {'file': open('test_resume.pdf', 'rb')}

try:
    print(f"Uploading to {url}...")
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Cleanup
# os.remove("test_resume.pdf")
