# Fetches the top posts from a sister subreddit and updates the main subreddit's sidebar with a list of them
# The main subreddit's sidebar must include strings to denote the beginning and ending location of the list, the bot will not update the sidebar if these strings are not present
# With the default delimiters the sidebar should include a chunk of text like:
# 
# **Top posts in our sister subreddit:**
# [](/hot-sister-start)
# [](/hot-sister-end)
# Other text that will be below the list

import re
import praw_script_oauth
import html.parser
import time

# defines the main and sister subreddits, and how many posts to list in the sidebar
subredditlist = {'imagesofafghanistan', 'imagesofaustralia', 'imagesofbelgium', 'imagesofbelize', 'imagesofbrazil', 'imagesofcanada', 'imagesoftoronto', 'imagesofchile', 'imagesofchina', 'imagesofhongkong', 'imagesofengland', 'imagesoffrance', 'imagesofguatemala', 'imagesoficeland', 'imagesofindia', 'imagesofiran', 'imagesofisleofman', 'imagesofjapan', 'imagesoflibya', 'imagesofmaldives', 'imagesofmexico', 'imagesofnetherlands', 'imagesofnewzealand', 'imagesofnorway', 'imagesofperu', 'imagesofrussia', 'imagesofscotland', 'imagesofsyria', 'imagesofusa', 'imagesofalabama', 'imagesofalaska', 'imagesofarizona', 'imagesofarkansas', 'imagesofcalifornia', 'imagesofcolorado', 'imagesofconnecticut', 'imagesofdelaware', 'imagesofflorida', 'imagesofgeorgia', 'imagesofhawaii', 'imagesofidaho', 'imagesofillinois', 'imagesofindiana', 'imagesofiowa', 'imagesofkansas', 'imagesofkentucky', 'imagesoflouisiana', 'imagesofmaine', 'imagesofmaryland', 'imagesofmassachusetts', 'imagesofmichigan', 'imagesofminnesota', 'imagesofmississippi', 'imagesofmissouri', 'imagesofmontana', 'imagesofnebraska', 'imagesofnevada', 'imagesofnewhampshire', 'imagesofnewjersey', 'imagesofnewmexico', 'imagesofnewyork', 'imagesofnorthcarolina', 'imagesofnorthdakota', 'imagesofohio', 'imagesofoklahoma', 'imagesoforegon', 'imagesofpennsylvania', 'imagesofrhodeisland', 'imagesofsouthcarolina', 'imagesofsouthdakota', 'imagesoftennessee', 'imagesoftexas', 'imagesofutah', 'imagesofvermont', 'imagesofvirginia', 'imagesofwashington', 'imagesofwashingtondc', 'imagesofwestvirginia', 'imagesofwisconsin', 'imagesofwyoming', 'imagesofwales', 'imagesofyemen'}
SISTER_MULTI_HOST = 'amici_ursi'
SISTER_MULTI_NAME = 'imagesofplaces'
POSTS_TO_LIST = 5

# don't change unless you want different delimiter strings for some reason
START_DELIM = '[](/hot-sister-start)'
END_DELIM = '[](/hot-sister-end)'

# log into reddit
print("logging into hot_sister")
r = praw_script_oauth.connect("client_id", "client_secret", "client_username", "client_password", oauth_scopes="client_scopes", useragent="hot_sister fork maintained by /u/amici_ursi")

# get the subreddits
while True:
    for MAIN_SUBREDDIT in subredditlist:
        print("running on {}".format(MAIN_SUBREDDIT))
        main_subreddit = r.get_subreddit(MAIN_SUBREDDIT)
        sister_subreddit = r.get_multireddit(SISTER_MULTI_HOST, SISTER_MULTI_NAME)

        # fetch the top posts from the sister subreddit, and build the text to update the sidebar with
        list_text = str()
        for (i, post) in enumerate(sister_subreddit.get_hot(limit=POSTS_TO_LIST)):
            list_text += '* [%s](%s)\n' % (post.title, post.permalink)

        # update the sidebar

        current_sidebar = main_subreddit.get_settings()['description']
        current_sidebar = html.parser.HTMLParser().unescape(current_sidebar)
        replace_pattern = re.compile('%s.*?%s' % (re.escape(START_DELIM), re.escape(END_DELIM)), re.IGNORECASE|re.DOTALL|re.UNICODE)
        new_sidebar = re.sub(replace_pattern,
                            '%s\\n\\n%s\\n%s' % (START_DELIM, list_text, END_DELIM),
                            current_sidebar)
        main_subreddit.update_settings(description=new_sidebar)

    #sleep for 30 minutes before doing it again
    for minute in range(30, 0, -1):
        print("sleeping for {} minutes".format(minute))
        time.sleep(60)
