from concurrent import futures
import time
import logging

import grpc

from google_translation import GoogleTranslation
from redis_cache import RedisCache

import cached_translation_pb2
import cached_translation_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class CachedTranslation(cached_translation_pb2_grpc.CachedTranslationServicer):

    def __init__(self):
        self.cloud_translation = GoogleTranslation()
        self.cache = RedisCache()

    def GetTranslation(self, request, context):
        key = request.text + ":" + request.targetLanguage

        if request.sourceLanguage:
            key += ":" + request.sourceLanguage

        print(key)

        if self.cache.check_cache(key):
            print("Get from cache")
            translation = self.cache.get_from_cache(key)
        else:
            try:
                translation = self.cloud_translation.get_translation(request)
                self.cache.save_to_cache(key, translation)
                print("Save to cache")
            except:
                translation = {"translatedText": "", "detectedSourceLanguage": "", "input": "BAD ARGUMENT" }

        if request.sourceLanguage:
            return cached_translation_pb2.TranslationReply(
                translatedText=translation["translatedText"],
                detectedSourceLanguage="",
                input=translation["input"])
        else:
            return cached_translation_pb2.TranslationReply(
                translatedText=translation["translatedText"],
                detectedSourceLanguage=translation["detectedSourceLanguage"],
                input=translation["input"])


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
