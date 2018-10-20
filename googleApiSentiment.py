import sys
import os
import six

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google_api_cred.json"

def entity_sentiment_text(text):
    """Detects entity sentiment in the provided text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    # Detect and send native Python encoding to receive correct word offsets.
    encoding = enums.EncodingType.UTF32
    if sys.maxunicode == 65535:
        encoding = enums.EncodingType.UTF16

    result = client.analyze_entity_sentiment(document, encoding)
    return result


def extract_entity_features(entity):
    features = {}
    features["name"] = entity.name
    features["salience"] = entity.salience.real
    features["sentiment"] = entity.sentiment.score.real
    features["magnitude"] = entity.sentiment.magnitude.real
    features["type"] = "sentiment"

    features['mentions'] = []
    for mention in entity.mentions:
        f = {}
        f["offset"] = mention.text.begin_offset
        f["content"] = mention.text.content
        f["magnitude"] = mention.sentiment.magnitude.real
        f["sentiment"] = mention.sentiment.score.real
        f["type"] = mention.type
        features['mentions'].append(f)
    return features

def get_sentiments(text):
    google_api_result = entity_sentiment_text(text)
    all_sentiments_features = []
    for entity in google_api_result.entities:
        features = extract_entity_features(entity)
        all_sentiments_features.append(features)
    return all_sentiments_features