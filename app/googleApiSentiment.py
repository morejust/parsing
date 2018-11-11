import sys
import os
import six

from google.cloud import language

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google_api_cred.json"

def entity_sentiment_text(text):
    """Detects entity sentiment in the provided text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    document = language.types.Document(
        content=text.encode('utf-8'),
        type=language.enums.Document.Type.PLAIN_TEXT, 
        language='en'
    )

    # Detect and send native Python encoding to receive correct word offsets.
    encoding = language.enums.EncodingType.UTF32
    if sys.maxunicode == 65535:
        encoding = language.enums.EncodingType.UTF16

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
        if mention.sentiment.score.real == 0:
            continue
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
        if features["sentiment"] == 0:
            continue
        all_sentiments_features.append(features)
    return all_sentiments_features