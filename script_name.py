import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you hear me?"}
        ]
    )
    print(response.choices[0].message['content'].strip())
except Exception as e:
    print(f"Error: {e}")
