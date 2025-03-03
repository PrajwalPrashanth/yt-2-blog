from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Settings
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest")

# File Settings
BASE_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = BASE_DIR / os.getenv("TRANSCRIPTS_DIR", "transcripts")
OUTPUTS_DIR = BASE_DIR / os.getenv("OUTPUTS_DIR", "outputs")

# Ensure directories exist
TRANSCRIPTS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Validation
def validate_settings():
    """Validate that all required settings are present"""
    required_settings = [
        ("GOOGLE_API_KEY", GOOGLE_API_KEY),
        ("OPENAI_API_KEY", OPENAI_API_KEY),
        ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    ]
    
    missing_settings = [name for name, value in required_settings if not value]
    
    if missing_settings:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_settings)}\n"
            "Please check your .env file."
        )

# Run validation when settings are imported
validate_settings() 