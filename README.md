# 🔍 Fine-Print Decoder

An AI tool that reads loan, insurance and credit card documents, flags hidden charges and risky clauses, and explains them in simple English or Hinglish.

**Live demo:** run locally, see "How to run" below

## The problem
Many students and first-time borrowers sign agreements without understanding flat-rate interest, processing fees, penalties and exclusions.

## What it does
- Upload a .txt or text-based .pdf, paste text, or click a sample
- Finds risky clauses and quotes the exact line from the document
- Gives an overall risk rating (Low / Medium / High)
- Suggests questions to ask before signing, shows an FAQ, and has a box for your own questions
- For loans, calculates the real cost with code: amount actually received, total repayment, extra paid and true yearly cost (APR)
- English and Hinglish explanations

## How it is different
Similar AI tools exist. This one focuses on Indian first-time borrowers, quotes the exact line behind every flag, and computes the key numbers with fixed formulas instead of AI guesses.

## How to run
1. Clone the repo
2. `pip install -r requirements.txt`
3. Create a `.env` file with your free key from console.groq.com/keys:
   `GROQ_API_KEY=your_key_here`
4. `streamlit run app.py`

## AI models and APIs used
- Groq API, model `openai/gpt-oss-120b`
- Streamlit, Groq Python SDK, python-dotenv, pypdf

## Limitations
- Scanned or image-only PDFs and photos are not supported yet
- AI can make mistakes; the loan calculator assumes the numbers shown are correct
- Sample documents in `samples/` are invented. Do not upload real personal data.
- For learning only, not financial advice
