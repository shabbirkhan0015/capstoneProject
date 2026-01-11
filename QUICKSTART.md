# Quick Start Guide

## Prerequisites
- Python 3.8+
- OpenAI API key

## Installation (5 minutes)

### Option 1: Using Setup Script
```bash
cd ~/Desktop/bia-project
./setup.sh
source venv/bin/activate
```

### Option 2: Manual Setup
```bash
cd ~/Desktop/bia-project
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Configuration

1. Edit `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

2. The knowledge base will be built automatically on first run.

## Running the Application

```bash
python main.py
```

Open your browser: `http://localhost:5000`

## Testing

### Try These Queries:
- "Where is my order ORD-12345?"
- "What is your return policy?"
- "I want to return my order ORD-11111"
- "How long does shipping take?"

### Run Evaluation:
```bash
python evaluation/evaluator.py
```

### Run Tests:
```bash
python -m pytest tests/
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
- Make sure `.env` file exists and contains your API key
- Check that you're in the project directory

### Issue: "Module not found"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Issue: "Port already in use"
- Change PORT in `.env` or `config.py`
- Or stop the process using port 5000

## Next Steps

1. Read `README.md` for detailed documentation
2. Check `TECHNICAL_REPORT.md` for architecture details
3. Review `PRESENTATION.md` for presentation materials
4. Customize knowledge base in `data/knowledge_base/`
5. Add more tools in `src/tools/mock_apis.py`

