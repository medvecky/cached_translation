from collections import namedtuple
from unittest.mock import MagicMock

import pytest
import redis_cache
import cached_translation_server
import google_translation

Request = namedtuple("Request", "text targetLanguage sourceLanguage")
TranslationRequest = namedtuple("Request", "text targetLanguage sourceLanguage")


class TestCachedTranslation:

    @pytest.fixture
    def get_request(self):
        return namedtuple("Request", "text targetLanguage sourceLanguage")

    @pytest.fixture
    def get_request_1(self):
        return namedtuple("Request", "texts targetLanguage sourceLanguage")

    @pytest.fixture
    def google_client_constructor_mock(self, monkeypatch):
        google_client_mock = MagicMock()
        google_client_constructor_mock = MagicMock(return_value=google_client_mock)
        monkeypatch.setattr("google.cloud.translate.Client", google_client_constructor_mock)
        return google_client_constructor_mock

    @pytest.fixture
    def get_translation_mock(self, monkeypatch):
        get_translation_mock = MagicMock()
        monkeypatch.setattr(google_translation.GoogleTranslation, "get_translation", get_translation_mock)
        return get_translation_mock

    @pytest.fixture
    def save_to_cache_mock(self, monkeypatch):
        save_to_cache_mock = MagicMock()
        monkeypatch.setattr(redis_cache.RedisCache, "save_to_cache", save_to_cache_mock)
        return save_to_cache_mock

    @pytest.fixture
    def handle_request_to_cloud_mock(self, monkeypatch):
        handle_request_to_cloud_mock = MagicMock()
        monkeypatch.setattr(
            cached_translation_server.CachedTranslation,
            "handle_request_to_cloud",
            handle_request_to_cloud_mock)
        return handle_request_to_cloud_mock

    @pytest.fixture
    def cached_translations(self, google_client_constructor_mock):
        cached_translations = cached_translation_server.CachedTranslation()
        return cached_translations

    def test_get_cloud_translations_and_save_to_cache_one_text(
            self,
            cached_translations,
            get_request,
            handle_request_to_cloud_mock):
        request = get_request(text=[], sourceLanguage="en", targetLanguage="ru")
        not_translated_text = ["not translated text"]
        handle_request_to_cloud_mock.return_value = {'Text for translation': ('Translated Text', '')}
        result = cached_translations.get_cloud_translations_and_save_to_cache(request, not_translated_text)
        handle_request_to_cloud_mock.assert_called_with(
            Request(text=[], targetLanguage='ru', sourceLanguage='en'),
            TranslationRequest(text=['not translated text'], targetLanguage='ru', sourceLanguage='en'))
        assert result == {'Text for translation': ('Translated Text', '')}

    def test_get_cloud_translations_and_save_to_cache_few_texts(
            self,
            cached_translations,
            get_request,
            handle_request_to_cloud_mock):
        request = get_request(text=[], sourceLanguage="en", targetLanguage="ru")

        not_translated_text = ["not translated text 1", "not translated text 2"]
        handle_request_to_cloud_mock.return_value = {'Text for translation 1': ('Translated Text 1', ''),
                                                     'Text for translation 2': ('Transalted text 2', '')}
        result = cached_translations.get_cloud_translations_and_save_to_cache(request, not_translated_text)
        handle_request_to_cloud_mock.assert_called_with(
            Request(text=[], targetLanguage='ru', sourceLanguage='en'),
            TranslationRequest(text=['not translated text 1', 'not translated text 2'],
                               targetLanguage='ru',
                               sourceLanguage='en'))
        assert result == {'Text for translation 1': ('Translated Text 1', ''),
                          'Text for translation 2': ('Transalted text 2', '')}

    def test_get_cloud_translations_and_save_to_cache_no_texts(
            self,
            cached_translations,
            get_request,
            handle_request_to_cloud_mock):
        request = get_request(text=[], sourceLanguage="en", targetLanguage="ru")

        not_translated_text = []
        result = cached_translations.get_cloud_translations_and_save_to_cache(request, not_translated_text)
        handle_request_to_cloud_mock.assert_not_called
        assert result == []

    def test_get_cloud_translations_and_save_to_cache_many_result(
            self,
            cached_translations,
            get_request,
            handle_request_to_cloud_mock):
        request = get_request(text=[], sourceLanguage="en", targetLanguage="ru")
        not_translated_text = ["not translated text"]
        handle_request_to_cloud_mock.return_value = {'Text for translation': ('Translated Text', '')}
        result = cached_translations.get_cloud_translations_and_save_to_cache(request, not_translated_text)
        assert result == {'Text for translation': ('Translated Text', '')}

    def test_handle_request_to_cloud_with_source(
            self,
            get_request,
            get_translation_mock,
            save_to_cache_mock,
            cached_translations):
        request = get_request(text=["text"], sourceLanguage="en", targetLanguage="ru")

        get_translation_mock.return_value = [{
            "translatedText": "Translated Text",
            "input": "Text for translation"}]

        result = cached_translations.handle_request_to_cloud(request, request)

        get_translation_mock.assert_called_with((Request(text=['text'], targetLanguage='ru', sourceLanguage='en')))
        save_to_cache_mock.assert_called_with(
            [{'translatedText': 'Translated Text', 'input': 'Text for translation'}],
            'en',
            'ru')

        assert result == {'Text for translation': ('Translated Text', '')}

    def test_handle_multi_string_request_to_cloud_with_source(
            self,
            get_request,
            get_translation_mock,
            save_to_cache_mock,
            cached_translations):
        request = get_request(text=["text1", "text2"], sourceLanguage="en", targetLanguage="ru")

        get_translation_mock.return_value = [{
            "translatedText": "Translated Text 1",
            "input": "Text for translation 1"},
            {"translatedText": "Translated Text 2",
             "input": "Text for translation 2"}]

        result = cached_translations.handle_request_to_cloud(request, request)

        get_translation_mock.assert_called_with(
            Request(text=['text1', 'text2'], targetLanguage='ru', sourceLanguage='en'))
        save_to_cache_mock.assert_called_with(
            [{'translatedText': 'Translated Text 1', 'input': 'Text for translation 1'},
             {'translatedText': 'Translated Text 2', 'input': 'Text for translation 2'}],
            'en', 'ru')

        assert result == {'Text for translation 1': ('Translated Text 1', ''),
                          'Text for translation 2': ('Translated Text 2', '')}

    def test_handle_request_to_cloud_without_source(
            self,
            get_request,
            get_translation_mock,
            save_to_cache_mock,
            cached_translations):
        request = get_request(text=["text"], sourceLanguage="", targetLanguage="ru")

        get_translation_mock.return_value = [{
            "translatedText": "Translated Text",
            "input": "Text for translation",
            "detectedSourceLanguage": "en"}]

        result = cached_translations.handle_request_to_cloud(request, request)

        get_translation_mock.assert_called_with((Request(text=['text'], targetLanguage='ru', sourceLanguage='')))
        save_to_cache_mock.assert_called_with(
            [{'translatedText': 'Translated Text', 'input': 'Text for translation', 'detectedSourceLanguage': 'en'}],
            '',
            'ru')

        assert result == {'Text for translation': ('Translated Text', 'en')}

    def test_handle_multi_string_request_to_cloud_without_source(
            self,
            get_request,
            get_translation_mock,
            save_to_cache_mock,
            cached_translations):
        request = get_request(text=["text1", "text2"], sourceLanguage="", targetLanguage="ru")

        get_translation_mock.return_value = [{
            "translatedText": "Translated Text 1",
            "input": "Text for translation 1",
            "detectedSourceLanguage": "en"},
            {"translatedText": "Translated Text 2",
             "input": "Text for translation 2",
             "detectedSourceLanguage": "lv"}]

        result = cached_translations.handle_request_to_cloud(request, request)

        get_translation_mock.assert_called_with(
            Request(text=['text1', 'text2'], targetLanguage='ru', sourceLanguage=''))
        save_to_cache_mock.assert_called_with(
            [{'translatedText': 'Translated Text 1', 'input': 'Text for translation 1', "detectedSourceLanguage": "en"},
             {'translatedText': 'Translated Text 2', 'input': 'Text for translation 2',
              "detectedSourceLanguage": "lv"}],
            '', 'ru')

        assert result == {'Text for translation 1': ('Translated Text 1', 'en'),
                          'Text for translation 2': ('Translated Text 2', 'lv')}

    def test_handle_request_to_cloud_with_bad_param(
            self,
            get_request,
            get_translation_mock,
            save_to_cache_mock,
            cached_translations):
        request = get_request(text=["text"], sourceLanguage="", targetLanguage="ru")

        get_translation_mock.side_effect = Exception

        result = cached_translations.handle_request_to_cloud(request, request)

        get_translation_mock.assert_called_with((Request(text=['text'], targetLanguage='ru', sourceLanguage='')))
        save_to_cache_mock.assert_not_called()

        assert result == {'BAD ARGUMENT': ('', '')}

    def test_merge_translations_mix(self, cached_translations, get_request_1):
        request = get_request_1(texts=["text 1", "text 2", "text 3", "text 4"], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {
            "text 2": ("trans 2", ""),
            "text 4": ("trans 4", "")
        }

        cloud_translations = {
            "text 1": ("trans 1", ""),
            "text 3": ("trans 3", "")
        }
        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        assert result == [{'translatedText': 'trans 1', 'detectedSourceLanguage': '', 'input': 'text 1'},
                          {'translatedText': 'trans 2', 'detectedSourceLanguage': '', 'input': 'text 2'},
                          {'translatedText': 'trans 3', 'detectedSourceLanguage': '', 'input': 'text 3'},
                          {'translatedText': 'trans 4', 'detectedSourceLanguage': '', 'input': 'text 4'}]

    def test_merge_translations_cached_only(self, cached_translations, get_request_1):
        request = get_request_1(texts=["text 1", "text 2"], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {
            "text 1": ("trans 1", ""),
            "text 2": ("trans 2", "")
        }

        cloud_translations = {}
        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        assert result == [{'translatedText': 'trans 1', 'detectedSourceLanguage': '', 'input': 'text 1'},
                          {'translatedText': 'trans 2', 'detectedSourceLanguage': '', 'input': 'text 2'}]

    def test_merge_translations_cloud_only(self, cached_translations, get_request_1):
        request = get_request_1(texts=["text 1", "text 2"], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {}

        cloud_translations = {
            "text 1": ("trans 1", ""),
            "text 2": ("trans 2", "")
        }
        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        assert result == [{'translatedText': 'trans 1', 'detectedSourceLanguage': '', 'input': 'text 1'},
                          {'translatedText': 'trans 2', 'detectedSourceLanguage': '', 'input': 'text 2'}]

    def test_merge_translations_no_texts(self, cached_translations, get_request_1):
        request = get_request_1(texts=[], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {}

        cloud_translations = {}
        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        assert result == [{'translatedText': '', 'detectedSourceLanguage': '', 'input': 'BAD ARGUMENT'}]

    def test_merge_translations_missed_text_from_cloud(self, cached_translations, get_request_1):
        request = get_request_1(texts=["text 1", "text 2", "text 3", "text 4"], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {
            "text 1": ("trans 1", ""),
            "text 2": ("trans 3", "")
        }

        cloud_translations = {}
        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        assert result == [{'translatedText': 'trans 1', 'detectedSourceLanguage': '', 'input': 'text 1'},
                          {'translatedText': 'trans 3', 'detectedSourceLanguage': '', 'input': 'text 2'},
                          False, False]

    def test_merge_translations_missed_text_from_cache(self, cached_translations, get_request_1):
        request = get_request_1(texts=["text 1", "text 2", "text 3", "text 4"], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {}

        cloud_translations = {"text 2": ("trans 2", ""),
                              "text 4": ("trans 4", "")}

        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        print(result)

        assert result == [{'translatedText': '', 'detectedSourceLanguage': '', 'input': 'BAD ARGUMENT'}]

    def test_merge_translations_missed_texts(self, cached_translations, get_request_1):
        request = get_request_1(texts=["text 1", "text 2", "text 3", "text 4"], sourceLanguage="", targetLanguage="ru")
        cached_translations_dic = {}

        cloud_translations = {}

        result = cached_translations.merge_translations(request, cached_translations_dic, cloud_translations)

        print(result)

        assert result == [{'translatedText': '', 'detectedSourceLanguage': '', 'input': 'BAD ARGUMENT'}]
