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
    if text in translations:
        tmp = translations[text]
        translation = {"translatedText": tmp[0],
                       "detectedSourceLanguage": tmp[1],
                       "input": text}
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

        cached_translations = {}

        result_translations = []

        cloud_translations = {}

        cloud_responses = []

        translation_request = TranslationRequest(
            text=[],
            targetLanguage=request.targetLanguage,
            sourceLanguage=request.sourceLanguage)

        if len(request.texts):
            cached_translations, not_translated_texts = self.cache.get_from_cache(
                request.texts,
                request.sourceLanguage,
                request.targetLanguage)

            print("Cached translations")
            print(cached_translations)
            print("Not translated texts")
            print(not_translated_texts)
            translation_request.text.extend(not_translated_texts)

            if len(translation_request.text):
                try:
                    cloud_responses = self.cloud_translation.get_translation(translation_request)
                    self.cache.save_to_cache(cloud_responses, request.sourceLanguage, request.targetLanguage)
                    for cloud_response in cloud_responses:
                        if request.sourceLanguage:
                            cloud_translations[cloud_response["input"]] = (cloud_response["translatedText"], "")
                        else:
                            cloud_translations[cloud_response["input"]] = (cloud_response["translatedText"],
                                                                           cloud_response["detectedSourceLanguage"])
                except:
                    cloud_translations[bad_translation["input"]] = ("", "")
            else:
                cloud_translations = []


            print("Cached translations")
            print(cached_translations)
            print("Cloud transaltions")
            print(cloud_translations)
            for text in request.texts:
                translation = find_translation(cached_translations, text)
                if translation:
                    result_translations.append(translation)
                    continue
                result_translations.append(find_translation(cloud_translations, text))

            print("Result tranlations")
            print(result_translations)
        else:
            cached_translations[bad_translation["input"]] = ("", "")

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
