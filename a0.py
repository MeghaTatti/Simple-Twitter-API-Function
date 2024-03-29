# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 12:42:04 2019

@author: megha
"""

# coding: utf-8


###CS579: Assignment 0

from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
import itertools 
from TwitterAPI import TwitterAPI

consumer_key = 'fXPWM69NxCLpNNkFnpCEMYVeO'
consumer_secret = 'v2758NlUg7HvmXOxO4QQrOhpEwbVU8vFmrKuC8kM2RiEAoOsc1'
access_token = '1058787616823349249-FFsXg2FnTJIiYYfWPgrYEZx9FmcCLA'
access_token_secret = 'HeBHf8OFMtSKJNaBD5uAHj8b5kPXuRBZPyub5Svkum3pV'

def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def read_screen_names(filename):
    """
    Read a text file containing Twitter screen_names, one per line.

    Params:
        filename....Name of the file to read.
    Returns:
        A list of strings, one per screen_name, in the order they are listed
        in the file."""

    with open('candidates.txt', 'r') as Twitter_file:
        Twitter_file = Twitter_file.read().splitlines()
        return Twitter_file
    
    pass


def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request        
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)


def get_users(twitter, screen_names):
    """Retrieve the Twitter user objects for each screen_name.
    Params:
        twitter........The TwitterAPI object.
        screen_names...A list of strings, one per screen_name
    Returns:
        A list of dicts, one per user, containing all the user information
        (e.g., screen_name, id, location, etc)

       """
    uResponse = robust_request(twitter,"users/lookup",{'screen_name':screen_names})
    u = [user for user in uResponse]
    return u
    pass


def get_friends(twitter, screen_name):
    """ Return a list of Twitter IDs for users that this person follows, up to 5000.
        Args:
        twitter.......The TwitterAPI object
        screen_name... a string of a Twitter screen name
    Returns:
        A list of ints, one per friend ID, sorted in ascending order.
    """
    fResponse = robust_request(twitter,"friends/ids",{'screen_name':screen_name,'count':5000})
    return [i for i in fResponse]
    pass


def add_all_friends(twitter, users):
    """ Get the list of accounts each user follows.
    Args:
        twitter...The TwitterAPI object.
        users.....The list of user dicts.
    Returns:
        Nothing
