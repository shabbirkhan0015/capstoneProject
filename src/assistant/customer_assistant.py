"""Main customer support assistant with LLM, RAG, and tool calling."""
import json
import sys
import os
from typing import List, Dict, Optional
from openai import OpenAI

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.rag.vector_store import VectorStore
from src.tools.mock_apis import execute_tool, TOOL_DEFINITIONS
import config


class CustomerSupportAssistant:
    """AI-powered customer support assistant with RAG and tool calling."""
    
    def __init__(self):
        """Initialize the assistant with LLM, RAG, and tools."""
        if not config.Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.client = OpenAI(api_key=config.Config.OPENAI_API_KEY)
        self.model = config.Config.LLM_MODEL
        self.vector_store = VectorStore()
        self.conversation_history: List[Dict] = []
        
        # System prompt for the assistant
        self.system_prompt = """You are a helpful and professional customer support assistant for an e-commerce platform. 
Your role is to assist customers with their inquiries about orders, returns, refunds, shipping, products, and general policies.

Guidelines:
1. Be friendly, empathetic, and professional in all interactions
2. Use the provided knowledge base and tools to answer questions accurately
3. If you don't have enough information, ask clarifying questions
4. When you cannot help or the issue is complex, offer to escalate to a human agent
5. Always verify order IDs and other details before taking actions
6. Be clear about policies, timelines, and limitations
7. Never make up information - if uncertain, say so and offer to connect with a human agent

You have access to:
- A knowledge base with FAQs, policies, and product information (via RAG)
- Tools to check order status, create returns, check refund policies, and check refund status

Use these tools when appropriate to provide accurate, actionable information."""
    
    def _get_rag_context(self, query: str) -> str:
        """Get relevant context from RAG system."""
        return self.vector_store.get_relevant_context(query)
    
    def _should_use_rag(self, query: str) -> bool:
        """Determine if RAG should be used for this query."""
        # Use RAG for policy, FAQ, or general information queries
        rag_keywords = [
            "policy", "faq", "how", "what", "when", "where", "why",
            "shipping", "return", "refund", "payment", "product",
            "information", "details", "explain", "tell me about"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in rag_keywords)
    
    def _format_tool_result(self, tool_name: str, result: Dict) -> str:
        """Format tool result for LLM context."""
        if result.get("success"):
            # Format successful result
            formatted = f"Tool '{tool_name}' executed successfully:\n"
            formatted += json.dumps(result, indent=2)
        else:
            # Format error result
            formatted = f"Tool '{tool_name}' encountered an error:\n"
            formatted += result.get("error", "Unknown error")
        return formatted
    
    def chat(self, user_message: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Process a user message and return assistant response.
        
        Args:
            user_message: User's message
            conversation_id: Optional conversation ID for tracking
        
        Returns:
            Dictionary with assistant response and metadata
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get RAG context if needed
        rag_context = ""
        if self._should_use_rag(user_message):
            rag_context = self._get_rag_context(user_message)
        
        # Prepare messages for LLM
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add RAG context if available
        if rag_context:
            messages.append({
                "role": "system",
                "content": f"Relevant information from knowledge base:\n\n{rag_context}\n\nUse this information to answer the customer's question accurately."
            })
        
        # Add conversation history
        messages.extend(self.conversation_history[-10:])  # Last 10 messages for context
        
        try:
            # Call LLM with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message
            tool_calls_made = []
            final_response = ""
            
            # Handle tool calls if any
            if assistant_message.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # Execute tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Execute tool
                    tool_result = execute_tool(tool_name, arguments)
                    tool_calls_made.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": tool_result
                    })
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": self._format_tool_result(tool_name, tool_result)
                    })
                
                # Get final response from LLM with tool results
                final_response_obj = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                final_response = final_response_obj.choices[0].message.content
            else:
                final_response = assistant_message.content or "I apologize, but I couldn't generate a response."
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
            
            # Determine if escalation is needed
            escalation_keywords = [
                "escalate", "human", "agent", "representative", "manager",
                "complex", "complicated", "cannot help", "unable to"
            ]
            needs_escalation = any(
                keyword in final_response.lower() 
                for keyword in escalation_keywords
            )
            
            return {
                "response": final_response,
                "tool_calls": tool_calls_made,
                "rag_used": bool(rag_context),
                "needs_escalation": needs_escalation,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in chat: {str(e)}")
            print(f"Traceback: {error_trace}")
            error_message = f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our support team."
            return {
                "response": error_message,
                "error": str(e),
                "error_trace": error_trace,
                "tool_calls": [],
                "rag_used": False,
                "needs_escalation": True,
                "conversation_id": conversation_id
            }
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history."""
        return self.conversation_history.copy()

