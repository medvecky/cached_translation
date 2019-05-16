from cached_translations.google_translation import GoogleTranslation

from collections import namedtuple

class TestCloudTranslation():

    def test_with_source_language(self):
        cloud_translation = GoogleTranslation()
        Request = namedtuple("Requerst", "text targetLanguage sourceLanguage")
        request = Request(text="Hello world", targetLanguage="ru", sourceLanguage="en")
        translation = cloud_translation.get_translation(request)
        assert translation["translatedText"] == "Привет, мир"
        assert translation["input"] == "Hello world"
        assert "detectedSourceLanguage" not in translation.keys()


    def test_witout_source_language(self):
        cloud_translation = GoogleTranslation()
        Request = namedtuple("Requerst", "text targetLanguage sourceLanguage")
        request = Request(text="Hello world", targetLanguage="ru",sourceLanguage="")
        translation = cloud_translation.get_translation(request)
        assert translation["translatedText"] == "Привет, мир"
        assert translation["input"] == "Hello world"
        assert translation["detectedSourceLanguage"] == "en"
