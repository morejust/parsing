import flask
from flask import request, jsonify
from newspaper import Article

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>API is working!</h1>
<p>Move your ass and cal the /parse method with 'url' param.</p>'''

@app.route('/parse', methods=['GET'])
def parse():
    query_parameters = request.args
    url = query_parameters.get('url')

    a = Article(url, keep_article_html=True)
    a.download()
    a.parse()
    a.nlp()
    
    source = a.source_url[a.source_url.find("//") + 2:].split("/")[0]
    features = {
        "author": ", ".join(a.authors),
        "source": source,
        "title": a.title,
        "image": a.top_image,
        "url": a.url,
        "publishedAt": a.publish_date,
        "html": a.article_html,
        "text": a.text,
        "summary": a.summary,
        "keywords": a.keywords,
    }
    return jsonify(features)


if __name__ == "__main__":
    app.run(host='0.0.0.0')