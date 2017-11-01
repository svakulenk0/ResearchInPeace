#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, Markup

from twitter_requests import *

from twython.exceptions import TwythonError

app = Flask(__name__)


@app.route("/listen/<list_name>")
def list_hashtags(list_name):
    '''RESTful web service that takes listname as a parameter e.g. wien'''
    return render_template('hashtags.html',
                           hashtags=Markup(get_hashtags(list_name)))
    # return Response(get_hashtags())


# @app.route("/timeline/")
# def generate_timeline():
#     '''Shows the most popular recent tweets'''
#     return render_template('timeline.html',
#                            top_tweets=get_timeline_for_lists())


@app.errorhandler(TwythonError)
def twython_error(e):
    return render_template('error.html'), 404


@app.route("/stats/")
def list_all_stats():
    '''Shows my Twitter lists statistics'''
    return render_template('stats.html',
                           stats=get_stats())


@app.route("/all_my_lists/")
def list_all_lists():
    '''Shows my all Twitter lists statistics'''
    return render_template('my_lists.html',
                           lists=retrieve_my_lists())

@app.route("/lists/")
def list_selected_lists():
    '''Shows my selected Twitter lists statistics'''
    return render_template('lists.html')


@app.route("/list_stats/<list_name>")
def list_stats(list_name):
    '''Shows my Twitter lists statistics'''
    return render_template('stats.html',
                           stats=get_stats([list_name], get_list_tweets))


@app.route("/hashtag_stats/<hashtag>")
def hashtag_stats(hashtag):
    '''Shows my Twitter lists statistics'''
    return render_template('stats.html',
                           stats=get_stats([hashtag], get_hashtag_tweets, True))

# def app(environ, start_response):
#     # Gunicorn server implementation
#     data = b"Hello, World!\n"
#     start_response("200 OK", [
#         ("Content-Type", "text/plain"),
#         ("Content-Length", str(len(data)))
#     ])
#     return iter([data])


if __name__ == "__main__":
    # host='127.0.0.1'
    app.debug = True
    app.run()
