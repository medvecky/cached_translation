from __future__ import print_function
import logging

import grpc

import cached_translation_pb2
import cached_translation_pb2_grpc

import argparse

parser = argparse.ArgumentParser(description="CLI for cached translation")
parser.add_argument("--source", metavar="Source", type=str)
parser.add_argument("--to", metavar="Target", type=str, required=True)
parser.add_argument("strings", metavar="Text", type=str, nargs="+")

args = parser.parse_args()


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = cached_translation_pb2_grpc.CachedTranslationStub(channel)

        texts = args.strings
        source_language = args.source
        target_language = args.to

        response = stub.GetTranslations(cached_translation_pb2.TranslationRequest(
            texts=texts,
            targetLanguage=target_language,
            sourceLanguage=source_language))

    for translation in response.translations:
        print(translation.translatedText)
        print(translation.detectedSourceLanguage)
        print(translation.input)


if __name__ == '__main__':
    logging.basicConfig()
    run()
