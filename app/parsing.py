from newspaper import Article
from urllib.parse import urlparse

from htmlTagsExtractor import extract_tags
from factsExtractor import extract_facts
from googleApiSentiment import get_sentiments
from keywordsFinder import KeywordsFinder

from caching import get_cached_article, get_cached_features
from caching import cache_article, cache_features

# parsers and classifiers inits
kf = KeywordsFinder()

def check_fake_source(url):
    site = '{uri.netloc}'.format(uri=urlparse(url))

    with open('./data/fakes.csv', 'r') as f:
        fakes = f.readlines()
    fakes = [f.strip() for f in fakes]

    return site in fakes

def download_article(url, cache=True):
    a = Article(url, keep_article_html=True)
    a.download()
    a.parse()
    a.nlp()

    result = {
        "author": ", ".join(a.authors),
        "source": a.source_url[a.source_url.find("//") + 2:].split("/")[0],
        "title": a.title,
        "image": a.top_image,
        "url": a.url,
        "publishedAt": a.publish_date,
        "html": a.article_html,
        "text": a.text,
        "summary": a.summary,
        "keywords": a.keywords,
    }
    if cache:
        cache_article(url, result)
    return result

def get_article(url, cache=True):
    if cache:
        result = get_cached_article(url)
        if result is not None:
            return result

    return download_article(url, cache=cache)

def populate_with_features_old(article):
    url = article['url']
    result = {'url': url, 'error': False, 'post': article, 'fake': False}

    tags, raw_text = extract_tags(result['post']['html'])
    result['html'] = tags
    result['post']['text'] = raw_text
    result['fake'] = check_fake_source(url)
    result['checkFacts'] = extract_facts(result['post'])
    result['stopwords'] = kf.find_keywords(raw_text)
    result['entities'] = get_sentiments(raw_text)

    return result

def get_text_entities(text):
    entities = []
    return entities

def populate_with_features(article, cache=True):
    url = article['url']
    if cache:
        features = get_cached_features(url)
        if features is not None:
            return features

    features = {'url': url, 'error': False, 'article': article}

    tags, raw_text = extract_tags(article['html'])
    features['html_tags'] = tags
    features['article']['text'] = raw_text

    # entity-based features
    features['entities'] = []

    # find key phrases
    facts = extract_facts(article)
    features['entities'].extend({
        'offset': e['offset'],
        'type': 'key_phrase',
        'content': e['content'],
        'properties': {}
    } for e in facts)

    sents_google = get_sentiments(raw_text)
    features['entities'].extend({
        'offset': e['offset'],
        'type': 'sentiment_positive_google' if e["sentiment"] > 0 else "sentiment_negative_google",
        'content': e['content'],
        'properties': {
            'magnitude': e['magnitude'],
            'sentiment': e['sentiment'],
        }
    } for m in sents_google for e in m["mentions"] if e["sentiment"] ** 2 > 0.5 ** 2)  # just not to use np.abs()

    stopwords = kf.find_keywords(raw_text)
    features['entities'].extend({
        'offset': e['offset'],
        'type': e['type'],
        'content': e['content'],
        'properties': {}
    } for e in stopwords)

    # article-based features
    features['features'] = {}
    features['features']['source_had_fake_news'] = check_fake_source(url)
    
    if cache:
        cache_features(url, features)
    return features
