"""Flask web application for customer support assistant."""
import sys
import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.assistant.customer_assistant import CustomerSupportAssistant
import config

app = Flask(__name__)
app.secret_key = config.Config.FLASK_SECRET_KEY or os.urandom(24).hex()
CORS(app)

# Initialize assistant
assistant = CustomerSupportAssistant()


@app.route('/')
def index():
    """Render the main chat interface."""
    # Initialize session if needed
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
        assistant.reset_conversation()
    
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        # Get or create conversation ID
        conversation_id = session.get('conversation_id', str(uuid.uuid4()))
        session['conversation_id'] = conversation_id
        
        # Get assistant response
        result = assistant.chat(user_message, conversation_id)
        
        return jsonify({
            'response': result['response'],
            'tool_calls': result.get('tool_calls', []),
            'rag_used': result.get('rag_used', False),
            'needs_escalation': result.get('needs_escalation', False),
            'conversation_id': conversation_id
        })
    
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation."""
    assistant.reset_conversation()
    session.pop('conversation_id', None)
    return jsonify({'success': True})


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model': config.Config.LLM_MODEL
    })


if __name__ == '__main__':
    app.run(debug=config.Config.DEBUG, port=config.Config.PORT, host='0.0.0.0')

