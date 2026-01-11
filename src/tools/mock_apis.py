"""Mock API functions for order status, returns, and refunds."""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, List


# Mock database for orders
MOCK_ORDERS = {
    "ORD-12345": {
        "order_id": "ORD-12345",
        "customer_id": "CUST-001",
        "status": "shipped",
        "items": [
            {"name": "Classic T-Shirt", "quantity": 2, "price": 29.99},
            {"name": "Summer Dress", "quantity": 1, "price": 59.99}
        ],
        "total": 119.97,
        "shipping_address": "123 Main St, City, State 12345",
        "order_date": "2024-01-15",
        "shipped_date": "2024-01-17",
        "tracking_number": "TRACK-789456",
        "estimated_delivery": "2024-01-22"
    },
    "ORD-67890": {
        "order_id": "ORD-67890",
        "customer_id": "CUST-002",
        "status": "processing",
        "items": [
            {"name": "ProBook 15 Laptop", "quantity": 1, "price": 1299.00}
        ],
        "total": 1299.00,
        "shipping_address": "456 Oak Ave, City, State 67890",
        "order_date": "2024-01-20",
        "estimated_ship_date": "2024-01-23"
    },
    "ORD-11111": {
        "order_id": "ORD-11111",
        "customer_id": "CUST-003",
        "status": "delivered",
        "items": [
            {"name": "AudioMax Pro Headphones", "quantity": 1, "price": 249.00}
        ],
        "total": 249.00,
        "shipping_address": "789 Pine Rd, City, State 11111",
        "order_date": "2024-01-10",
        "shipped_date": "2024-01-12",
        "delivered_date": "2024-01-15",
        "tracking_number": "TRACK-123456"
    }
}

# Mock return requests
MOCK_RETURNS = {}

# Mock refund records
MOCK_REFUNDS = {}


def get_order_status(order_id: str) -> Dict:
    """
    Get order status information.
    
    Args:
        order_id: Order ID to look up
    
    Returns:
        Dictionary with order information or error message
    """
    order_id = order_id.upper().strip()
    
    if order_id in MOCK_ORDERS:
        order = MOCK_ORDERS[order_id].copy()
        
        # Format response
        response = {
            "success": True,
            "order_id": order["order_id"],
            "status": order["status"],
            "order_date": order["order_date"],
            "items": order["items"],
            "total": order["total"],
            "shipping_address": order["shipping_address"]
        }
        
        # Add status-specific information
        if order["status"] == "shipped":
            response["tracking_number"] = order.get("tracking_number", "N/A")
            response["shipped_date"] = order.get("shipped_date", "N/A")
            response["estimated_delivery"] = order.get("estimated_delivery", "N/A")
        elif order["status"] == "processing":
            response["estimated_ship_date"] = order.get("estimated_ship_date", "N/A")
        elif order["status"] == "delivered":
            response["delivered_date"] = order.get("delivered_date", "N/A")
            response["tracking_number"] = order.get("tracking_number", "N/A")
        
        return response
    else:
        return {
            "success": False,
            "error": f"Order {order_id} not found. Please verify your order ID."
        }


def create_return_request(order_id: str, reason: str, items: Optional[List[str]] = None) -> Dict:
    """
    Create a return request for an order.
    
    Args:
        order_id: Order ID to return
        reason: Reason for return
        items: Optional list of specific items to return (defaults to all items)
    
    Returns:
        Dictionary with return request information
    """
    order_id = order_id.upper().strip()
    
    if order_id not in MOCK_ORDERS:
        return {
            "success": False,
            "error": f"Order {order_id} not found."
        }
    
    order = MOCK_ORDERS[order_id]
    
    # Check if order is eligible for return
    if order["status"] == "processing":
        return {
            "success": False,
            "error": "Cannot return an order that is still being processed. Please wait until it ships."
        }
    
    # Check if return already exists
    if order_id in MOCK_RETURNS:
        return {
            "success": False,
            "error": f"Return request already exists for order {order_id}."
        }
    
    # Create return request
    return_id = f"RET-{random.randint(10000, 99999)}"
    return_request = {
        "return_id": return_id,
        "order_id": order_id,
        "status": "pending",
        "reason": reason,
        "items": items if items else [item["name"] for item in order["items"]],
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "estimated_refund": order["total"]
    }
    
    MOCK_RETURNS[order_id] = return_request
    
    return {
        "success": True,
        "return_id": return_id,
        "order_id": order_id,
        "status": "pending",
        "message": "Return request created successfully. You will receive a return shipping label via email.",
        "estimated_refund": order["total"],
        "instructions": "Please package items in original packaging and use the provided return label."
    }


