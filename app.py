import flask
from flask import request, jsonify
from newspaper import Article

from htmlTagsExtractor import extract_tags
from googleApiSentiment import get_sentiments

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>AI is working!</h1>
<p>Move your ass and cal the /parse method with 'url' param.</p>'''

def parse(url):
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

@app.route('/analyse', methods=['GET'])
def analyse():
    query_parameters = request.args
    url = query_parameters.get('url')
    result = { 'url': url, 'error': False}

    try:
        result['post'] = parse(url)
        
        tags, raw_text = extract_tags(result['post']["html"])
        result['html'] = tags
        result['post']['text'] = raw_text

        result['entities'] = get_sentiments(raw_text)
    except Exception as e:
        print(e)
        result["error"] = True
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0')