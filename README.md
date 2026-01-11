# E-Commerce Customer Support Assistant

An AI-powered customer support assistant that uses Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and tool calling to autonomously resolve common customer issues for e-commerce platforms.

## Features

- 🤖 **LLM-Powered Conversations**: Natural language understanding and generation
- 🔍 **RAG System**: Retrieval-augmented generation over FAQs, policies, and product information
- 🛠️ **Tool Integration**: Mock APIs for order status, returns, and refunds
- 💬 **Interactive Web UI**: Beautiful, modern chat interface
- 📊 **Evaluation Framework**: Built-in evaluation system for testing and improvement
- 🔄 **Conversation Management**: Context-aware conversations with history

## Project Structure

```
bia-project/
├── src/
│   ├── assistant/          # Main assistant with LLM integration
│   ├── rag/               # RAG system with vector store
│   ├── tools/             # Mock backend APIs
│   └── ui/                # Web interface (Flask)
├── data/
│   ├── knowledge_base/    # FAQs, policies, product info (Markdown)
│   ├── queries/           # Synthetic test queries
│   └── logs/              # Conversation logs
├── evaluation/            # Evaluation scripts and reports
├── tests/                 # Unit tests
├── config.py              # Configuration settings
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- OpenAI API key (or compatible LLM API)

### 2. Installation

```bash
# Navigate to project directory
cd ~/Desktop/bia-project

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 4. Initialize Knowledge Base

The RAG system will automatically build the vector store from markdown files in `data/knowledge_base/` on first run. The knowledge base includes:

- **FAQs**: Common customer questions
- **Policies**: Return, shipping, payment, and privacy policies
- **Products**: Product information and specifications

### 5. Run the Application

```bash
# Start the web server
python main.py

# Or run directly with Flask
python -m src.ui.app
```

The application will be available at `http://localhost:5000`

## Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Start chatting with the assistant
3. Try queries like:
   - "Where is my order ORD-12345?"
   - "What is your return policy?"
   - "I want to return my order"
   - "How long does shipping take?"

### Mock Order IDs

For testing, use these mock order IDs:
- `ORD-12345` - Shipped order
- `ORD-67890` - Processing order
- `ORD-11111` - Delivered order

### Command Line Interface (Optional)

You can also interact with the assistant programmatically:

```python
from src.assistant.customer_assistant import CustomerSupportAssistant

assistant = CustomerSupportAssistant()
result = assistant.chat("Where is my order ORD-12345?")
print(result['response'])
```

## Evaluation

Run the evaluation framework to test assistant performance:

```bash
python evaluation/evaluator.py
```

This will:
- Test the assistant on synthetic queries
- Evaluate tool usage accuracy
- Evaluate RAG usage accuracy
- Generate a detailed evaluation report

## Core Components

### 1. RAG System (`src/rag/vector_store.py`)

- Uses ChromaDB for vector storage
- OpenAI embeddings for semantic search
- Retrieves relevant context from knowledge base

### 2. Assistant (`src/assistant/customer_assistant.py`)

- Integrates LLM with RAG and tools
- Manages conversation history
- Handles function calling for tool execution

### 3. Mock Tools (`src/tools/mock_apis.py`)

Available tools:
- `get_order_status(order_id)`: Check order status and tracking
- `create_return_request(order_id, reason)`: Initiate returns
- `get_refund_policy()`: Get refund policy information
- `get_refund_status(return_id)`: Check refund processing status

### 4. Web UI (`src/ui/`)

- Flask backend with REST API
- Modern, responsive frontend
- Real-time chat interface

## Configuration

Edit `config.py` or set environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `LLM_MODEL`: LLM model to use (default: gpt-4-turbo-preview)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)
- `TOP_K_RESULTS`: Number of RAG results (default: 3)
- `SIMILARITY_THRESHOLD`: RAG similarity threshold (default: 0.7)

## Limitations & Future Improvements

### Current Limitations

1. **Mock Data**: Uses simulated order/return data
2. **Single LLM Provider**: Currently configured for OpenAI
3. **Basic Evaluation**: Evaluation metrics are simplified
4. **No Persistence**: Conversation history not persisted
5. **Limited Error Handling**: Basic error handling for edge cases

### Future Improvements

- [ ] Support for multiple LLM providers (Anthropic, local models)
- [ ] Database integration for real order data
- [ ] Advanced evaluation metrics (BLEU, ROUGE, human evaluation)
- [ ] Conversation persistence and history
- [ ] Multi-language support
- [ ] Enhanced safety and guardrails
- [ ] Analytics and monitoring dashboard
- [ ] Integration with real e-commerce platforms

## Safety & Ethics

The assistant includes:

- **Honest Uncertainty**: Admits when it cannot help
- **Escalation Path**: Offers human agent connection for complex issues
- **Policy Adherence**: Follows defined policies and limitations
- **No Hallucination**: Uses RAG and tools to ground responses in facts

## Technical Report

See `TECHNICAL_REPORT.md` for detailed architecture, design decisions, and evaluation results.

## License

This project is for educational and demonstration purposes.

## Contributing

This is a project template. Feel free to extend and modify for your needs.

## Support

For issues or questions, please refer to the technical documentation or create an issue in the repository.

