from openai import OpenAI

def gpt4omini(text, use_case, api_key):
    client = OpenAI(api_key=api_key)

    prompt = ""
    if use_case == "audio_transcription":
        prompt = f"Voici la retranscription textuelle de notre réunion: {text}\n\n___\nFais-moi le compte rendu détaillé de cette réunion."
    elif use_case == "note_formatting":
        prompt = f"Voici mes notes de réunion: {text}\n\n___\nMets en forme ces notes de réunion."

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-4o-mini",
    )
    result = response.choices[0].message.content
    return result