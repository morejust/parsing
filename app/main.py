import os
import time
import flask
import random
import requests

from flask import request, jsonify
from flask_cors import CORS

from htmlTagsExtractor import extract_tags
from parsing import get_article
from parsing import populate_with_features_old, populate_with_features
from parsing import get_text_entities

# flask inits
app = flask.Flask(__name__, static_url_path='/static')
CORS(app)

# HACK: save Google API key from env vars to file
if not os.path.isfile('google_api_cred.json') and os.getenv('GOOGLE_API_JSON'):
    with open('google_api_cred.json', 'w') as f:
        f.write(str(os.getenv('GOOGLE_API_JSON')))

@app.route('/', methods=['GET'])
def home():
    return '''<h1>AI is working! You are not...</h1>'''

@app.route('/parse', methods=['GET'])
def parse():
    query_parameters = request.args
    url = query_parameters.get('url')

    try:
        article_data = get_article(url)
        
        tags, raw_text = extract_tags(article_data['html'])
        article_data["text"] = raw_text
        article_data["html_tags"] = tags
        return jsonify(article_data)

    except Exception as e:
        print(e)
        return jsonify({
            'error': True, 
            'description': "'%s' parsing went wrong with error: '%s'" % (url, str(e))
        })

@app.route('/analyse', methods=['POST'])
def analyse():
    try:
        result = populate_with_features_old(request.json)
    except Exception as e:
        print(e)
        result = {"error": True, "description": str(e)}
    return jsonify(result)
    
@app.route('/v2/analyse', methods=['POST'])
def new_analyse():
    result = populate_with_features(request.json)
    return jsonify(result)

@app.route('/v3/analyse', methods=['POST'])
def new_new_analyse():
    try:
        text = request.json["text"]
        result = get_text_entities(text)
    except Exception as e:
        print(e)
        result = {"error": True, "description": str(e)}
    return jsonify(result)

@app.route('/search', methods=['GET'])
def source_articles():
    query_parameters = request.args
    query = query_parameters.get('q')

    if query is None:
        return jsonify({'error': True, 'description': 'No query'})

    result = {'q': query, 'error': False, 'url': ''}
    try:
        api_token = os.getenv('NEWS_API_TOKEN', '') 
        qurl = 'https://newsapi.org/v2/everything?q=%s&language=en&sortBy=popularity&apiKey=%s'
        r = requests.get(qurl % (query, api_token))
        print(r.json())
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

@app.route('/v2/get', methods=['GET'])
def get_articles():
    query_parameters = request.args
    url = query_parameters.get('url')

    article = get_article(url)
    article_with_features = populate_with_features(article)

    return jsonify(article_with_features)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
