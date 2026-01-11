"""Main entry point for the E-Commerce Customer Support Assistant."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import app
import config

if __name__ == '__main__':
    print("="*60)
    print("E-Commerce Customer Support Assistant")
    print("="*60)
    print(f"Starting server on http://0.0.0.0:{config.Config.PORT}")
    print(f"Model: {config.Config.LLM_MODEL}")
    print(f"Debug Mode: {config.Config.DEBUG}")
    print("="*60)
    print("\nOpen your browser and navigate to the URL above to start chatting!")
    print("\nPress Ctrl+C to stop the server.\n")
    
    app.run(
        debug=config.Config.DEBUG,
        port=config.Config.PORT,
        host='0.0.0.0'
    )

