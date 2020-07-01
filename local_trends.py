from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import twitter_credentials
import json


# Twitter Authorization

class TwitterAuthorization():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

# Twitter Client 

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthorization().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_user_recent_timeline(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets



if __name__ == '__main__':
    # fetching user info
    twitter_client = TwitterClient()
    print( twitter_client.twitter_client.trends_closest(74.5698, 42.8746))
    # trend = twitter_client.twitter_client.trends_place(2972)
    # trends = json.loads(json.dumps(trend, indent=2))
    
    # print(trends[0]['created_at'])