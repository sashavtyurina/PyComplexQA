import json
import re
import sqlite3
from itertools import permutations
import itertools
from Keywords import *
from SQLWizard import SQLWizard
from KLDWizard import KLDWizard


# removes punctuations from the string
def removePunctuation(str):
    str = re.sub(r'\n', ' ', str)
    str = re.sub("[^A-Za-z\s\d']", ' ', str)
    str = re.sub("(?<![A-Za-z\d])'", ' ', str)
    str = re.sub("'(?![A-Za-z\d])", ' ', str)
    return str


# replaces 3 or more repeated chars with a single one
def shrinkRepeatedChars(str):
    cleanStr = re.sub(r'(.)\1{2,}', '\g<1>', str)
    cleanStr = re.sub(r'\s{2,}', ' ', cleanStr)
    return cleanStr


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
            return re.sub("(?<!')s$", '', word)
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
    tokens = removeShortTokens(tokens, 2)
    return ' '.join(tokens)


# given a list of tokens, return all queries of length queryLength
# also requires question text to put the tokens in the queries the same order as they were in the question
def constructQueries(tokens, queryLength, rawQuestion):
    def addOne(queries, tokens):
        newQueries = {}
        for q in queries.items():
            for i in range(q[1] + 1, len(tokens)):
                # check if these tokens (or bigrams) overlap
                if len(set(q[0].split()).intersection(set(tokens[i].split()))) == 0:
                    qq = ' '.join([q[0], tokens[i]])
                    newQueries[qq] = max(q[1], i)
        return newQueries


    # order tokens the same way they appear in the question
    def sortTokens(tokensToSort, rawQuestion):
        # for every token find its first occurence in the initial string
        # then sort based on these indecies
        tokensInd = {}
        for t in tokensToSort:
            if t not in tokensInd.keys():
                ind = rawQuestion.find(t)
                if ind == -1:
                    ind = rawQuestion.find(t[:-1])
                tokensInd[t] = ind
        print(tokensInd)
        sortedInd = sorted(tokensInd.items(), key=operator.itemgetter(1))
        sortedTokens = [i[0] for i in sortedInd]

        return sortedTokens


    # find collocations and glue them together as a single token
    # TODO: add answers text here as well?
    def findCollocations(rawQuestion):
        # split the question into blocks by punctuation marks
        # blocks = [b.strip() for b in re.split('[^0-9A_Za-x\s]+', rawQuestion) if b.strip() != '']
        # Example:
        # blocks : ['why is my 5 month old pit bull puppy eating rocks',
        # 'my dog is very active and has a really good appetite',
        # 'she loves to play and is very well mannered',
        # 'lately she has been eating small pea gravel from my landscaping',
        # 'is she just being a puppy or is something wrong']
        blocks = [b.strip() for b in re.split('[.,\?\!\-\:\;\(\)\{\}\[\]]+', rawQuestion) if b.strip() != '']

        # for each block tokens. blocksTokens = List[List[Str]]
        # Example:
        # blocksTokens: [['month', 'old', 'pit', 'bull', 'puppy', 'eating', 'rock'],
        # ['dog', 'active', 'good', 'appetite'],
        # ['love', 'play', 'mannered'],
        # ['lately', 'eating', 'small', 'pea', 'gravel', 'landscaping'],
        # ['puppy', 'wrong']]
        blocksTokens = [preprocessText(b).split() for b in blocks]

        # compose bigrams. blocksBigrams = List[List[Str]]
        # Example:
        # blocksBigrams: [['month old',
        #  'old pit',
        #  'pit bull',
        #  'bull puppy',
        #  'puppy eating',
        #  'eating rock'],
        # ['dog active', 'active good', 'good appetite'],
        # ['love play', 'play mannered'],
        # ['lately eating',
        #  'eating small',
        #  'small pea',
        #  'pea gravel',
        #  'gravel landscaping'],
        # ['puppy wrong']]
        N = 2
        blocksBigrams = [[' '.join(tokens[i: i + N]) for i in range(0, len(tokens) - N + 1)] for tokens in blocksTokens]

        # flatten previous list of lists to a single list of strings
        # Example:
        # flatBigrams : ['month old',
        # 'old pit',
        # 'pit bull',
        # 'bull puppy',
        # 'puppy eating',
        # 'eating rock',
        # 'dog active',
        # 'active good',
        # 'good appetite',
        # 'love play',
        # 'play mannered',
        # 'lately eating',
        # 'eating small',
        # 'small pea',
        # 'pea gravel',
        # 'gravel landscaping',
        # 'puppy wrong']
        flatBigrams = list(itertools.chain.from_iterable(blocksBigrams))

        # find repetitive bigrams
        freqBigrams = {}
        for b in flatBigrams:
            if b in freqBigrams.keys():
                freqBigrams[b] += 1
            else:
                freqBigrams[b] = 1
        # print('Freq bigrams ' + str(freqBigrams))
        repBigrams = [b[0] for b in freqBigrams.items() if b[1] > 1]
        print('Found collocations: ' + str(repBigrams))
        return repBigrams


    queriesOfLengths = {}
    queries = {}

    # sort tokens in order of their occurence in the initial question
    # print('Found collocations: ' + str(findCollocations(rawQuestion)))
    tokens += findCollocations(rawQuestion)
    sortedTokens = sortTokens(tokens, rawQuestion)

    print('raw question :: ' + str(rawQuestion))
    print('sorted tokens :: ' + str(sortedTokens))

    # start by creating all single word queries
    for i in range(0, len(sortedTokens)):
        queries[sortedTokens[i]] = i
    queriesOfLengths[1] = queries.keys()

    # append one word to existing queries
    for i in range(1, queryLength):
        queries = addOne(queries, sortedTokens)
        queriesOfLengths[i + 1] = queries.keys()

    print('queries :: ' + str(queriesOfLengths[queryLength]))
    return queriesOfLengths[queryLength]


