from concurrent import futures
import time
import logging

import grpc

from google.cloud import translate

import cached_translation_pb2
import cached_translation_pb2_grpc

import os
import urllib
import redis

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class CachedTranslation(cached_translation_pb2_grpc.CachedTranslationServicer):

    def __init__(self):
        self.translate_client = translate.Client()
        url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
        self.redis = redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            charset="utf-8",
            decode_responses=True)

    def GetTranslation(self, request, context):
        key = request.text + ":" + request.targetLanguage

        if request.sourceLanguage:
            key += ":" + request.sourceLanguage

        print(key)

        if self.redis.exists(key):
            print("Get from cache")
            translation = self.redis.hgetall(key)
        else:
            try:
                translation = self.GetGoogleTranslation(request)
                self.redis.hmset(key, translation)
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

    def GetGoogleTranslation(self, request):
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
