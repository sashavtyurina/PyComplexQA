import json
import re
import sqlite3

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

# performs s stemming of the list of tokens
def s_stemmer(tokens):
    def s_stem(word):
        if re.match('.*[^ea]ies$', word):
            return re.sub('ies$', 'y', word)
        if re.match('.*[^oae]es$', word):
            return re.sub('es$', 'e', word)
        if re.match('.*[^us]s$', word):
            return re.sub('s$', '', word)
        return word
    return [s_stem(t) for t in tokens]

# performs text cleaning. Use this to do all the text cleaning
def preprocessText(text):
    text = removeURLs(text)
    text = removePunctuation(text)
    text = shrinkRepeatedChars(text)
    tokens = text.split(' ')
    tokens = dropStopWords(tokens)
    tokens = s_stemmer(tokens)
    tokens = removeShortTokens(tokens, 3)
    return ' '.join(tokens)

# looks through the questions and answers and pick out distinct words and writes them in a file
def exportDistinctWords():
    distinctWords = set()
    for line in open('questions.txt'):
        jquestion = json.loads(line.strip())
        question = jquestion['qtitle'].lower() + ' ' + jquestion['qbody'].lower()
        qtokens = preprocessText(question).split(' ')
        atokens = [preprocessText(a['answer']).lower().split(' ') for a in jquestion['answers']]
        atokens = list(itertools.chain(*atokens))
        distinctWords.update(qtokens)
        distinctWords.update(atokens)

        print(distinctWords)
        print('\n***\n')

    with open('distinctWordsQA.txt', 'w') as f:
        for w in distinctWords:
            f.write('%s\n' %w)

# exports all snippets to a text file. each row as a separate json
def exportSnippetsFromDB():
    connection = sqlite3.connect('KeywordRankingDB.db')
    connection.text_factory = lambda x: str(x, 'latin1') # taking care of the encoding
    print('Connected to DB')
    sql = 'select questID, queryText, docURL, snippet from AllSnippets;'
    cursor = connection.execute(sql)
    with open('AllSnippets.txt', 'w') as fOut:
            for row in cursor:
                try:
                    questID = row[0]
                    queryText = row[1]
                    docURL = row[2]
                    snippet = row[3]
                    jsonRow = json.dumps({'questID':questID, 'queryText': queryText, 'docURL': docURL, 'snippet': snippet})
                    fOut.write('%s\n' % jsonRow)
                except sqlite3.OperationalError:
                    print(row)
                    continue

# imports questions from text file to a db
def importQuestionsFromText():
    connection = sqlite3.connect('Snippets.db')
    cursor = connection.cursor()
    print('Connected to DB')
    for line in open('questions.txt'):
        jQuestion = json.loads(line.strip())
        qtitle = jQuestion['qtitle']
        qbody = jQuestion['qbody']
        gtquery = jQuestion['gtquery']
        yahooqid = jQuestion['yahooqid']
        sql = 'insert into questions (qtitle, qbody, gtquery, yahooqid) values (?, ?, ?, ?);'
        cursor.execute(sql, (qtitle, qbody, gtquery, yahooqid))
        qid = cursor.lastrowid
        answers = jQuestion['answers']
        for a in answers:
            sql = 'insert into answers (qid, answertext) values (?, ?)'
            cursor.execute(sql, (qid, a['answer']))
    connection.commit()
    connection.close()

# import snippets from text file to a db
def importSnippetsFromText():
    connection = sqlite3.connect('Snippets.db')
    cursor = connection.cursor()
    print('Connected to DB')
    for line in open('AllSnippets.txt'):
        jSnippet = json.loads(line.strip())
        query = jSnippet['queryText']
        docURL = jSnippet['docURL']
        snippet = jSnippet['snippet']
        sql = 'insert into snippets (querytext, docurl, snippet) values (?, ?, ?);'
        cursor.execute(sql, (query, docURL, snippet))
    connection.commit()
    connection.close()



