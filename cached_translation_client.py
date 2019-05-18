from __future__ import print_function
import logging

import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

        texts = ["Hello world guys"]
        source_language = "en"
        target_language="ru"

        response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
            texts=texts,
            targetLanguage=target_language,
            sourceLanguage=source_language))


    print(response.translations[0].translatedText)
    print(response.translations[0].input)


if __name__ == '__main__':
    logging.basicConfig()
    run()
