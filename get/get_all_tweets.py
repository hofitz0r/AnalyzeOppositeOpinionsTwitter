import datetime
from datetime import timedelta

import got
import codecs


def save_tweets(output_file_name, tweets):
    output_file = codecs.open(output_file_name, "w+", "utf-8")
    output_file.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink')
    for t in tweets:
        output_file.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s' % (
            t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions,
            t.hashtags,
            t.id, t.permalink)))
    output_file.flush()
    output_file.close()


def get_file_name(hashtag_query, dir_name, since, until, max_tweets, location=""):
    if location != "":
        return dir_name + "/{0}_to_{1}_{2}_{3}_max{4}_output.csv".format(since, until,
                                                                         hashtag_query, location, max_tweets)

    return dir_name + "/{0}_to_{1}_{2}_max{3}_output.csv".format(since, until,
                                                                 hashtag_query, max_tweets)


def get_tweet_criteria(hashtag_query, since, until, max_tweets, location):
    tweet_criteria = got.manager.TweetCriteria().setQuerySearch(hashtag_query). \
        setSince(since).setUntil(until).setMaxTweets(max_tweets)
    if location != "":
        tweet_criteria.setNear(location)

    return tweet_criteria


def get_all_tweets_to_direction(dir_name, since, until, max_tweets, threshold, hashtag_list, direction, location=""):
    counter = 1
    while counter > 0:
        counter = 0
        for hashtag_query in hashtag_list:
            file_name = get_file_name(hashtag_query, dir_name, since, until, max_tweets, location)

            tweet_criteria = get_tweet_criteria(hashtag_query, since, until, max_tweets, location)

            tweets = got.manager.TweetManager.getTweets(tweet_criteria)

            print "{0} got {1} tweets".format(hashtag_query, len(tweets))

            save_tweets(file_name, tweets)

            print("tweets saved to file name {0}".format(file_name))

            if len(tweets) > threshold:
                counter += 1

        since, until = get_new_dates(since, until, direction)


def get_new_dates(since, until, direction):
    if direction == "forward":
        since = until
        until = get_next_day_as_string(until)
    elif direction == "backward":
        until = since
        since = get_prev_day_as_string(since)
    return since, until


def get_next_day_as_string(date):
    new_date = datetime.datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
    return new_date.strftime("%Y-%m-%d")


def get_prev_day_as_string(date):
    new_date = datetime.datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)
    return new_date.strftime("%Y-%m-%d")


def get_all_tweets(dir_name, since, until, max_tweets, threshold, hashtag_list, location=""):
    """
    Search all tweets from hashtag_list from since to until(not included), with max_tweets results per hashtag.
    Stop the search when tweets count from each hashtag is not large than threshold, and save the results to dir_name.
    The location parameter doesn't work well, not recommended to use it.
    The function works best with following dates.
    :param dir_name: the dir to put results to.
    :param since: date string, to search from, example: "2017-01-23".
    :param until: date string, to search until, example: "2017-01-24". It is recommended to put following dates.
    :param max_tweets: max tweets to get from each hashtag.
    :param threshold: minimum tweets to search the previous and next days.
    :param hashtag_list: the hashtag list to search.
    :param location: The location to search near. not recommended.
    """
    original_since = since
    original_until = until
    print("getting all tweets forward!")
    get_all_tweets_to_direction(dir_name, since, until, max_tweets, threshold, hashtag_list, "forward",
                                location)

    print("-----------------------------------------------------------------------------")
    print("getting all tweets backward!")
    get_all_tweets_to_direction(dir_name, get_prev_day_as_string(original_until),
                                original_since, max_tweets, threshold, hashtag_list, "backward", location)


def main():
    # use examples.
    THRESHOLD = 20

    DIR_NAME = r"C:\ACA\searches"

    SINCE = "2018-04-13"
    UNTIL = "2018-04-14"

    MAX_TWEETS = 6000

    hashtag_list = ["#fullrepeal",
                    "#patientfreedomandchoiceplan",
                    "#destroyinghealthcare",
                    "#healthcarevoter",
                    "#healthforall",
                    "#medicareforall",
                    "#staycovered",
                    "#protectourcare",
                    "#repealandreplace",
                    "#saveaca"]

    get_all_tweets(DIR_NAME, SINCE, UNTIL, MAX_TWEETS, THRESHOLD, hashtag_list)


if __name__ == '__main__':
    main()
