import os
import time
import flask
import random
import requests

from flask import request, jsonify
from flask_cors import CORS

from parsing import get_article, populate_with_features_old

# flask inits
app = flask.Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>AI is working! You are not...</h1>'''

@app.route('/parse', methods=['GET'])
def parse():
    query_parameters = request.args
    url = query_parameters.get('url')

    try:
        article_data = get_article(url)
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

@app.route('/v2/analyse', methods=['GET'])
def new_analyse():
    result = populate_with_features(request.json)
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

@app.route('/v2/get', methods=['GET'])
def get():
    query_parameters = request.args
    url = query_parameters.get('url')

    article = get_article(url)
    article_with_features = populate_with_features_old(article)

    return jsonify(article_with_features)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