def averageSnippetIntersection(snippetTokensSets, topWordsSet, queryTokensSet):
    intersections = []
    # print('Top words :: ' + str(topWordsSet))
    # print('Query tokens :: ' + str(queryTokensSet))
    for singleSnippetTokens in snippetTokensSets:
        # print('Snippet tokens initial:: ' + str(singleSnippetTokens))
        # print('Top words :: ' + str(topWordsSet))
        # print('\n\n')

        singleSnippetTokens.difference_update(queryTokensSet)
        intersection = singleSnippetTokens.intersection(topWordsSet)
        intersectionLength = len(intersection)
        snippetLength = len(singleSnippetTokens)
        # print('Intersection :: ' + str(intersection))
        # print('Intersection length :: ' + str(intersectionLength))
        # print('Snippet length :: ' + str(snippetLength))

        intersections.append(intersectionLength / snippetLength)
        # print(intersections)
        # print('\n***\n')
        # input()
    result = sum(intersections) / len(intersections)
    # print(result)
    return result


def totalSnippetIntersection(snippetTokensSet, topWordsSet, queryTokensSet):
    allSnippetsTokensSet = set(itertools.chain(*snippetTokensSet))
    allSnippetsTokensSet.difference_update(queryTokensSet)
    intersection = allSnippetsTokensSet.intersection(topWordsSet)
    result = len(intersection) / len(allSnippetsTokensSet)
    # print(result)
    return result


