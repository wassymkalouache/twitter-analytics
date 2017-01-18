import tweepy
import csv

consumer_key='X1bliquVsgsPkW1nVDbViAe3Z'
consumer_secret='6QiAL3830kxExxY8GxzWojExnmEH8LU1UshP14FC95L3a9I2cK'

access_token='624121876-qfGeJslHyYUK9oYrfwqwNKKdQ4uTwCitCCdpjcji'
access_token_secret='GcNScEp1c6CFFCXO7Vl4RcIQ4hlQeNcYaINWQZ7eSsxlQ'

auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)

api=tweepy.API(auth)

with open('webapp/tweets.csv','w') as f:
    writer=csv.writer(f)
    writer.writerow(["account","number of followers","id","created_at","text","retweets"])
    f.close()


def get_all_tweets(screen_name):
    alltweets=[]
    new_tweets=api.user_timeline(screen_name=screen_name,count=200)
    user=api.get_user(screen_name, include_rts=False)
    alltweets.extend(new_tweets)
    oldest=alltweets[-1].id-1

    while len(new_tweets)>0:
        print ("getting tweets before %s"%(oldest))
        new_tweets=api.user_timeline(screen_name=screen_name,count=200,max_id=oldest)
        alltweets.extend(new_tweets)
        oldest=alltweets[-1].id-1

        print ("...%s tweets downloaded so far"%(len(alltweets)))

    outtweets = [[screen_name,user.followers_count,tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.retweet_count] for tweet in alltweets]
    with open('webapp/tweets.csv','a') as f:
        writer=csv.writer(f)
        writer.writerows(outtweets)
        f.close()
    pass

if __name__=='__main__':
    users = ['BarackObama', "HillaryClinton", "realDonaldTrump", "timkaine", "mike_pence", "marcorubio", "SenSanders", "GovGaryJohnson", "DrJillStein"]

    for user in users:
        get_all_tweets(user)