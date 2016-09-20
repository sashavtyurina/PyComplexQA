"""Static class containing a set of functions to work with text. Cleaning, removing bad tokens, etc."""
import re
# import polyglot
from polyglot.text import Text

stopwordsPath = '../data/stop_words.txt'


class TextWizard:
    """Static class containing a set of functions to work with text."""

    @staticmethod
    def extractNamedEntities(text):
        """Return a list of NEs that were found in the text."""
        text = Text(text, hint_language_code='en')
        return text.entities

    @staticmethod
    def preprocessText(text):
        """Perform text cleaning. Use this to do all the default text cleaning."""
        text = TextWizard.removeURLs(text)
        text = TextWizard.removePunctuation(text)
        text = TextWizard.shrinkRepeatedChars(text)
        tokens = text.split(' ')
        tokens = TextWizard.dropStopWords(tokens)
        tokens = TextWizard.removeShortTokens(tokens, 2)
        return ' '.join(tokens)


    @staticmethod
    def removePunctuation(str):
        """Remove punctuation signs from the string."""
        str = re.sub(r'\n', ' ', str)
        str = re.sub("[^A-Za-z\s\d\-']", ' ', str)
        str = re.sub("(?<![A-Za-z\d])'", ' ', str)
        str = re.sub("'(?![A-Za-z\d])", ' ', str)
        str = re.sub("(?<![A-Za-z\d])-", ' ', str)
        str = re.sub("-(?![A-Za-z\d])", ' ', str)
        return str


    @staticmethod
    def shrinkRepeatedChars(str):
        """Replace 3 or more repeated chars with a single one. For ex. pleaaase -> please."""
        cleanStr = re.sub(r'(.)\1{2,}', '\g<1>', str)
        cleanStr = re.sub(r'\s{2,}', ' ', cleanStr)
        return cleanStr


    @staticmethod
    def removeShortTokens(tokens, minLength):
        """Remove tokens shorter than minLength."""
        return [t for t in tokens if not len(t) < minLength]


    @staticmethod
    def dropStopWords(tokens):
        """Remove stop words from the list of tokens."""
        stopWords = [w.strip() for w in open(stopwordsPath)]
        return [t for t in tokens if t not in stopWords]


    @staticmethod
    def removeURLs(str):
        """Replace URLs with the domain name. For ex. www.youtube.com/bestvideo -> youtube."""
        # return re.sub(r'https?:\/\/([^\/]+)[^\s]*\s', '\g<1>', str)
        return re.sub(r'https?://(www\.)?([^\/]+)\.[^\s]*\s', '\g<2> ', str)