def scoreQuery(query, snippets, answersTopWords, questionTopWords, weights):
    cleanSnippetTokens = [set(preprocessText(s.snippet).split()) for s in snippets]
    questionTopWords = set(questionTopWords)
    answersTopWords = set(answersTopWords)

    aveIntersectionWQuestion = averageSnippetIntersection(cleanSnippetTokens, questionTopWords)
    aveIntersectionWAnswers = averageSnippetIntersection(cleanSnippetTokens, answersTopWords)

    totalIntersectionWQuestion = totalSnippetIntersection(cleanSnippetTokens, questionTopWords)
    totalIntersectionWAnswers = totalSnippetIntersection(cleanSnippetTokens, answersTopWords)

    score = weights[0] * aveIntersectionWQuestion + weights[1] * aveIntersectionWAnswers + weights[2] * totalIntersectionWQuestion + weights[3] * totalIntersectionWAnswers

    return score


# given a list of snippets remove the ones that were retrieved from the same page as the question (compare yahooqid)
# and also remove the ones that look too similar to the question (more than 50% of snippet terms are in the question)
def filterOutDuplicateSnippets(snippets, question):
    cleanSnippets = []
    for s in snippets:
        if question.yahooqid in s.docURL:
            continue
        snippetTokens = set(preprocessText(s.snippet).split(' '))
        questionTokens = set(preprocessText(' '.join([question.qtitle, question.qbody])).split(' '))
        intersectionFraction = len(snippetTokens.intersection(questionTokens)) / len(snippetTokens)
        if intersectionFraction > 0.5:
            continue
        cleanSnippets.append(s)
    return cleanSnippets


# MISC UTILITIES
def loadLinesFromTextToList(filePath):
    gtqueries = []
    for line in open(filePath):
        gtqueries.append(line.strip())
    return gtqueries


# ONE TIME FUNCTIONS

# after making some fixes, find which queries are missing, put them in a sepaarte file.
def extractMissingQueries():
    missingQueries = open('NoBadAnswers/MissingQueries.txt', 'a')
    sqlWiz = SQLWizard('Snippets.db')
    questions = sqlWiz.getQuestions()
    skipQuestions = 12

    for question in questions:
        if skipQuestions != 0:
            skipQuestions -= 1
            continue

        qtext = ' '.join([question.qtitle, question.qtitle, question.qbody])
        top20QuestionWords = [item[0] for item in keywordsNFromText(qtext, 20)]

        # compose queries
        print('Composing queries...')
        # TODO: glue collocations together to form a single token
        top10QuestionWords = top20QuestionWords[:10]
        queries = list(constructQueries(top10QuestionWords, 3, ' '.join([question.qtitle, question.qbody])))
        queries.append(preprocessText(question.gtquery))

        for query in queries:
            print('Working with query :: ' + query)
            snippets = sqlWiz.getNSnippetsForQuery(query, -1)
            snippets = filterOutDuplicateSnippets(snippets, question)
            if (len(snippets) < 10):
                missingQueries.write('%s\n' % query)
                print(query + " -- missing")
                continue
    missingQueries.close()


