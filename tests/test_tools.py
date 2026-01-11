"""Unit tests for mock API tools."""
import unittest
from src.tools.mock_apis import (
    get_order_status,
    create_return_request,
    get_refund_policy,
    get_refund_status
)


class TestMockAPIs(unittest.TestCase):
    """Test cases for mock API functions."""
    
    def test_get_order_status_existing(self):
        """Test getting status for existing order."""
        result = get_order_status("ORD-12345")
        self.assertTrue(result["success"])
        self.assertEqual(result["order_id"], "ORD-12345")
        self.assertIn("status", result)
    
    def test_get_order_status_nonexistent(self):
        """Test getting status for non-existent order."""
        result = get_order_status("ORD-99999")
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_get_refund_policy(self):
        """Test getting refund policy."""
        result = get_refund_policy()
        self.assertTrue(result["success"])
        self.assertIn("policy", result)
        self.assertIn("return_window", result["policy"])
    
    def test_create_return_request(self):
        """Test creating return request."""
        result = create_return_request("ORD-12345", "defective")
        self.assertTrue(result["success"])
        self.assertIn("return_id", result)
        self.assertIn("order_id", result)
    
    def test_create_return_request_invalid_order(self):
        """Test creating return for invalid order."""
        result = create_return_request("ORD-99999", "defective")
        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main()

