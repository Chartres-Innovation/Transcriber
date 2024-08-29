import anthropic

def claude_3_5_sonnet(text, use_case, api_key):
    client = anthropic.Anthropic(api_key=api_key)

    prompt = ""
    if use_case == "audio_transcription":
        prompt = f" Voici la retranscription textuelle de notre réunion: {text} \n \n ___ \n Fais-moi le compte rendu détaillé de cette réunion."
    elif use_case == "note_formatting":
        prompt = f" Voici mes notes de réunion: {text} \n \n ___ \n Mets en forme ces notes de réunion."

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            }
        ]
    )

    result = message.content[0].text
    return result
