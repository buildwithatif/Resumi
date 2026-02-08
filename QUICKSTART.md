# Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download spaCy model:**
```bash
python -m spacy download en_core_web_md
```

## Running the Application

1. **Start the server:**
```bash
cd orchestration
python main.py
```

2. **Open your browser:**
Navigate to `http://localhost:8000`

3. **Upload your resume:**
- Drag and drop or click to browse
- Supports PDF and DOCX files (max 5MB)

4. **Set your preferences:**
- Add career goals (optional)
- Add preferred locations
- Set relocation and remote preferences

5. **View recommendations:**
- See top 20 matched jobs
- Review match scores and explanations
- Apply directly via provided links

## Troubleshooting

**spaCy model not found:**
```bash
python -m spacy download en_core_web_md
```

**Port 8000 already in use:**
Edit `orchestration/main.py` and change the port number.

**No jobs found:**
- Job sources may be temporarily unavailable
- Try broadening your location preferences
- Consider enabling remote-only option
