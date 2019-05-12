# Imports the Google Cloud client library
from google.cloud import translate


def get_google_translation(text, target_language, client):
    if not text or not target_language or not client:
        return "Parameters missing"
    translation = client.translate(
        text,
        target_language=target_language)
    return translation


# Instantiates a client
translate_client = translate.Client()

while True:
    text = input("Enter text for translation: ")
    if text == "EXIT!":
        break
    target = input("Enter target language: ")
    print(get_google_translation(text, target, translate_client))
