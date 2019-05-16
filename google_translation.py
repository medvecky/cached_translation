from google.cloud import translate


class GoogleTranslation():
    def __init__(self):
        self.translate_client = translate.Client()

    def get_translation(self, request):
        if request.sourceLanguage:
            translation = self.translate_client.translate(
                request.text,
                source_language=request.sourceLanguage,
                target_language=request.targetLanguage)
        else:
            translation = self.translate_client.translate(
                request.text,
                target_language=request.targetLanguage)
        return translation
