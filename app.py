import flask
import requests_cache
import time
import appdirs
import os
from flask import request, jsonify
from newspaper import Article

from htmlTagsExtractor import extract_tags
from googleApiSentiment import get_sentiments
from flask_cors import CORS
__program__ = 'google_cache'

# determine platform-specific user cache directory
cache_dir = appdirs.user_cache_dir(__program__)

# ensure cache directory exists
os.makedirs(cache_dir, exist_ok=True)

requests_cache.install_cache(
    cache_name=os.path.join(cache_dir, __program__),expire_after=500000
)
#requests_cache.install_cache(cache_name='google_api_cache', backend='sqlite', expire_after=500000)
#requests_cache.install_cache()

app = flask.Flask(__name__)

CORS(app)

app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome page!</h1>'''

@app.route('/parse', methods=['GET'])
def parse():
    query_parameters = request.args
    url = query_parameters.get('url')
    if "clear_cache" in query_parameters:
        if query_parameters.get('clear_cache')=='1':
            requests_cache.clear()
            #print("It's clearing 1!\n")
    try:
        a = Article(url, keep_article_html=True)
        a.download()
        a.parse()
        a.nlp()

        return  jsonify({
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
        return jsonify({ 'error': True, 'description': "'%s' parsing went wrong with error: '%s'" % (url, e)})

@app.route('/analyse', methods=['POST'])
def analyse():

    # query_parameters = request.args
    # if "clear_cache" in query_parameters:
    #     if query_parameters.get('clear_cache')=='1':
    #         requests_cache.clear()
    #         print("It's clearing 2 !\n")
    url = "" #query_parameters.get('url')
    jso = request.json
    result = { 'url': url, 'error': False , 'post':jso}

    # result['post']['html'] = jso['html']
    # result['post']['text'] = jso['text']

    try:
        before = time.ctime(int(time.time()))
        #result['post'] = parse(url)

        tags, raw_text = extract_tags(result['post']["html"])
        result['html'] = tags
        result['post']['text'] = raw_text

        result['entities'] = get_sentiments(raw_text)

        after = time.ctime(int(time.time()))

        print("Time: {0} / Used Cache: {1}".format(before, after))

    except Exception as e:
        print(e)
        result["error"] = True
        result["description"] = e
    return jsonify(result)

@app.route('/sourceArticles', methods=['GET'])
def source_articles():
    query_parameters = request.args
    source = query_parameters.get('source')
    if source is None:
        return jsonify({'error': True, 'description': 'No source provided'})
    result = { 'source': source, 'error': False, 'acticles': [] }
    try:
        source_urls = ['url.com', 'url1.com', 'rul2.com']
        result['acticles'] = [{ 'url': u } for u in source_urls]

    except Exception as e:
        print(e)
        result["error"] = True
        result["description"] = e
    return jsonify(result)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
