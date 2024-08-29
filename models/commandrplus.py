import cohere

def commandrplus(text, use_case, api_key):
    client = cohere.Client(api_key)

    prompt = ""
    if use_case == "audio_transcription":
        prompt = f" Voici la retranscription textuelle de notre réunion: {text} \n \n ___ \n Fais-moi le compte rendu détaillé de cette réunion."
    elif use_case == "note_formatting":
        prompt = f" Voici mes notes de réunion: {text} \n \n ___ \n Mets en forme ces notes de réunion."

    chat_response = client.chat(
        model="command-r-plus",
        message=prompt
    )

    result = chat_response.text
    return result
