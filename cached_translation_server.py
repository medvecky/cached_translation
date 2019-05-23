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


class CachedTranslation(cached_translation_pb2_grpc.CachedTranslationServicer):

    def __init__(self):
        self.cloud_translation = GoogleTranslation()
        self.cache = RedisCache()

    def GetTranslations(self, request, context):

        translations = []

        if len(request.texts):
            for text in request.texts:
                translation_request = TranslationRequest(
                    text=text,
                    targetLanguage=request.targetLanguage,
                    sourceLanguage=request.sourceLanguage)

                translations.append(self.GetTranslation(translation_request))
        else:
            translation = {"translatedText": "",
                           "detectedSourceLanguage": "",
                           "input": "BAD ARGUMENT"}
            translations.append(translation)
        return cached_translation_pb2.TranslationReply(translations=translations)


    def GetTranslation(self, translation_request):

        if self.cache.check_cache(
                translation_request.text,
                translation_request.sourceLanguage,
                translation_request.targetLanguage):
            print("Get from cache")
            translated_text, source = self.cache.get_from_cache(
                translation_request.text,
                translation_request.sourceLanguage,
                translation_request.targetLanguage)
            if translation_request.sourceLanguage:
                translation = {"translatedText": translated_text,
                               "detectedSourceLanguage": "",
                               "input": translation_request.text}
            else:
                translation = {"translatedText": translated_text,
                               "detectedSourceLanguage": source,
                               "input": translation_request.text}
        else:
            try:
                translation = self.cloud_translation.get_translation(translation_request)

                if translation_request.sourceLanguage:
                    self.cache.save_to_cache(
                        translation,
                        translation_request.sourceLanguage,
                        translation_request.targetLanguage)
                else:
                    self.cache.save_to_cache(
                        translation,
                        translation["detectedSourceLanguage"],
                        translation_request.targetLanguage)
                print("Save to cache")
            except:
                translation = {"translatedText": "",
                               "detectedSourceLanguage": "",
                               "input": "BAD ARGUMENT"}
        return translation


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