def get_refund_policy() -> Dict:
    """
    Get refund policy information.
    
    Returns:
        Dictionary with refund policy details
    """
    return {
        "success": True,
        "policy": {
            "return_window": "30 days from delivery date",
            "condition": "Items must be unused, unwashed, and in original packaging with tags attached",
            "processing_time": "5-7 business days after we receive and inspect the returned item",
            "refund_method": "Refunds issued to original payment method",
            "exceptions": [
                "Electronics: 14-day return window",
                "Personalized items: No returns accepted",
                "Intimate apparel: No returns for hygiene reasons",
                "Final sale items: Non-returnable"
            ],
            "return_shipping": "Free returns for items over $50; otherwise, return shipping costs apply"
        }
    }


def get_refund_status(return_id: str) -> Dict:
    """
    Get status of a refund for a return.
    
    Args:
        return_id: Return request ID
    
    Returns:
        Dictionary with refund status
    """
    return_id = return_id.upper().strip()
    
    # Find return by return_id
    return_request = None
    for order_id, ret in MOCK_RETURNS.items():
        if ret["return_id"] == return_id:
            return_request = ret
            break
    
    if not return_request:
        return {
            "success": False,
            "error": f"Return request {return_id} not found."
        }
    
    # Simulate refund processing based on return date
    return_date = datetime.strptime(return_request["created_date"], "%Y-%m-%d")
    days_since_return = (datetime.now() - return_date).days
    
    if days_since_return < 2:
        status = "processing"
        message = "Return is being processed. We'll inspect the items and process your refund."
    elif days_since_return < 7:
        status = "approved"
        message = "Return approved. Refund is being processed and will appear in your account within 5-7 business days."
    else:
        status = "completed"
        message = "Refund has been processed and issued to your original payment method."
    
    return {
        "success": True,
        "return_id": return_id,
        "order_id": return_request["order_id"],
        "status": status,
        "message": message,
        "refund_amount": return_request["estimated_refund"],
        "days_since_return": days_since_return
    }


# Tool definitions for LLM function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the status and details of a customer's order. Use this when the customer asks about their order, tracking, delivery status, or order details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID (e.g., ORD-12345)"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_return_request",
            "description": "Create a return request for an order. Use this when the customer wants to return items, initiate a return, or start the return process.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to return"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the return (e.g., 'defective', 'wrong size', 'changed mind', 'not as described')"
                    },
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of specific item names to return. If not provided, all items will be returned."
                    }
                },
                "required": ["order_id", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_refund_policy",
            "description": "Get the refund and return policy information. Use this when the customer asks about return policy, refund policy, return window, or return conditions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_refund_status",
            "description": "Check the status of a refund for a return request. Use this when the customer asks about their refund status, when they'll receive their refund, or refund processing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "return_id": {
                        "type": "string",
                        "description": "The return request ID (e.g., RET-12345)"
                    }
                },
                "required": ["return_id"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: Dict) -> Dict:
    """
    Execute a tool function by name.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments for the tool
    
    Returns:
        Result from tool execution
    """
    tool_map = {
        "get_order_status": get_order_status,
        "create_return_request": create_return_request,
        "get_refund_policy": get_refund_policy,
        "get_refund_status": get_refund_status
    }
    
    if tool_name not in tool_map:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    
    try:
        func = tool_map[tool_name]
        result = func(**arguments)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing {tool_name}: {str(e)}"
        }