# calculate intersections of words
def calcIntersections():
    missingQueries = open('NoBadAnswers/missingQueries.txt', 'a')
    intersectFile = open('NoBadAnswers/intersectionsWords.txt', 'w')
    sqlWiz = SQLWizard('Snippets.db')
    questions = sqlWiz.getQuestions()



    for question in questions:

        # extract top words from answers
        print('Extracting top answer words...')
        answers = sqlWiz.getAnswersForQID(question.qid)
        top20AnswersWords = [item[0] for item in keywordsFromAnswers(answers, 20)]
        # TODO: all answer words?

        # extract top words from question
        print('Extracting top question words...')
        qtext = ' '.join([question.qtitle, question.qtitle, question.qbody])
        top20QuestionWords = [item[0] for item in keywordsNFromText(qtext, 20)]

        # compose queries
        print('Composing queries...')
        # TODO: glue collocations together to form a single token
        top10QuestionWords = top20QuestionWords[:10]
        queries = list(constructQueries(top10QuestionWords, 3, qtext))
        queries.append(preprocessText(question.gtquery))
        print(queries)

        allProbesIntersections = []
        for query in queries:
            print('Working with query :: ' + query)
            snippets = sqlWiz.getNSnippetsForQuery(query, -1)
            snippets = filterOutDuplicateSnippets(snippets, question)
            snippets = snippets[:10]
            if (len(snippets) < 10):
                missingQueries.write('%s\n' % query)
                continue

            cleanSnippetTokens = [set(preprocessText(s.snippet).split()) for s in snippets]
            # TODO look for collocations from q and a, give them bigger weights

            questionTopWords = set(top20QuestionWords)
            answersTopWords = set(top20AnswersWords)

            aveIntersectionWQuestion = averageSnippetIntersection(cleanSnippetTokens, questionTopWords,
                                                                  set(query.split(' ')))
            aveIntersectionWAnswers = averageSnippetIntersection(cleanSnippetTokens, answersTopWords,
                                                                 set(query.split(' ')))
            totalIntersectionWQuestion = totalSnippetIntersection(cleanSnippetTokens, questionTopWords,
                                                                  set(query.split(' ')))
            totalIntersectionWAnswers = totalSnippetIntersection(cleanSnippetTokens, answersTopWords,
                                                                 set(query.split(' ')))

            probeIntersections = {'query': query, 'aveWQuest': aveIntersectionWQuestion,
                                  'aveWAns': aveIntersectionWAnswers, 'totWQuest': totalIntersectionWQuestion,
                                  'totWAns': totalIntersectionWAnswers}
            allProbesIntersections.append(probeIntersections)

        questionIntersections = {'qid': question.qid, 'qtitle': question.qtitle,
                                 'qbody': question.qbody, 'gtquery': question.gtquery,
                                 'yahooqid': question.yahooqid, 'probes': allProbesIntersections}
        intersectFile.write('%s\n' % json.dumps(questionIntersections))
    intersectFile.close()
    missingQueries.close()


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

    with open('distinctWordsQA.txt', 'a') as f:
        for w in distinctWords:
            f.write('%s\n' % w)


# exports all snippets to a text file. each row as a separate json
def exportSnippetsFromDB():
    connection = sqlite3.connect('KeywordRankingDB.db')
    connection.text_factory = lambda x: str(x, 'latin1')  # taking care of the encoding
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
                    jsonRow = json.dumps({'questID': questID, 'queryText': queryText,
                                          'docURL': docURL, 'snippet': snippet})
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
def importSnippetsFromText(pathToFile):
    connection = sqlite3.connect('Snippets.db')
    cursor = connection.cursor()
    print('Connected to DB')
    for line in open(pathToFile):
        jSnippet = json.loads(line.strip())
        query = preprocessText(jSnippet['queryText'].lower())
        print(query)
        docURL = jSnippet['docURL']
        snippet = jSnippet['snippet']
        sql = 'insert into snippets (querytext, docurl, snippet) values (?, ?, ?);'
        cursor.execute(sql, (query, docURL, snippet))
    connection.commit()
    connection.close()


# make sure that words in queries are in the same order as in the question
def updateQueries():
    with open('UpdatedQueries.txt', 'w') as fOut:
        gtqueries = loadLinesFromTextToList('gtqueries.txt')
        for line in open('AllSnippets.txt'):
            jSnippet = json.loads(line.strip())
            if jSnippet['queryText'] in gtqueries:
                continue
            queryTokens = jSnippet['queryText'].split()
            for p in permutations(queryTokens):
                jSnippet['queryText'] = ' '.join(p)
                fOut.write('%s\n' % json.dumps(jSnippet))


