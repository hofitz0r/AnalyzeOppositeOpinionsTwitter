import csv
import datetime
import os

import matplotlib.pyplot as plt
import numpy


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


def calc_ht(for_hashtags, against_hashtags, filename, l, hashtags):
    with open(filename, "rb") as f:
        for i in f.readlines():
            csv_data = i.split(';')
            try:
                d = Data(*csv_data)
            except:
                continue

            if d.id in l or d.id == "id":
                continue

            if is_bad_tweet(for_hashtags, against_hashtags, d.hashtags):
                continue

            l[d.id] = d

            for h in d.hashtags.split():
                hash = h.lower()
                if hash not in hashtags:
                    hashtags[hash] = {}

                date = d.date.split()[0]
                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                if date not in hashtags[hash]:
                    hashtags[hash][date] = []
                hashtags[hash][date].append(d.id)


class Opinion:
    def __init__(self, graph_label, hashtag_list):
        self.graph_label = graph_label
        self.hashtag_list = map(lambda x: x.lower(), hashtag_list)


def is_intersect(lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return len(lst3) > 0


def is_bad_tweet(for_hashtags, against_hashtags, tweets_hashtags_string):
    split = tweets_hashtags_string.lower().split()
    return is_intersect(for_hashtags, split) and is_intersect(against_hashtags, split)


def summary_opposite_opinions(data_dir, results_dir, opinion_for, opinion_against):
    """
    Get results of tweets in data_dir summarised as for and against according to the
    opinion for and opinion against.
    Put plot , hashtags by count, and summarised opinions data into results_dir.
    :param data_dir: tweets dir
    :param results_dir: results dir
    :param opinion_for: type Opinion, containing hashtag list of the opinion and the graph label.
    :param opinion_against: type Opinion, containing hashtag list of the opinion and the graph label.
    """
    hashtags = {}
    l = {}

    for name in os.listdir(data_dir):
        if name != "desktop.ini":
            filename = os.path.join(data_dir, name)
            calc_ht(opinion_for.hashtag_list, opinion_against.hashtag_list, filename, l, hashtags)

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
                hashtags[key][date] = []

    # relate to empty hashtags - bad results
    if "#" in hashtags:
        del hashtags["#"]

    lll = hashtags.items()
    lll = map(lambda x: (x[0], x[1].copy()), lll)
    for x, y in lll:
        for key in y:
            y[key] = len(y[key])

    lll = map(lambda x: (x[0], sum(x[1].values()), x[1]), lll)

    lll.sort(key=lambda x: x[1])

    lll = map(lambda x: (x[0], x[1], sorted(x[2].items(), key=lambda y: y[0])), lll)

    x2 = x1 = sorted(list(dates))

    y1 = [set() for i in range(len(x1))]
    for h in opinion_for.hashtag_list:
        items = sorted(hashtags[h].items(), key=lambda y: y[0])
        for i, t in enumerate(items):
            y1[i].update(t[1])

    y2 = [set() for i in range(len(x1))]
    for h in opinion_against.hashtag_list:
        items = sorted(hashtags[h].items(), key=lambda y: y[0])
        for i, t in enumerate(items):
            y2[i].update(t[1])

    y1 = [len(x) for x in y1]
    y2 = [len(x) for x in y2]

    y_tot = list(numpy.add(y1, y2))
    y1_perc = list(numpy.divide(numpy.multiply(y1, 100), y_tot, dtype=float))
    y2_perc = list(numpy.divide(numpy.multiply(y2, 100), y_tot, dtype=float))

    plt.plot(x1, y1, 'bo-', label=opinion_for.graph_label)
    plt.plot(x2, y2, 'go-', label=opinion_against.graph_label)

    plt.legend()
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(results_dir, "summary_opposite_plot.png"), bbox_inches='tight', dpi=600)
    plt.show()

    with(open(os.path.join(results_dir, "summary_opposite.txt"), "w")) as f:
        for x in lll:
            f.write(str(x))

    with(open(os.path.join(results_dir, "summary_opposite_percentage.csv"), "wb")) as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        title = ["date", opinion_for.graph_label, opinion_for.graph_label + "_perc", opinion_against.graph_label,
         opinion_against.graph_label + "_perc" , "total"]

        wr.writerow(title)
        for line in numpy.transpose([x1, y1, y1_perc, y2, y2_perc, y_tot]):
            wr.writerow(line)


    for x in lll:
        print x

    print "done"


def main():
    dir_name = r"C:\ACA\searches"
    results_dir = r"C:\ACA\results"
    pro = [
        "#protectourcare",
        "#saveaca",
        "#medicareforall",
        "#votenoahca",
        "#voteno",
        "#noahca",
        "#healthforall",
        "#notrumpcare",
        "#obamacarehelpedme",
        "#savetheaca",
        "#votenoacha",
        "#healthcareforall",
        "#medicare4all",
        "#trumpcarekills",
        "#killthebill",
    ]

    against = [
        "#fullrepeal",
        "#repealandreplace",
        "#singlepayer",
        "#singlepayernow",
        "#repealobamacare"
    ]
    opinion_for = Opinion("ProObamaCare", pro)
    opinion_against = Opinion("ProTrumpCare", against)

    summary_opposite_opinions(dir_name, results_dir, opinion_for, opinion_against)


if __name__ == "__main__":
    main()
