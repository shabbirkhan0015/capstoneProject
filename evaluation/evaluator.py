"""Evaluation framework for the customer support assistant."""
import json
import os
import sys
from typing import Dict, List

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.assistant.customer_assistant import CustomerSupportAssistant


class AssistantEvaluator:
    """Evaluates assistant performance on test queries."""
    
    def __init__(self):
        """Initialize evaluator with assistant."""
        self.assistant = CustomerSupportAssistant()
    
    def load_test_queries(self, file_path: str) -> List[Dict]:
        """Load test queries from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('queries', [])
    
    def evaluate_query(self, query_data: Dict) -> Dict:
        """
        Evaluate assistant response for a single query.
        
        Args:
            query_data: Query with id, query, intent, expected_tool, etc.
        
        Returns:
            Evaluation results
        """
        query = query_data['query']
        expected_tool = query_data.get('expected_tool')
        expected_rag = query_data.get('expected_rag', False)
        
        # Get assistant response
        result = self.assistant.chat(query)
        
        # Check tool usage
        tools_used = [tc['tool'] for tc in result.get('tool_calls', [])]
        correct_tool = expected_tool in tools_used if expected_tool else True
        
        # Check RAG usage
        rag_used = result.get('rag_used', False)
        correct_rag = rag_used == expected_rag if expected_rag is not None else True
        
        # Basic response quality checks
        response = result.get('response', '')
        has_response = len(response) > 0
        response_length = len(response)
        
        # Check for escalation (should be appropriate)
        needs_escalation = result.get('needs_escalation', False)
        
        return {
            'query_id': query_data['id'],
            'query': query,
            'intent': query_data.get('intent'),
            'response': response,
            'tools_used': tools_used,
            'expected_tool': expected_tool,
            'correct_tool': correct_tool,
            'rag_used': rag_used,
            'expected_rag': expected_rag,
            'correct_rag': correct_rag,
            'has_response': has_response,
            'response_length': response_length,
            'needs_escalation': needs_escalation,
            'tool_calls': result.get('tool_calls', [])
        }
    
    def evaluate_all(self, queries_file: str) -> Dict:
        """
        Evaluate all test queries.
        
        Args:
            queries_file: Path to queries JSON file
        
        Returns:
            Overall evaluation results
        """
        queries = self.load_test_queries(queries_file)
        results = []
        
        print(f"Evaluating {len(queries)} queries...")
        
        for query_data in queries:
            print(f"Processing query {query_data['id']}...")
            result = self.evaluate_query(query_data)
            results.append(result)
            # Reset conversation for each query
            self.assistant.reset_conversation()
        
        # Calculate metrics
        total = len(results)
        correct_tools = sum(1 for r in results if r['correct_tool'])
        correct_rag = sum(1 for r in results if r.get('correct_rag', True))
        has_responses = sum(1 for r in results if r['has_response'])
        avg_response_length = sum(r['response_length'] for r in results) / total if total > 0 else 0
        
        metrics = {
            'total_queries': total,
            'tool_accuracy': correct_tools / total if total > 0 else 0,
            'rag_accuracy': correct_rag / total if total > 0 else 0,
            'response_rate': has_responses / total if total > 0 else 0,
            'avg_response_length': avg_response_length,
            'results': results
        }
        
        return metrics
    
    def generate_report(self, metrics: Dict, output_file: str):
        """Generate evaluation report."""
        report = f"""
# Evaluation Report

## Summary Metrics

- **Total Queries**: {metrics['total_queries']}
- **Tool Accuracy**: {metrics['tool_accuracy']:.2%}
- **RAG Accuracy**: {metrics['rag_accuracy']:.2%}
- **Response Rate**: {metrics['response_rate']:.2%}
- **Average Response Length**: {metrics['avg_response_length']:.0f} characters

## Detailed Results

"""
        for result in metrics['results']:
            report += f"""
### Query {result['query_id']}: {result['query']}

- **Intent**: {result['intent']}
- **Tools Used**: {', '.join(result['tools_used']) if result['tools_used'] else 'None'}
- **Expected Tool**: {result['expected_tool'] or 'N/A'}
- **Tool Correct**: {'✓' if result['correct_tool'] else '✗'}
- **RAG Used**: {'Yes' if result['rag_used'] else 'No'}
- **RAG Correct**: {'✓' if result.get('correct_rag', True) else '✗'}
- **Response Length**: {result['response_length']} characters
- **Needs Escalation**: {'Yes' if result['needs_escalation'] else 'No'}

**Response**: {result['response'][:200]}...

---
"""
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"Report saved to {output_file}")


if __name__ == '__main__':
    evaluator = AssistantEvaluator()
    
    queries_file = './data/queries/synthetic_queries.json'
    metrics = evaluator.evaluate_all(queries_file)
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Total Queries: {metrics['total_queries']}")
    print(f"Tool Accuracy: {metrics['tool_accuracy']:.2%}")
    print(f"RAG Accuracy: {metrics['rag_accuracy']:.2%}")
    print(f"Response Rate: {metrics['response_rate']:.2%}")
    print(f"Avg Response Length: {metrics['avg_response_length']:.0f} chars")
    print("="*50)
    
    # Generate report
    os.makedirs('./evaluation', exist_ok=True)
    evaluator.generate_report(metrics, './evaluation/evaluation_report.md')

