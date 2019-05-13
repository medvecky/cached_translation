from concurrent import futures
import time
import logging

import grpc

from google.cloud import translate

import cached_translation_pb2
import cached_translation_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class CachedTranslation(cached_translation_pb2_grpc.CachedTranslationServicer):

    def __init__(self):
        self.translate_client = translate.Client()

    def GetTranslation(self, request, context):
        translation = self.GetGoogleTranslation(request)

        return cached_translation_pb2.TranslationReply(
            translatedText=translation["translatedText"],
            detectedSourceLanguage=translation["detectedSourceLanguage"],
            input=translation["input"])

    def GetTranslationWithSource(self, request, context):
        translation = self.GetGoogleTranslationWithSource(request)

        print(translation)

        return cached_translation_pb2.TranslationWithSourceReply(
            translatedText=translation["translatedText"],
            input=translation["input"])

    def GetGoogleTranslation(self, request):
        translation = self.translate_client.translate(
            request.text,
            target_language=request.targetLanguage)
        return translation

    def GetGoogleTranslationWithSource(self, request):
        translation = self.translate_client.translate(
            request.text,
            source_language=request.sourceLanguage,
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
