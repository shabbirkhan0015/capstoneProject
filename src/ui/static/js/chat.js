// Chat interface JavaScript
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const resetButton = document.getElementById('resetButton');
const statusIndicator = document.getElementById('statusIndicator');
const modelInfo = document.getElementById('modelInfo');

// Load model info on page load
fetch('/api/health')
    .then(response => response.json())
    .then(data => {
        modelInfo.textContent = data.model || 'Unknown';
    })
    .catch(error => {
        console.error('Error fetching health:', error);
        modelInfo.textContent = 'Error';
    });

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    
    // Disable input while processing
    setInputEnabled(false);
    statusIndicator.innerHTML = '<span class="loading"></span> Processing...';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (response.ok) {
            // Add assistant response
            let responseText = data.response;
            
            // Add tool call indicators if any
            if (data.tool_calls && data.tool_calls.length > 0) {
                const toolsUsed = data.tool_calls.map(tc => tc.tool).join(', ');
                responseText += `<div class="tool-call-indicator">🔧 Used tools: ${toolsUsed}</div>`;
            }
            
            // Add escalation notice if needed
            if (data.needs_escalation) {
                responseText += '<div class="escalation-notice">⚠️ This conversation may need human assistance. Would you like me to connect you with a support agent?</div>';
            }
            
            addMessage(responseText, 'assistant');
            statusIndicator.textContent = 'Ready';
        } else {
            addMessage(`Error: ${data.error || 'An error occurred'}`, 'assistant');
            statusIndicator.textContent = 'Error';
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        statusIndicator.textContent = 'Error';
    } finally {
        setInputEnabled(true);
        userInput.focus();
    }
}

// Add message to chat
function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Set input enabled/disabled
function setInputEnabled(enabled) {
    userInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

resetButton.addEventListener('click', async () => {
    if (confirm('Start a new conversation? This will clear the current chat history.')) {
        try {
            await fetch('/api/reset', { method: 'POST' });
            chatMessages.innerHTML = `
                <div class="message assistant-message">
                    <div class="message-content">
                        <p>Hello! I'm your customer support assistant. How can I help you today?</p>
                        <p class="message-hint">I can help with:</p>
                        <ul class="hint-list">
                            <li>Order status and tracking</li>
                            <li>Returns and refunds</li>
                            <li>Shipping information</li>
                            <li>Product questions</li>
                            <li>Policies and FAQs</li>
                        </ul>
                    </div>
                </div>
            `;
            statusIndicator.textContent = 'Ready';
        } catch (error) {
            console.error('Error resetting:', error);
        }
    }
});

// Focus input on load
userInput.focus();

