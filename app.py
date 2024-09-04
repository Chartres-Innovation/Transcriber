import os
import streamlit as st
from werkzeug.utils import secure_filename
from openai import OpenAI
import time
from st_copy_to_clipboard import st_copy_to_clipboard
from model_manager import get_model_function
from pydub import AudioSegment

# config
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutes

def split_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    chunks = [audio[i:i + CHUNK_DURATION_MS] for i in range(0, len(audio), CHUNK_DURATION_MS)]
    chunk_files = []

    for i, chunk in enumerate(chunks):
        chunk_file = f"chunk_{i}.mp3"
        chunk.export(chunk_file, format="mp3")
        chunk_files.append(chunk_file)

    return chunk_files

def handle_large_files(uploaded_file):
    # save in temp
    file_path = secure_filename(uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    # split
    chunk_files = split_audio(file_path)

    return file_path, chunk_files

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

def cleanup_files(files):
    """Delete specified files."""
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            st.error(f"Error deleting file {file}: {e}")
            

def cleanup_files(files):
    """Delete specified files."""
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            st.error(f"Error deleting file {file}: {e}")

st.set_page_config(page_title="Transcriber", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")

# init session state variables
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'summary' not in st.session_state:
    st.session_state.summary = None

st.title('Transcriber - Synthèse de réunion IA')

# app container params
with st.container():
    st.subheader("📊 Paramètres", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        option = st.selectbox(
            'Choisissez une option:',
            ('Transcription audio', 'Mise en forme de notes'),
            format_func=lambda x: f"🎙️ {x}" if x == 'Transcription audio' else f"📝 {x}"
        )
    with col2:
        model_choice = st.selectbox(
            'Choisissez le modèle:',
            ('OpenAI/GPT-4o mini', 'OpenAI/GPT-4o'),
            help="Si vous ne savez pas quel modèle choisir, utilisez OpenAI/GPT-4o mini."
        )
        api_key = st.text_input("Entrez votre clé API OpenAI:", type="password")

# workflow transcript
if option == 'Transcription audio':
    with st.expander("En savoir plus sur le RGPD"):
        st.write("""Le Règlement Général sur la Protection des Données (RGPD) est une réglementation de l'Union
                 européenne sur la protection des données personnelles.
                 https://www.cnil.fr/fr/reglement-europeen-protection-donnees""")

    gdpr_compliance = st.checkbox("Je respecte le RGPD et je ne transmets pas de données confidentielles.",
                                  key="gdpr_compliance")

    if gdpr_compliance:
        uploaded_file = st.file_uploader("Choisissez un fichier audio...", type=["wav", "mp3", "m4a"],
                                         help="Le fichier audio ne doit pas dépasser 200 mb.")

        if uploaded_file is not None:
            file_size = uploaded_file.size

            # handle large file if > limit
            if file_size > MAX_FILE_SIZE:
                st.warning(f"""⚠️ Le fichier dépasse 25 mb. Un traitement supplémentaire est nécessaire. Veuillez
                           patienter.""")
                file_path, chunk_files = handle_large_files(uploaded_file)

                st.session_state.file_uploaded = True
                st.success("✅ Fichier audio téléchargé et divisé avec succès.")
            else:
                st.session_state.file_uploaded = True
                st.success("✅ Fichier audio téléchargé avec succès.")
                file_path = secure_filename(uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                chunk_files = []

        if st.session_state.file_uploaded and not st.session_state.processing and st.button("🚀 Lancer l'analyse"):
            if not api_key:
                st.error("⚠️ Veuillez entrer une clé API OpenAI valide avant de lancer l'analyse.")
            else:
                st.session_state.processing = True
                st.info("ℹ️ Traitement en cours, veuillez patienter... Peut prendre plusieurs minutes...")

                try:
                    if file_size > MAX_FILE_SIZE:
                        # add to all_text all chunk texts
                        all_text = ""
                        for chunk_file in chunk_files:
                            with st.spinner("🔄 Transcription de l'audio en cours..."):
                                text = transcribe_audio(chunk_file, api_key)
                                all_text += text + "\n"
                                cleanup_files([chunk_file])  # clean up chunk file after processing
                    else:
                        with st.spinner("🔄 1/2 Transcription de l'audio en cours..."):
                            text = transcribe_audio(file_path, api_key)
                            all_text = text

                    # audio transcript
                    with st.spinner("🔄 2/2 Génération de la synthèse en cours..."):
                        model_function = get_model_function(model_choice)
                        summary = model_function(all_text, use_case="audio_transcription", api_key=api_key)

                    st.session_state.summary = summary
                    st.session_state.processing = False

                except Exception as e:
                    st.session_state.processing = False
                    st.error(f"❌ Une erreur s'est produite: {e}")

                # cleanup main audio files after processing
                cleanup_files([file_path])

    else:
        st.warning("""⚠️ Veuillez confirmer que vous respectez le RGPD et ne transmettez pas de données confidentielles
                   avant de télécharger un fichier audio.""")

# note formatting workflow
elif option == 'Mise en forme de notes':
    with st.expander("En savoir plus sur le RGPD"):
        st.write("""Le Règlement Général sur la Protection des Données (RGPD) est une réglementation de l'Union
                 européenne sur la protection des données personnelles.
                 https://www.cnil.fr/fr/reglement-europeen-protection-donnees""")

    gdpr_compliance = st.checkbox("Je respecte le RGPD et je ne transmets pas de données confidentielles.",
                                  key="gdpr_compliance_notes")

    if gdpr_compliance:
        notes = st.text_area("Entrez vos notes de réunion ici...",
                             help="Collez vos notes de réunion ici pour les faire formater.")

        if notes and not st.session_state.processing and st.button("🚀 Lancer la mise en forme"):
            if not api_key:
                st.error("⚠️ Veuillez entrer une clé API OpenAI valide avant de lancer le formatage.")
            else:
                st.session_state.processing = True
                st.info("ℹ️ Traitement en cours, veuillez patienter...")

                try:
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
        st.warning("""⚠️ Veuillez confirmer que vous respectez le RGPD et ne transmettez pas de données confidentielles
                   avant d'entrer vos notes de réunion.""")

# show summarization
if st.session_state.summary:
    st.subheader("📝 Résumé de la transcription / Mise en forme des notes")
    st.write(st.session_state.summary)

    # copy button / need https
    st_copy_to_clipboard(st.session_state.summary, "Copier dans le presse-papiers", "Contenu copié ! ✅")


# footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.markdown("![Version](https://img.shields.io/badge/Version-v0.1-yellow)")
with col2:
    st.markdown("Cette app web vous est proposée par la Cellule Innovation Intelligence Artificielle.")
