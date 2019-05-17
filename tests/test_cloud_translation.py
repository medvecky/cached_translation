# from google_translation import GoogleTranslation
from ..google_translation import GoogleTranslation

from collections import namedtuple

import pytest


class TestCloudTranslation:

    @pytest.fixture(scope="module")
    def cloud_translation(self):
        return GoogleTranslation()

    @pytest.fixture(scope="module")
    def get_request(self):
        return namedtuple("Request", "text targetLanguage sourceLanguage")

    def test_with_source_language(self, cloud_translation, get_request):
        request = get_request(text="Hello world", targetLanguage="ru", sourceLanguage="en")
        translation = cloud_translation.get_translation(request)
        assert translation["translatedText"] == "Привет, мир"
        assert translation["input"] == "Hello world"
        assert "detectedSourceLanguage" not in translation.keys()

    def test_without_source_language(self, cloud_translation, get_request):
        request = get_request(text="Hello world", targetLanguage="ru", sourceLanguage="")
        translation = cloud_translation.get_translation(request)
        assert translation["translatedText"] == "Привет, мир"
        assert translation["input"] == "Hello world"
        assert translation["detectedSourceLanguage"] == "en"
