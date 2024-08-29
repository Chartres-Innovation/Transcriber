import os
import streamlit as st
from werkzeug.utils import secure_filename
from openai import OpenAI
from model_manager import get_model_function
import time
from st_copy_to_clipboard import st_copy_to_clipboard 

UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB in bytes

# set up the Streamlit page configuration
st.set_page_config(page_title="Transcriber", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")

# init session state variables
def initialize_session_state():
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'summary' not in st.session_state:
        st.session_state.summary = None

# function to transcribe audio using Whisper API
def transcribe_audio(file_path, api_key):
    client = OpenAI(api_key=api_key)
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
    return transcription

st.title('Transcriber - Synthèse de réunion IA', anchor=False)

# app container params
with st.container():
    st.subheader("📊 Paramètres", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        # choose between audio transcription and meeting notes formatting
        option = st.selectbox(
            'Choisissez une option:',
            ('Transcription audio', 'Formatage de notes de réunion'),
            format_func=lambda x: f"🎙️ {x}" if x == 'Transcription audio' else f"📝 {x}"
        )
    with col2:
        # select the ai model
        model_choice = st.selectbox(
            'Choisissez le modèle:',
            ('OpenAI/GPT-4o mini', 'OpenAI/GPT-4o','Mistral AI/Mistral Large 2', 'Mistral AI/Mixtral 8x22b', 'Cohere/Command-R+', 'Anthropic/Claude 3.5 Sonnet', 'Anthropic/Claude 3 Opus'),
            help="Si vous ne savez pas quel modèle choisir, utilisez OpenAI/GPT-4o mini."
        )
        
        api_key = st.text_input("Entrez votre clé API OpenAI:", type="password")

initialize_session_state()

# workflow transcript
if option == 'Transcription audio':
    # GDPR compliance check
    with st.expander("En savoir plus sur le RGPD"):
        st.write("Le Règlement Général sur la Protection des Données (RGPD) est une réglementation de l'Union européenne sur la protection des données personnelles. https://www.cnil.fr/fr/reglement-europeen-protection-donnees")

    gdpr_compliance = st.checkbox("Je respecte le RGPD et je ne transmets pas de données confidentielles.", key="gdpr_compliance")

    if gdpr_compliance:
        uploaded_file = st.file_uploader("Choisissez un fichier audio...", type=["wav", "mp3", "m4a"], help="Le fichier audio ne doit pas dépasser 25 mb.")

        if uploaded_file is not None:
            file_size = uploaded_file.size

            if file_size > MAX_FILE_SIZE:
                st.warning(f"⚠️ Le fichier dépasse la limite de 25 mb. Veuillez utiliser [https://offlineconverter.com/audio/](https://offlineconverter.com/audio/) pour réduire la taille du fichier avant de le télécharger.")
            else:
                filename = secure_filename(uploaded_file.name)
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.session_state.file_uploaded = True
                st.success("✅ Fichier audio téléchargé avec succès.")

        if st.session_state.file_uploaded and not st.session_state.processing:
            if st.button("🚀 Lancer l'analyse"):
                if not api_key:
                    st.error("⚠️ Veuillez entrer une clé API OpenAI valide avant de lancer l'analyse.")
                else:
                    st.session_state.processing = True
                    st.info("ℹ️ Traitement en cours, veuillez patienter... Peut prendre plusieurs minutes...")

                    try:
                        # audio transcription process
                        with st.spinner("🔄 1/2 Transcription de l'audio en cours..."):
                            progress_bar = st.progress(0)
                            for i in range(50):
                                time.sleep(0.1)
                                progress_bar.progress(i + 1)
                            text = transcribe_audio(file_path, api_key)

                        # summary generation process
                        with st.spinner("🔄 2/2 Génération de la synthèse en cours..."):
                            for i in range(50, 100):
                                time.sleep(0.1)
                                progress_bar.progress(i + 1)
                            model_function = get_model_function(model_choice)
                            summary = model_function(text, use_case="audio_transcription", api_key=api_key)

                        st.session_state.summary = summary
                        st.session_state.processing = False

                    except Exception as e:
                        st.session_state.processing = False
                        st.error(f"❌ Une erreur s'est produite: {e}")
    else:
        st.warning("⚠️ Veuillez confirmer que vous respectez le RGPD et ne transmettez pas de données confidentielles avant de télécharger un fichier audio.")

# note formatting workflow
elif option == 'Formatage de notes de réunion':
    # GDPR compliance check
    with st.expander("En savoir plus sur le RGPD"):
        st.write("Le Règlement Général sur la Protection des Données (RGPD) est une réglementation de l'Union européenne sur la protection des données personnelles. https://www.cnil.fr/fr/reglement-europeen-protection-donnees")

    gdpr_compliance = st.checkbox("Je respecte le RGPD et je ne transmets pas de données confidentielles.", key="gdpr_compliance_notes")

    if gdpr_compliance:
        notes = st.text_area("Entrez vos notes de réunion ici...", help="Collez vos notes de réunion ici pour les faire formater.")

        if notes and not st.session_state.processing:
            if st.button("🚀 Lancer le formatage"):
                if not api_key:
                    st.error("⚠️ Veuillez entrer une clé API OpenAI valide avant de lancer le formatage.")
                else:
                    st.session_state.processing = True
                    st.info("ℹ️ Traitement en cours, veuillez patienter...")

                    try:
                        # notes formatting process
                        with st.spinner("🔄 Formatage des notes en cours..."):
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.05)
                                progress_bar.progress(i + 1)
                            model_function = get_model_function(model_choice)
                            summary = model_function(notes, use_case="note_formatting", api_key=api_key)

                        st.session_state.summary = summary
                        st.session_state.processing = False

                    except Exception as e:
                        st.session_state.processing = False
                        st.error(f"❌ Une erreur s'est produite: {e}")
    else:
        st.warning("⚠️ Veuillez confirmer que vous respectez le RGPD et ne transmettez pas de données confidentielles avant d'entrer vos notes de réunion.")

# display summary + copy button
if st.session_state.summary:
    st.subheader("📑 Synthèse")
    st.write(st.session_state.summary)

    st_copy_to_clipboard(st.session_state.summary, before_copy_label="📋 Copier la synthèse", after_copy_label="✅ Synthèse copiée dans le presse-papier.")

# footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.markdown("![Version](https://img.shields.io/badge/Version-Beta-blue)")
with col2:
    st.markdown("Cette app web vous est proposée par la Cellule Innovation Intelligence Artificielle.")