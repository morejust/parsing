import flask
import requests_cache
from flask import request, jsonify
from newspaper import Article

from htmlTagsExtractor import extract_tags
from googleApiSentiment import get_sentiments
from flask_cors import CORS

requests_cache.install_cache(cache_name='google_api_cache', backend='sqlite', expire_after=180)

app = flask.Flask(__name__)

CORS(app)

app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>AI is working!</h1>
<p>Move your ass and cal the /analyse method with 'url' param.</p>'''

def parse(url):
    try:
        a = Article(url, keep_article_html=True)
        a.download()
        a.parse()
        a.nlp()

        return  {
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
    except Exception as e:
        print(e)
        return { 'error': True, 'description': "'%s' parsing went wrong with error: '%s'" % (url, e)}

@app.route('/analyse', methods=['GET'])
def analyse():
    query_parameters = request.args
    url = query_parameters.get('url')
    result = { 'url': url, 'error': False }

    try:
        result['post'] = parse(url)

        tags, raw_text = extract_tags(result['post']["html"])
        result['html'] = tags
        result['post']['text'] = raw_text

        result['entities'] = get_sentiments(raw_text)
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
