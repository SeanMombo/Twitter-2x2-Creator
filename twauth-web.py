from __future__ import unicode_literals
import os
from flask import Flask, render_template, request, url_for, redirect, session
import tweepy
import oauth2 as oauth
import urllib.request
import urllib.parse
import urllib.error
import json

app = Flask(__name__)
app.static_folder = 'static'
app.debug = True
app.secret_key = 'badsecretkey'

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authorize_url = 'https://api.twitter.com/oauth/authorize'
show_user_url = 'https://api.twitter.com/2/users/by'


# Support keys from environment vars (Heroku).
# app.config['APP_CONSUMER_KEY'] = os.getenv(
#     'TWAUTH_APP_CONSUMER_KEY', 'API_Key_from_Twitter')
# app.config['APP_CONSUMER_SECRET'] = os.getenv(
#     'TWAUTH_APP_CONSUMER_SECRET', 'API_Secret_from_Twitter')

# alternatively, add your key and secret to config.cfg
# config.cfg should look like:
# APP_CONSUMER_KEY = 'API_Key_from_Twitter'
# APP_CONSUMER_SECRET = 'API_Secret_from_Twitter'

app.config.from_pyfile('config.cfg', silent=True)


oauth_store = {}


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/start')
def start():
    
    auth = tweepy.OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'], app.config['CALLBACK'])
    print(auth)
    url = auth.get_authorization_url()
    session['request_token'] = auth.request_token
    return redirect(url)

@app.route('/callback')
def callback():

    request_token = session['request_token']
    del session['request_token']

    auth = tweepy.OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'], app.config['CALLBACK'])
    auth.request_token = request_token
    verifier = request.args.get('oauth_verifier')
    auth.get_access_token(verifier)
    session['token'] = (auth.access_token, auth.access_token_secret)

    return redirect('/grid')

@app.route('/grid', methods=['GET', 'POST'])
def grid():
    # captain_mrs 2x2 thread
    # https://twitter.com/captain_mrs/status/1346473885789655041?s=20

    if request.method == 'POST':

        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'], app.config['CALLBACK'])
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit=True)

        tweet_url = 'https://twitter.com/captain_mrs/status/1346473885789655041?s=20'
        tweet_id = tweet_url.split('/')[-1].split('?')[0]
        screen_name = 'captain_mrs'
        q_str = 'to:' + screen_name + ' conversation_id:' + tweet_id

        _max_queries = 5
        n = 500
        ct = 1

        tweets = tweet_batch = api.search(q=q_str, since_id=tweet_id, count=n, result_type='mixed', include_entities=True)
        tweets = tweets['statuses']
        tweet_batch = tweet_batch['statuses']

        #batch the search requests to get around 100 limit
        while len(tweets) < n and ct < _max_queries:
            max_id = 9999999999999999999
            #get smallest id from returned tweets 
            for a in tweet_batch:
                if a['id'] < max_id:
                    max_id = a['id']

            tweet_batch = api.search(q=q_str, since_id=tweet_id, count=n - len(tweets), result_type='mixed', include_entities=True, max_id=max_id)['statuses']         
            tweets.extend(tweet_batch)
            ct += 1



        lis = []
        screen_names = []
        pfp_urls = []
        for t in tweets:
            reply_id = t['in_reply_to_status_id_str']
            cur_id = t['user']['id']
            if reply_id == tweet_id and cur_id not in lis:
                screen_names.append(t['user']['screen_name'])
                pfp_urls.append(t['user']['profile_image_url_https'])
                lis.append(cur_id)

        print(screen_names)

        # with open('./static/names.txt') as f:
        #     names = f.read().splitlines()

        # count = 0;
        # for n in names:
        #     if n in screen_names:
        #         count+=1

        return render_template('grid.html', pfp_urls=pfp_urls, access_token_url=access_token_url) 

    return render_template('grid.html', data=[], access_token_url=access_token_url)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500

  
if __name__ == '__main__':
    app.run()
