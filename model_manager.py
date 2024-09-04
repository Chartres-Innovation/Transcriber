from models import gpt4, gpt4omini

def get_model_function(model_choice):
    """high level get model function"""
    def model_wrapper(text, use_case, api_key):
        if model_choice == "OpenAI/GPT-4o":
            return gpt4.gpt4(text, use_case, api_key)
        elif model_choice == "OpenAI/GPT-4o mini":
            return gpt4omini.gpt4omini(text, use_case, api_key)
        else:
            raise ValueError("Modèle non reconnu")

    return model_wrapper
