# Fine-Print Decoder

An AI tool that reads loan, insurance and credit card documents and flags hidden charges and risky clauses in simple Hinglish.

## What it does
- Upload or paste a document
- Finds risky clauses and quotes the exact line
- Gives an overall risk rating (Low / Medium / High)
- Calculates the real cost of a loan: money you actually receive, total repayment, extra paid, and the true yearly cost (APR)

## How to run
1. Clone this repo
2. Install: `pip install -r requirements.txt`
3. Create a `.env` file with your free key from console.groq.com/keys:
   `GROQ_API_KEY=your_key_here`
4. Start: `streamlit run app.py`

## AI models and APIs used
- Groq API with the `openai/gpt-oss-120b` model
- Streamlit, Groq Python SDK, python-dotenv

## Notes
- Sample documents are in the `samples` folder. All are invented.
- For learning only, not financial advice. Do not upload real personal data.
