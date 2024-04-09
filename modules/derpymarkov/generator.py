from . import config
from . import derpy_common
import markovify
import random
import re

test_kwargs = {'max_overlap_ratio': config.max_overlap_ratio,
               'max_overlap_total': config.max_overlap_total,
               'test_output': config.test_output}

if config.sentence_max_words > 0:
    test_kwargs['max_words'] = config.sentence_max_words

def compose_reply(message):
    key_phrase = None
    sentence = None

    if config.use_keywords:
        key_phrase = choose_key_phrase(message)

    sentence = get_sentence(message, key_phrase)
    reply = sentence

    if reply == message:
        reply = ""

    return reply

def choose_key_phrase(words):
    """
    Used to derive a keyword or phrase from the given text.
    
    words: Input text to be used for key words or phrases.
    """

    wordlist = derpy_common.model.word_split(words)
    index = random.randint(0, len(wordlist))
    key_phrase = wordlist[index - 1]
    return key_phrase

def get_sentence(words, key_phrase):
    """
    We generate sentences here and return them. Starts with the basic
    make_sentence and checks for any keywords (or returns the sentence if
    keywords are disabled). This gives the nicest results but tends to fail
    for words that are uncommon in a dictionary
    
    If the first method fails we attempt making a sentence with a starting
    key word which has a better rate of success but the possible responses
    are more limited and can feel repetitive if everything was done this way.
    
    words: Input text to be used for key words or phrases.
    key_phrase: A specific keyword or phrase can be sent for use instead.
    """
    wordlist = []

    if config.use_keywords:
        if config.try_all_words_for_key:
            wordlist = derpy_common.model.word_split(words)
            random.shuffle(wordlist)
        else:
            if key_phrase is not None:
                wordlist = [key_phrase]

    counter = 0
    sentence = None
    final_sentence = None
    attempt = None

    while counter < config.sentence_with_key_tries:
        counter += 1

        try:
            attempt = derpy_common.model.make_sentence(tries = 1, **test_kwargs)
        except KeyError as error:
            attempt = None

        if attempt is None:
            continue

        if config.use_keywords:
            for word in wordlist:
                if re.search(r'\b' + re.escape(word) + r'\b', attempt, re.IGNORECASE) is not None:
                    sentence = attempt
                    break
        else:
            sentence = attempt

        if sentence is not None:
            break

    if sentence is None:
        try:
            for word in wordlist:
                sentence = derpy_common.model.make_sentence_with_start(word, strict = False, **test_kwargs)

                if sentence is not None:
                    break
        except (KeyError, markovify.text.ParamError) as error:
            sentence = None

    if sentence is None and config.random_on_key_fail:
        sentence = derpy_common.model.make_sentence(tries = 3, **test_kwargs)

    if sentence is not None:
        final_sentence = post_process(sentence)

    return final_sentence

def post_process(sentence):
    if config.fix_punctuation:
        sentence = punctuation_cleanup(sentence)
        
    return sentence
    
def punctuation_cleanup(sentence):
    sentence_fragments = derpy_common.model.word_split(sentence)
    unmatched_open = -1
    unmatched_close = -1
    
    for index, fragment in enumerate(sentence_fragments, start = 1):
        if '(' in fragment:
            unmatched_open = index - 1
        
        if ')' in fragment:
            if unmatched_open != -1:
                unmatched_open = -1
            else:
                unmatched_close = index - 1

    if unmatched_open != -1:
        if len(sentence_fragments) > unmatched_open + 1:
            random_index = random.randrange(unmatched_open + 1, len(sentence_fragments))
        else:
            random_index = len(sentence_fragments);

        sentence_fragments[random_index] = sentence_fragments[random_index] + ')'

    if unmatched_close != -1:
        if unmatched_close < 2:
            sentence_fragments[unmatched_close] = '(' + sentence_fragments[unmatched_close]
        else:
            random_index = random.randrange(0, unmatched_close - 1)
            sentence_fragments[random_index] = sentence_fragments[random_index] + '('
        
    sentence = ' '.join(sentence_fragments)
    return sentence