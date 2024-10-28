from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Together AI API configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.ai/models/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
