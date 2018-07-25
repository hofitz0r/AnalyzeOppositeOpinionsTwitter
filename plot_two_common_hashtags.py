import datetime
import os

import matplotlib.pyplot as plt


class Data:
    def __init__(self, username, date, retweets, favorites, text, geo, mentions, hashtags, id, permalink):
        self.username = username
        self.date = date
        self.retweets = retweets
        self.favorites = favorites
        self.text = text
        self.geo = geo
        self.mentions = mentions
        self.hashtags = hashtags
        self.id = id
        self.permalink = permalink


def calc_ht(filename, l, hashtags):
    with open(filename, "rb") as f:
        for i in f.readlines():
            csv_data = i.split(';')
            try:
                d = Data(*csv_data)
            except:
                continue

            if d.id in l or d.id == "id":
                continue

            l[d.id] = d

            for h in d.hashtags.split():
                hash = h.lower()
                if hash not in hashtags:
                    hashtags[hash] = {}

                date = d.date.split()[0]
                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                if date not in hashtags[hash]:
                    hashtags[hash][date] = 0

                hashtags[hash][date] += 1


def two_common_hashtags(data_dir, results_dir):
    """
    plot two most common hashtags in the data directory, and export hashtags counts into file.
    :param data_dir: the tweets dir.
    :param results_dir: dir to put results into.
    """
    hashtags = {}
    l = {}
    for name in os.listdir(data_dir):
        filename = os.path.join(data_dir, name)
        calc_ht(filename, l, hashtags)

    # find all dates
    dates = set()
    for key in hashtags:
        values = hashtags[key].keys()
        for v in values:
            dates.add(v)

    # add all dates to all hashtags
    for key in hashtags:
        for date in dates:
            if date not in hashtags[key]:
                hashtags[key][date] = 0

    # relate to empty hashtags - bad results
    if "#" in hashtags:
        del hashtags["#"]

    lll = hashtags.items()

    lll = map(lambda x: (x[0], sum(x[1].values()), x[1]), lll)

    lll.sort(key=lambda x: x[1])

    lll = map(lambda x: (x[0], x[1], sorted(x[2].items(), key=lambda y: y[0])), lll)

    x2 = x1 = sorted(list(dates))

    y1 = map(lambda x: x[1], lll[-1][2])
    y2 = map(lambda x: x[1], lll[-2][2])

    plt.plot(x1, y1, 'bo-', label=lll[-1][0])
    plt.plot(x2, y2, 'go-', label=lll[-2][0])
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()
    plt.savefig(os.path.join(results_dir, "two_common.png"), bbox_inches='tight', dpi=600)
    with(open(os.path.join(results_dir, "two_common_summary.txt"), "wb")) as f:
        for x in lll:
            f.write(str(x))

    for x in lll:
        print x

    print "done"


def main():
    # example use:
    data_dir = r"C:\ACA\searches"
    results_dir = r"C:\ACA\results"
    two_common_hashtags(data_dir, results_dir)
