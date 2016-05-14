import re

# removes punctuations from the string
def removePunctuation(str):
    str = re.sub(r'\n', ' ', str)
    return re.sub('[^A-Za-z\s\d]', ' ', str)

# replaces 3 or more repeated chars with a single one
def shrinkRepeatedChars(str):
    return re.sub(r'(.)\1{2,}', '\g<1>', str)

# removes tokens shorter than minLength
def removeShortTokens(tokens, minLength):
    return [t for t in tokens if not len(t) < minLength]

# removes stop words from the list of tokens
def dropStopWords(tokens):
    stopWords = [w.strip() for w in open('stop_words.txt')]
    return [t for t in tokens if t not in stopWords]

# replaces URLs with the domain name
def removeURLs(str):
    # return re.sub(r'https?:\/\/([^\/]+)[^\s]*\s', '\g<1>', str)
    return re.sub(r'https?://([^\/]+)\.[^\s]*\s', '\g<1> ', str)

def preprocessQuestion(qtitle, qbody):
    question = qtitle.lower() + ' ' + qbody.lower()
    question = removeURLs(question)
    question = removePunctuation(question)
    question = shrinkRepeatedChars(question)
    tokens = dropStopWords(question.split(' '))
    tokens = removeShortTokens(tokens, 3)
    return ' '.join(tokens)


