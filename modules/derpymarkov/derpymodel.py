import markovify
import re

DEFAULT_MAX_OVERLAP_RATIO = 0.7
DEFAULT_MAX_OVERLAP_TOTAL = 15
DEFAULT_TRIES = 10

class DerpyText(markovify.Text):

    def sentence_split(self, text):
        return re.split(r"\s*\n\s*", text)

    def test_sentence_input(self, sentence):
        """
        A basic sentence filter. This one rejects sentences that contain
        the type of punctuation that would look strange on its own
        in a randomly-generated sentence. 
        """
        
        #reject_pat = re.compile(r"(^')|('$)|\s'|'\s|[\"(\(\)\[\])]")
        reject_pat = re.compile(r"(?!)")
        # Decode unicode, mainly to normalize fancy quotation marks
        if sentence.__class__.__name__ == "str": # pragma: no cover
            decoded = sentence
        else: # pragma: no cover
            decoded = unidecode(sentence)
        # Sentence shouldn't contain problematic characters
        if re.search(reject_pat, decoded): return False
        return True
    