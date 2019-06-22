from collections import namedtuple
import google_translation
from unittest.mock import MagicMock
import pytest
import google


class TestGoogleTranslation:

    @pytest.fixture
    def google_client_mock(self):
        google_client_mock = MagicMock()
        return google_client_mock

    @pytest.fixture
    def get_request(self):
        return namedtuple("Request", "text targetLanguage sourceLanguage")

    @pytest.fixture
    def google_client_constructor_mock(self, google_client_mock, monkeypatch):
        google_client_constructor_mock = MagicMock(return_value=google_client_mock)
        monkeypatch.setattr("google.cloud.translate.Client", google_client_constructor_mock)

    def test_get_translation_with_source(self, google_client_constructor_mock, google_client_mock, get_request):
        google_client_mock.translate = MagicMock(return_value={
            "translatedText": "Translated Text",
            "input": "Text for translation"})

        translation_request = get_request(
            text=["Text for translation"],
            targetLanguage="ru",
            sourceLanguage="en")

        cloud_translation = google_translation.GoogleTranslation()
        translation = cloud_translation.get_translation(translation_request)

        google_client_mock.translate.assert_called_with(
            translation_request.text,
            source_language=translation_request.sourceLanguage,
            target_language=translation_request.targetLanguage)

        assert translation["translatedText"] == "Translated Text"
        assert translation["input"] == "Text for translation"
        assert "detectedSourceLanguage" not in translation.keys()

    def test_get_translation_without_source(self, google_client_mock, google_client_constructor_mock, get_request):
        google_client_mock.translate = MagicMock(return_value={
            "translatedText": "Translated Text",
            "input": "Text for translation",
            "detectedSourceLanguage": "en"})

        translation_request = get_request(
            text=["Text for translation"],
            targetLanguage="ru",
            sourceLanguage="")

        cloud_translation = google_translation.GoogleTranslation()
        translation = cloud_translation.get_translation(translation_request)

        google_client_mock.translate.assert_called_with(
            translation_request.text,
            target_language=translation_request.targetLanguage)

        assert translation["translatedText"] == "Translated Text"
        assert translation["input"] == "Text for translation"
        assert translation["detectedSourceLanguage"] == "en"

    def test_get_translation_multi_string_with_source(
            self,
            google_client_constructor_mock,
            google_client_mock, get_request):
        google_client_mock.translate = MagicMock(return_value=[{
            "translatedText": "Translated Text 1",
            "input": "Text for translation 1"},
            {"translatedText": "Translated Text 2",
             "input": "Text for translation 2"}
        ])

        translation_request = get_request(
            text=["Text for translation 1", "Text for translation 2"],
            targetLanguage="ru",
            sourceLanguage="en")

        cloud_translation = google_translation.GoogleTranslation()
        translation = cloud_translation.get_translation(translation_request)

        google_client_mock.translate.assert_called_with(
            translation_request.text,
            source_language=translation_request.sourceLanguage,
            target_language=translation_request.targetLanguage)

        assert len(translation) == 2
        translation_1 = translation[0]
        translation_2 = translation[1]
        assert translation_1["translatedText"] == "Translated Text 1"
        assert translation_1["input"] == "Text for translation 1"
        assert "detectedSourceLanguage" not in translation_1.keys()
        assert translation_2["translatedText"] == "Translated Text 2"
        assert translation_2["input"] == "Text for translation 2"
        assert "detectedSourceLanguage" not in translation_2.keys()

    def test_get_translation_multi_string_without_source(
            self,
            google_client_constructor_mock,
            google_client_mock, get_request):
        google_client_mock.translate = MagicMock(return_value=[{
            "translatedText": "Translated Text 1",
            "input": "Text for translation 1",
            "detectedSourceLanguage": "en"},
            {"translatedText": "Translated Text 2",
             "input": "Text for translation 2",
             "detectedSourceLanguage": "lv"}
        ])

        translation_request = get_request(
            text=["Text for translation 1", "Text for translation 2"],
            targetLanguage="ru",
            sourceLanguage="")

        cloud_translation = google_translation.GoogleTranslation()
        translation = cloud_translation.get_translation(translation_request)

        google_client_mock.translate.assert_called_with(
            translation_request.text,
            target_language=translation_request.targetLanguage)

        assert len(translation) == 2
        translation_1 = translation[0]
        translation_2 = translation[1]
        assert translation_1["translatedText"] == "Translated Text 1"
        assert translation_1["input"] == "Text for translation 1"
        assert translation_1["detectedSourceLanguage"] == "en"
        assert translation_2["translatedText"] == "Translated Text 2"
        assert translation_2["input"] == "Text for translation 2"
        assert translation_2["detectedSourceLanguage"] == "lv"
