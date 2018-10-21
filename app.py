import os
import time
import flask
import random
import appdirs
import requests
import requests_cache

from flask import request, jsonify
from newspaper import Article
from urllib.parse import urlparse
from flask_cors import CORS

from htmlTagsExtractor import extract_tags
from factsExtractor import extract_facts
from googleApiSentiment import get_sentiments
from keywordsFinder import KeywordsFinder

__program__ = 'google_cache'

# determine platform-specific user cache directory
cache_dir = appdirs.user_cache_dir(__program__)

# ensure cache directory exists
os.makedirs(cache_dir, exist_ok=True)

requests_cache.install_cache(
    cache_name=os.path.join(cache_dir, __program__), 
    expire_after=50000
)

# flask inits
app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

# parsers and classifiers inits
kf = KeywordsFinder()

def check_fake_source(url):
    site = '{uri.netloc}'.format(uri=urlparse(url))

    with open('./data/fakes.csv', 'r') as f:
        fakes = f.readlines()
    fakes = [f.strip() for f in fakes]

    return site in fakes

@app.route('/', methods=['GET'])
def home():
    return '''<h1>AI is working! You are not...</h1>'''

@app.route('/parse', methods=['GET'])
def parse():
    query_parameters = request.args
    url = query_parameters.get('url')
    if 'clear_cache' in query_parameters and query_parameters.get('clear_cache') == '1':
        requests_cache.clear()

    try:
        a = Article(url, keep_article_html=True)
        a.download()
        a.parse()
        a.nlp()

        return jsonify({
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
        })
    except Exception as e:
        print(e)
        return jsonify({
            'error': True, 
            'description': "'%s' parsing went wrong with error: '%s'" % (url, str(e))
        })

@app.route('/analyse', methods=['POST'])
def analyse():
    jso = request.json
    url = jso['url']
    result = {'url': url, 'error': False, 'post': jso, 'fake': False}

    # TODO: Allow to pass the url and perform /parse and /analyse at the same time.
    try:
        tags, raw_text = extract_tags(result['post']['html'])
        result['html'] = tags
        result['post']['text'] = raw_text
        result['fake'] = check_fake_source(url)
        result['checkFacts'] = extract_facts(result['post'])
        result['keywords'] = kf.find_keywords(raw_text)

        result['entities'] = get_sentiments(raw_text)

    except Exception as e:
        print(e)
        result["error"] = True
        result["description"] = str(e)

    return jsonify(result)

@app.route('/search', methods=['GET'])
def source_articles():
    query_parameters = request.args
    query = query_parameters.get('q')

    if query is None:
        return jsonify({'error': True, 'description': 'No query'})

    result = {'q': query, 'error': False, 'url': ''}
    try:
        api_token = '61b5063e2cdb47d3913945c311932ab3'  # key that was taken from mainpage
        qurl = 'https://newsapi.org/v2/everything?q=%s&language=en&from=2018-10-20&to=2018-10-20&sortBy=popularity&apiKey=%s'
        r = requests.get(qurl % (query, api_token))
        if len(r.json()['articles']) == 0:
            result['error'] = True
            return jsonify(result)

        article = random.choice(r.json()['articles'])
        result['url'] = article['url']

    except Exception as e:
        print(e)
        result['error'] = True
        result['description'] = str(e)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
