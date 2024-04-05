import re

model = None
unsaved = False
doing_chain = False

uri_regex = re.compile("[^\s]*:\/\/[^\s]*")
emoticon_regex = re.compile(":[DPO]|D:|[X|x]D|[Oo][_-][Oo]")
hashtag_user_regex = re.compile("^[@#][^\s]*")