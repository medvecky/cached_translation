from __future__ import print_function
import logging

import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)
        response = stub.GetTranslation(cached_translation_pb2.TranslationRequest(
            text="tout",
            targetLanguage="ru"))
        print("translatedText: " + response.translatedText)
        print("detectedSourceLanguage: " + response.detectedSourceLanguage)
        print("input: " + response.input)

        response = stub.GetTranslationWithSource(cached_translation_pb2.TranslationWithSourceRequest(
            text="tout",
            targetLanguage="ru",
            sourceLanguage="en"))

        print("translatedText: " + response.translatedText)
        print("input: " + response.input)


if __name__ == '__main__':
    logging.basicConfig()
    run()
