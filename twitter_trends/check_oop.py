from local_trends import TwitterAuthorization
from local_trends import TwitterClient

twitter_client = TwitterClient()
print( twitter_client.twitter_client.trends_closest(74.5698, 42.8746))