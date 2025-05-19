FROM alpine

LABEL maintainer "Roman Dodin <dodin.roman@gmail.com> and Daniil Okhlopkov <okhlopkov.com>"
LABEL description "Nginx + uWSGI + Flask based on Alpine Linux and managed by Supervisord"

ENV LDFLAGS=-L/usr/lib/x86_64-linux-gnu/

# Copy python requirements file
COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache \
    gcc \
    python3 \
    py3-pip \
    python3-dev \
    bash \
    nginx \ 
    uwsgi \
    uwsgi-python3 \
    supervisor \ 
    # For lxml
    alpine-sdk libxml2-dev libxslt-dev \
    # For Pillow
    musl-dev jpeg-dev zlib-dev openjpeg-dev && \
    pip3 install --break-system-packages --upgrade pip setuptools && \
    pip3 install --break-system-packages -r /tmp/requirements.txt && \
    rm -f /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

# Download NLTK corporas
# RUN curl https://raw.githubusercontent.com/codelucas/newspaper/master/download_corpora.py | python3
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data punkt brown maxent_treebank_pos_tagger movie_reviews wordnet stopwords

# Copy the Nginx global conf
COPY nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY flask-site-nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf

# Add demo app
COPY ./app /app
WORKDIR /app

CMD ["/usr/bin/supervisord"]