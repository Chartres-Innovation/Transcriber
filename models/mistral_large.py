from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

def mistral_large(text, use_case, api_key):
    client = MistralClient(api_key=api_key)

    prompt = ""
    if use_case == "audio_transcription":
        prompt = f" Voici la retranscription textuelle de notre réunion: {text} \n \n ___ \n Fais-moi le compte rendu détaillé de cette réunion."
    elif use_case == "note_formatting":
        prompt = f" Voici mes notes de réunion: {text} \n \n ___ \n Mets en forme ces notes de réunion."

    messages = [
        ChatMessage(role="user", content=prompt)
    ]

    chat_response = client.chat(
        model="mistral-large-latest", #set to large latest, currently using Large 2
        messages=messages,
    )
    result = chat_response.choices[0].message.content
    return result
