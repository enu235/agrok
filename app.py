from flask import Flask, request, Response, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

def stream_from_xai(prompt, api_key):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )
    try:
        completion = client.chat.completions.create(
            model="grok-beta",  # Update to "grok-3" when available
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Error: {str(e)}"

def generate_streaming_response(prompt, api_key):
    for chunk in stream_from_xai(prompt, api_key):
        yield chunk

@app.route('/api/grok', methods=['POST'])
def grok():
    data = request.get_json()
    prompt = data.get('prompt')
    api_key = data.get('api_key')
    
    # Check for API key in environment variables
    env_api_key = os.getenv('OPENAI_API_KEY')
    
    if env_api_key:
        api_key = env_api_key
    elif not api_key:
        return Response("API key is required", status=400)
    
    return Response(generate_streaming_response(prompt, api_key), mimetype='text/plain')

@app.route('/')
def index():
    env_api_key = os.getenv('OPENAI_API_KEY')
    return render_template('index.html', api_key_present=bool(env_api_key))

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for better error logging