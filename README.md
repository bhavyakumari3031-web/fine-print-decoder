# 🔍 Fine-Print Decoder

An AI tool that reads loan, insurance and credit card documents, flags hidden charges and risky clauses, and tells you what to do about them, in simple English or Hinglish.

## The problem
Many students and first-time borrowers sign agreements without understanding flat-rate interest, processing fees, penalties and exclusions. By the time they notice, the real cost of the loan is far higher than what was advertised.

## What it does
- Upload a .txt or .pdf, upload or take a photo of the document, paste text, or click a sample
- Finds risky clauses and quotes the exact line from the document
- Gives an overall risk rating (Low / Medium / High) and a verdict: Sign / Negotiate first / Avoid
- Suggests what to do for each risky clause, a step-by-step action plan and safer options
- Suggests questions to ask before signing, shows an FAQ, and has a box for your own questions
- For loans, calculates the real cost with code: amount actually received, total repayment, extra paid and true yearly cost (APR)
- Warns when the real yearly cost is far above the advertised rate, and shows how much a reducing-balance loan would save, calculated by code
- English and Hinglish explanations

## How it is different
Similar AI tools exist. This one focuses on Indian first-time borrowers, quotes the exact line behind every flag, computes the key numbers with fixed formulas instead of AI guesses, and ends with clear next steps, not just warnings.

## Example
For the sample loan in `samples/loan_agreement.txt`, the advertised rate looks like 18% a year. After the 8% processing fee, GST and flat-rate interest, the real yearly cost comes to about 51.9%. The app shows this, explains each risky clause, and shows that a reducing-balance loan at the same rate would save about ₹3,992.

## How to run
1. Clone the repo
2. Install the requirements: `pip install -r requirements.txt`
3. Create a file named `.env` in the project folder with your free key from console.groq.com/keys:
   `GROQ_API_KEY=your_key_here`
4. Start the app: `streamlit run app.py`

## Project files
- `app.py`: the Streamlit app
- `samples/`: three invented sample documents (loan, insurance, credit card)
- `.streamlit/config.toml`: the dark theme
- `requirements.txt`: Python libraries

## AI models and APIs used
- Groq API, model `openai/gpt-oss-120b`, for document analysis, FAQ and questions
- A Groq-hosted vision model (listed in `VISION_MODELS` in `app.py`) to read photos and scanned PDFs
- Streamlit, Groq Python SDK, python-dotenv, pypdf, PyMuPDF, Pillow

## Limitations
- AI can make mistakes. Blurry photos or handwriting may not be read correctly.
- The loan calculator assumes the numbers read from the document are correct, and you can edit them
- Sample documents in `samples/` are invented. Do not upload real personal data.
- This is general guidance for learning, not financial advice
