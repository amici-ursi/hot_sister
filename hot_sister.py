# Fetches the top posts from a sister subreddit and updates the main subreddit's sidebar with a list of them
# The main subreddit's sidebar must include strings to denote the beginning and ending location of the list, the bot will not update the sidebar if these strings are not present
# With the default delimiters the sidebar should include a chunk of text like:
# 
# **Top posts in our sister subreddit:**
# [](/hot-sister-start)
# [](/hot-sister-end)
# Other text that will be below the list

import re
import html.parser
import time
import praw
import os

# defines the main and sister subreddits, and how many posts to list in the sidebar
PLACESLIST = {'imagesofafghanistan', 'imagesofaustralia', 'imagesofbelgium', 'imagesofbelize', 'imagesofbrazil', 'imagesofcanada', 'imagesoftoronto', 'imagesofchile', 'imagesofchina', 'imagesofhongkong', 'imagesofengland', 'imagesoffrance', 'imagesofguatemala', 'imagesoficeland', 'imagesofindia', 'imagesofiran', 'imagesofisleofman', 'imagesofjapan', 'imagesoflibya', 'imagesofmaldives', 'imagesofmexico', 'imagesofnetherlands', 'imagesofnewzealand', 'imagesofnorway', 'imagesofperu', 'imagesofrussia', 'imagesofscotland', 'imagesofsyria', 'imagesofusa', 'imagesofalabama', 'imagesofalaska', 'imagesofarizona', 'imagesofarkansas', 'imagesofcalifornia', 'imagesofcolorado', 'imagesofconnecticut', 'imagesofdelaware', 'imagesofflorida', 'imagesofgeorgia', 'imagesofhawaii', 'imagesofidaho', 'imagesofillinois', 'imagesofindiana', 'imagesofiowa', 'imagesofkansas', 'imagesofkentucky', 'imagesoflouisiana', 'imagesofmaine', 'imagesofmaryland', 'imagesofmassachusetts', 'imagesofmichigan', 'imagesofminnesota', 'imagesofmississippi', 'imagesofmissouri', 'imagesofmontana', 'imagesofnebraska', 'imagesofnevada', 'imagesofnewhampshire', 'imagesofnewjersey', 'imagesofnewmexico', 'imagesofnewyork', 'imagesofnorthcarolina', 'imagesofnorthdakota', 'imagesofohio', 'imagesofoklahoma', 'imagesoforegon', 'imagesofpennsylvania', 'imagesofrhodeisland', 'imagesofsouthcarolina', 'imagesofsouthdakota', 'imagesoftennessee', 'imagesoftexas', 'imagesofutah', 'imagesofvermont', 'imagesofvirginia', 'imagesofwashington', 'imagesofwashingtondc', 'imagesofwestvirginia', 'imagesofwisconsin', 'imagesofwyoming', 'imagesofwales', 'imagesofyemen', 'imagesofnetwork', 'imagesofegypt', 'imagesofsingapore', 'imagesofbulgaria'}
PLACES_MULTI_HOST = 'amici_ursi'
PLACES_MULTI_NAME = 'imagesofplaces'
DECADESLIST = {'imagesofthe1800s', 'imagesofthe1900s', 'imagesofthe1910s', 'imagesofthe1920s', 'imagesofthe1930s', 'imagesofthe1940s', 'imagesofthe1950s', 'imagesofthe1960s', 'imagesofthe1970s', 'imagesofthe1980s', 'imagesofthe1990s', 'imagesofthe2000s', 'imagesofthe2010s'}
DECADES_MULTI_HOST = 'noeatnosleep'
DECADES_MULTI_NAME = 'imagesofthedecades'
POSTS_TO_LIST = 5

# login info for the script to log in as, this user must be a mod in the main subreddit

# don't change unless you want different delimiter strings for some reason
START_DELIM = '[](/hot-sister-start)'
END_DELIM = '[](/hot-sister-end)'

# log into reddit
print("logging into hot_sister")
client_username = os.environ.get("hot_sister_username")
print("client_username: {}".format(client_username))
client_password = os.environ.get("hot_sister_password")
print("client_password: {}".format(client_password))
r = praw.Reddit(user_agent="hot_sister fork by /u/amici_ursi")
r.login(client_username, client_password)

# get the subreddits
while True:
    #fetch the top posts from the sister MULTI, and build the text to update the sidebar with
    PLACES_MULTI = r.get_multireddit(PLACES_MULTI_HOST, PLACES_MULTI_NAME)
    PLACES_LIST_TEXT = str()
    for (i, post) in enumerate(PLACES_MULTI.get_hot(limit=POSTS_TO_LIST)):
        PLACES_LIST_TEXT += ' * [%s](%s)\n' % (post.title, post.permalink)
    DECADES_MULTI = r.get_multireddit(DECADES_MULTI_HOST, DECADES_MULTI_NAME)
    DECADES_LIST_TEXT = str()
    for (i, post) in enumerate(DECADES_MULTI.get_hot(limit=POSTS_TO_LIST)):
        DECADES_LIST_TEXT += ' * [%s](%s)\n' % (post.title, post.permalink)
    COMBINED_TEXT = "* Places:\n{}\n\n* Times:\n{}".format(PLACES_LIST_TEXT, DECADES_LIST_TEXT)
    for MAIN_SUBREDDIT in PLACESLIST:
        print("running on {}".format(MAIN_SUBREDDIT))
        main_subreddit = r.get_subreddit(MAIN_SUBREDDIT)
        
        # update the sidebar
        current_sidebar = main_subreddit.get_settings()['description']
        current_sidebar = html.parser.HTMLParser().unescape(current_sidebar)
        replace_pattern = re.compile('%s.*?%s' % (re.escape(START_DELIM), re.escape(END_DELIM)), re.IGNORECASE|re.DOTALL|re.UNICODE)
        new_sidebar = re.sub(replace_pattern,
                            '%s\\n\\n%s\\n%s' % (START_DELIM, COMBINED_TEXT, END_DELIM),
                            current_sidebar)
        main_subreddit.update_settings(description=new_sidebar)

    #DO THE DECADES
    for MAIN_SUBREDDIT in DECADESLIST:
        print("running on {}".format(MAIN_SUBREDDIT))
        main_subreddit = r.get_subreddit(MAIN_SUBREDDIT)

        # update the sidebar
        current_sidebar = main_subreddit.get_settings()['description']
        current_sidebar = html.parser.HTMLParser().unescape(current_sidebar)
        replace_pattern = re.compile('%s.*?%s' % (re.escape(START_DELIM), re.escape(END_DELIM)), re.IGNORECASE|re.DOTALL|re.UNICODE)
        new_sidebar = re.sub(replace_pattern,
                            '%s\\n\\n%s\\n%s' % (START_DELIM, COMBINED_TEXT, END_DELIM),
                            current_sidebar)
        main_subreddit.update_settings(description=new_sidebar)

    #sleep for 30 minutes before doing it again
    for minute in range(30, 0, -1):
        print("sleeping for {} minutes".format(minute))
        time.sleep(60)
