from models import gpt4, mistral_large, mixtral_8x22b, commandrplus, claude_3_5_sonnet, claude_3_opus, gpt4omini

def get_model_function(model_choice):
    """high level get model function"""
    def model_wrapper(text, use_case, api_key):
        if model_choice == "OpenAI/GPT-4o":
            return gpt4.gpt4(text, use_case, api_key)
        elif model_choice == "OpenAI/GPT-4o mini":
            return gpt4omini.gpt4omini(text, use_case, api_key)
        elif model_choice == "Mistral AI/Mistral Large 2":
            return mistral_large.mistral_large(text, use_case, api_key)
        elif model_choice == "Mistral AI/Mixtral 8x22b":
            return mixtral_8x22b.mixtral_8x22b(text, use_case, api_key)
        elif model_choice == "Cohere/Command-R+":
            return commandrplus.commandrplus(text, use_case, api_key)
        elif model_choice == "Anthropic/Claude 3.5 Sonnet":
            return claude_3_5_sonnet.claude_3_5_sonnet(text, use_case, api_key)
        elif model_choice == "Anthropic/Claude 3 Opus":
            return claude_3_opus.claude_3_opus(text, use_case, api_key)
        else:
            raise ValueError("Modèle non reconnu")
    
    return model_wrapper