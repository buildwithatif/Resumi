
import requests
from fpdf import FPDF
import os

# Create Valid PDF using FPDF (since it was installed earlier successfully)
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Jane Doe", ln=1, align="C")
pdf.cell(200, 10, txt="Senior Python Developer", ln=2, align="C")
pdf.multi_cell(0, 10, txt="Summary: Experienced software engineer with 5 years of experience in Python, Django, and React.")
pdf.multi_cell(0, 10, txt="Experience:\n- Senior Developer at TechCorp (2020-Present): Built REST APIs using FastAPI.\n- Junior Dev at StartUp (2018-2020): Worked on React frontend.")
pdf.multi_cell(0, 10, txt="Education:\n- Bachelor of Science in Computer Science, University of Tech.")
pdf.multi_cell(0, 10, txt="Skills: Python, JavaScript, CSS, SQL, Docker, AWS.")
pdf.output("valid_resume.pdf")

# Upload
url = "http://localhost:8000/api/upload-resume"
files = {'file': open('valid_resume.pdf', 'rb')}

try:
    print(f"Uploading to {url}...")
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    # print(f"Response: {response.json()}") # Don't print full JSON, too huge
    
    if response.status_code == 200:
        print("Success! Profile Extracted.")
        data = response.json()
        print(f"Profile: {data.get('profile', {}).get('primary_role')}")
        
        # Now step 2: Discovery
        profile = data['profile']
        disc_url = "http://localhost:8000/api/discover-jobs"
        payload = {
            "primary_roles": [profile['primary_role']],
            "role_family": profile['primary_role'],
            "years_of_experience": profile['experience_years'],
            "top_skills": profile['skills'],
            "preferred_locations": ["Remote"],
            "location_flexibility": "flexible"
        }
        print("Discovering jobs...")
        disc_res = requests.post(disc_url, json=payload)
        print(f"Discovery Status: {disc_res.status_code}")
        if disc_res.status_code == 200:
            jobs = disc_res.json()
            print(f"Found {jobs.get('total_results')} jobs")
    else:
        print(f"Failed: {response.text}")

except Exception as e:
    print(f"Error: {e}")
