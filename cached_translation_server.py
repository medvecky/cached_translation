from concurrent import futures
import time
import logging

import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class CachedTranslation(cached_translation_pb2_grpc.CachedTranslationServicer):

    def GetTranslation(self, request, context):
        return cached_translation_pb2.TranslationReply(
            translatedText=request.text,
            detectedSourceLanguage=request.targetLanguage,
            input="input stub")


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