def characterNGramSimilarity(outFilepath, N):
    # for every question and every snippet look at how much they overlap using character n-grams
    def constructNGramsForText(text, N):
        return [text[i:i + N] for i in range(0, len(text) - N + 1)]

    intersectFile = open(outFilepath, 'w')
    sqlWiz = SQLWizard('Snippets.db')
    questions = sqlWiz.getQuestions()

    for question in questions:
        answers = sqlWiz.getAnswersForQID(question.qid)

        cleanQuestion = shrinkRepeatedChars(removePunctuation(' '.join([question.qtitle, question.qbody])))
        cleanAnswers = [shrinkRepeatedChars(removePunctuation(a.answerText)) for a in answers]
        # print(' '.join([question.qtitle, question.qbody]))
        # print(cleanQuestion)

        # input()
        # for a in answers:
            # print(a.answerText)

        # for a in cleanAnswers:
        #     print(a)

        # input()

        questionNGrams = set(constructNGramsForText(cleanQuestion, N))
        # print(questionNGrams)
        # input()
        answersNGrams = [set(constructNGramsForText(a, N)) for a in cleanAnswers]
        answersNGrams = set(itertools.chain(*answersNGrams))
        # for a in answersNGrams:
            # print(a)
        # input()

        # extract top words from question and compose queries
        print('Extracting top question words...')
        qtext = ' '.join([question.qtitle, question.qtitle, question.qbody])
        top10QuestionWords = [item[0] for item in Keywords.keywordsNFromText(qtext, 10)]
        print('Composing queries...')
        queries = list(constructQueries(top10QuestionWords, 3, qtext))
        queries.append(preprocessText(question.gtquery))
        # print(queries)

        allProbesIntersections = []

        for query in queries:
            print('Working with query :: ' + query)
            snippets = sqlWiz.getNSnippetsForQuery(query, 10)
            snippets = filterOutDuplicateSnippets(snippets, question)
            snippets = snippets[:10]
            if (len(snippets) == 0):
                continue

            cleanSnippets = [shrinkRepeatedChars(removePunctuation(s.snippet)) for s in snippets]
            # for s in cleanSnippets:
            #     print(s)
            snippetsNgrams = [set(constructNGramsForText(s, N)) for s in cleanSnippets]
            # print('Constructing ngrams')


            aveIntersectionWQuestion = averageSnippetIntersection(snippetsNgrams, questionNGrams, set([]))
            aveIntersectionWAnswers = averageSnippetIntersection(snippetsNgrams, answersNGrams, set([]))
            totalIntersectionWQuestion = totalSnippetIntersection(snippetsNgrams, questionNGrams, set([]))
            totalIntersectionWAnswers = totalSnippetIntersection(snippetsNgrams, answersNGrams, set([]))

            probeIntersections = {'query': query, 'aveWQuest': aveIntersectionWQuestion,
                                  'aveWAns': aveIntersectionWAnswers, 'totWQuest': totalIntersectionWQuestion,
                                  'totWAns': totalIntersectionWAnswers}
            allProbesIntersections.append(probeIntersections)

        questionIntersections = {'qid': question.qid, 'qtitle': question.qtitle, 'qbody': question.qbody,
                                 'gtquery': question.gtquery, 'yahooqid': question.yahooqid,
                                 'probes': allProbesIntersections}
        intersectFile.write('%s\n' % json.dumps(questionIntersections))
    intersectFile.close()


def findMisspelledWords(outputFilename):
    dictionaryFile = 'en_CA.txt'
    sqlWiz = SQLWizard('Snippets.db')
    questions = sqlWiz.getQuestions()
    dictionaryWords = [w.strip() for w in open(dictionaryFile)]
    misspelledTokens = set()
    allTokens = []

    for question in questions:
        answers = sqlWiz.getAnswersForQID(question.qid)

        cleanQuestion = preprocessText(' '.join([question.qtitle, question.qbody])).split()
        cleanAnswers = list(itertools.chain(*[preprocessText(a.answerText) for a in answers]))
        allTokens += cleanQuestion + cleanAnswers

    tokensSet = set(allTokens)

    for token in tokensSet:
        if token not in dictionaryWords:
            misspelledTokens.add(token)

    with open(outputFilename, 'w') as f:
        for t in misspelledTokens:
            f.write('%s\n' % t)
