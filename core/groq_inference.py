
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")

client = Groq(api_key=api_key)

def query_groq_api(messages):
    """
    Sends the list of messages to Groq chat completion API and returns the assistant's reply.
    :param messages: list of dicts with keys 'role' and 'content' (both strings)
    :return: response string from Groq assistant
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Your model name here
        messages=messages,
    )
    return response.choices[0].message.content.strip()
