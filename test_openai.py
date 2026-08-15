from dotenv import load_dotenv
from google import genai
import os

# Load variables from .env
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Check whether API key exists
if not api_key:
    print("ERROR: GEMINI_API_KEY was not found in .env")
    exit()

# Create Gemini client
client = genai.Client(api_key=api_key)

# Send request to Gemini
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Say hello to my SupportPilot AI project."
)

# Print Gemini's response
print(response.text)