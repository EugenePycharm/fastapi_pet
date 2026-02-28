from google import genai
from google.genai import types
from config import config_env

client = genai.Client(api_key=config_env.API_KEY)
chat = client.chats.create(model="gemini-2.5-flash-lite", config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)))
response = chat.send_message_stream("I have 2 dogs in my house.")
for chunk in response:
    print(chunk.text, end="")

response = chat.send_message_stream("How many paws are in my house?")
for chunk in response:
    print(chunk.text, end="")

for message in chat.get_history():
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)
