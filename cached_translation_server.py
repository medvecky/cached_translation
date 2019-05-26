from concurrent import futures
import time
import logging

import grpc

from collections import namedtuple

from google_translation import GoogleTranslation
from redis_cache_20 import RedisCache

import cached_translation_pb2
import cached_translation_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

TranslationRequest = namedtuple("TranslationRequest", "text targetLanguage sourceLanguage")


def find_translation(translations, text):
    for translation in translations:
        if translation["input"] == text:
            return translation
    return False


class CachedTranslation(cached_translation_pb2_grpc.CachedTranslationServicer):

    def __init__(self):
        self.cloud_translation = GoogleTranslation()
        self.cache = RedisCache()

    def GetTranslations(self, request, context):

        bad_translation = {"translatedText": "",
                           "detectedSourceLanguage": "",
                           "input": "BAD ARGUMENT"}

        cached_translations = []

        result_translations = []

        translation_request = TranslationRequest(
            text=[],
            targetLanguage=request.targetLanguage,
            sourceLanguage=request.sourceLanguage)

        if len(request.texts):
            for text in request.texts:
                if self.cache.check_cache(text, request.sourceLanguage, request.targetLanguage):
                    translated_text, source = self.cache.get_from_cache(
                        text,
                        request.sourceLanguage,
                        request.targetLanguage)

                    if request.sourceLanguage:
                        translation = {"translatedText": translated_text,
                                       "input": text}
                    else:
                        translation = {"translatedText": translated_text,
                                       "detectedSourceLanguage": source,
                                       "input": text}
                    cached_translations.append(translation)
                else:
                    translation_request.text.append(text)

            if len(translation_request.text):

                try:
                    cloud_translations = self.cloud_translation.get_translation(translation_request)
                except:
                    cloud_translations = [bad_translation]

                for cloud_translation in cloud_translations:
                    if request.sourceLanguage:
                        self.cache.save_to_cache(
                            cloud_translation,
                            request.sourceLanguage,
                            request.targetLanguage)
                    else:
                        self.cache.save_to_cache(
                            cloud_translation,
                            cloud_translation["detectedSourceLanguage"],
                            request.targetLanguage)
            else:
                cloud_translations = []

            for text in request.texts:
                translation = find_translation(cached_translations, text)
                if translation:
                    result_translations.append(translation)
                    continue
                result_translations.append(find_translation(cloud_translations, text))

            print(result_translations)
        else:
            cached_translations.append(bad_translation)

        if not len(result_translations) or not result_translations[0]:
            result_translations = [bad_translation]

        return cached_translation_pb2.TranslationReply(translations=result_translations)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cached_translation_pb2_grpc.add_CachedTranslationServicer_to_server(CachedTranslation(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
