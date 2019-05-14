from __future__ import print_function
import logging

import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

        while True:
            text = input("Enter text for translation: ")

            if text == "EXIT!":
                break

            source_language = input("Enter source language: ")
            target_language = input("Enter target language: ")

            response = stub.GetTranslation(cached_translation_pb2.TranslationRequest(
                text=text,
                targetLanguage=target_language,
                sourceLanguage=source_language))
            print("translatedText: " + response.translatedText)
            print("detectedSourceLanguage: " + response.detectedSourceLanguage)
            print("input: " + response.input)


if __name__ == '__main__':
    logging.basicConfig()
    run()