"""
    for i in range(len(users)):
        friends = get_friends(twitter, users[i]['screen_name'])
        users[i]['friends']=friends
        
    pass


def print_num_friends(users):
    """Print the number of friends per candidate, sorted by candidate name.
    See Log.txt for an example.
    Args:
        users....The list of user dicts.
    Returns:
        Nothing
       """
    sort_users=sorted(users, key=lambda x: x['screen_name'])
    for i in range(len(sort_users)):
        print(sort_users[i]['screen_name'] , len(sort_users[i]['friends']))
    pass


def count_friends(users):
    """ Count how often each friend is followed.
    Args:
        users: a list of user dicts
    Returns:
        a Counter object mapping each friend to the number of candidates who follow them.
        Counter documentation: https://docs.python.org/dev/library/collections.html#collections.Counter

    In this example, friend '2' is followed by three different users.
    >>> c = count_friends([{'friends': [1,2]}, {'friends': [2,3]}, {'friends': [2,3]}])
    >>> c.most_common()
    [(2, 3), (3, 2), (1, 1)]
    """
    
    cfriends = Counter()
    for e in users:
        cfriends.update(e['friends'])
    return cfriends
    
    pass


def friend_overlap(users):
    """
    Compute the number of shared accounts followed by each pair of users.

    Args:
        users...The list of user dicts.

    Return: A list of tuples containing (user1, user2, N), where N is the
        number of accounts that both user1 and user2 follow.  This list should
        be sorted in descending order of N. Ties are broken first by user1's
        screen_name, then by user2's screen_name (sorted in ascending
        alphabetical order). See Python's builtin sorted method.

    In this example, users 'a' and 'c' follow the same 3 accounts:
    >>> friend_overlap([
    ...     {'screen_name': 'a', 'friends': ['1', '2', '3']},
    ...     {'screen_name': 'b', 'friends': ['2', '3', '4']},
    ...     {'screen_name': 'c', 'friends': ['1', '2', '3']},
    ...     ])
    [('a', 'c', 3), ('a', 'b', 2), ('b', 'c', 2)]
    """
    
    friendsOverlap = []
    for userone, usertwo in itertools.combinations(users, 2):
        cfriends=Counter()
        cfriends.update(userone['friends'])
        cfriends.update(usertwo['friends'])
        common_friends = [idx for idx in userone['friends'] if cfriends[idx]==2]
        friendsOverlap.append((userone['screen_name'],usertwo['screen_name'],len(common_friends)))

    friendsOverlap=sorted(friendsOverlap, key=lambda x:(x[2]),reverse=True)
    return friendsOverlap
    
    pass


def followed_by_hillary_and_donald(users, twitter):
    """
    Find and return the screen_names of the Twitter users followed by both Hillary
    Clinton and Donald Trump. You will need to use the TwitterAPI to convert
    the Twitter ID to a screen_name. See:
    https://dev.twitter.com/rest/reference/get/users/lookup

    Params:
        users.....The list of user dicts
        twitter...The Twitter API object
    Returns:
        A list of strings containing the Twitter screen_names of the users
        that are followed by both Hillary Clinton and Donald Trump.
    """
    for hillary, donald in itertools.combinations(users, 2):
        if(hillary['screen_name']=="HillaryClinton" and donald['screen_name']=="realDonaldTrump"):
            cFriends=Counter()
            cFriends.update(hillary['friends'])
            cFriends.update(donald['friends'])
            commonFriend=[ind for ind in hillary['friends'] if cFriends[ind]==2]
            break
    fname = robust_request(twitter,"users/lookup",{'user_id':commonFriend},5)
    sList = [itr for itr in fname]
    return sList[0]['screen_name']   
    pass


def create_graph(users, friend_counts):
    """ Create a networkx undirected Graph, adding each candidate and friend
        as a node.  Note: while all candidates should be added to the graph,
        only add friends to the graph if they are followed by more than one
        candidate. (This is to reduce clutter.)

        Each candidate in the Graph will be represented by their screen_name,
        while each friend will be represented by their user id.

    Args:
      users...........The list of user dicts.
      friend_counts...The Counter dict mapping each friend to the number of candidates that follow them.
    Returns:
      A networkx Graph
    """
    graph = nx.Graph()
    for u in users:
        for friend in range(len(u['friends'])):
            if friend_counts[u['friends'][friend]] > 1:
                graph.add_edge(u['friends'][friend],u['screen_name'])
    return graph
    pass


def draw_network(graph, users, filename):
    """
    Draw the network to a file. Only label the candidate nodes; the friend
    nodes should have no labels (to reduce clutter).

    Methods you'll need include networkx.draw_networkx, plt.figure, and plt.savefig.

    Your figure does not have to look exactly the same as mine, but try to
    make it look presentable.
    """
    
    labels={}
    for u in users:
        labels[u['screen_name']]=u['screen_name']
    plt.figure(figsize=(10,10))
    nx.draw_networkx(graph,labels=labels,with_labels=True,alpha=0.5, width=0.2)
    plt.axis('off')
    plt.savefig(filename,format="PNG",frameon=None,dpi=300)
    plt.show()
    pass


def main():
    """ Main method. You should not modify this. """
    twitter = get_twitter()
    screen_names = read_screen_names('candidates.txt')
    print('Established Twitter connection.')
    print('Read screen names: %s' % screen_names)
    users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %
          (len(users), str([u['screen_name'] for u in users])))
    add_all_friends(twitter, users)
    print('Friends per candidate:')
    print_num_friends(users)
    friend_counts = count_friends(users)
    print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
    print('Friend Overlap:\n%s' % str(friend_overlap(users)))
    print('User followed by Hillary and Donald: %s' % str(followed_by_hillary_and_donald(users, twitter)))

    graph = create_graph(users, friend_counts)
    print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
    draw_network(graph, users, 'network.png')
    print('network drawn to network.png')


if __name__ == '__main__':
    main()

# That's it for now! This should give you an introduction to some of the data we'll study in this course.
