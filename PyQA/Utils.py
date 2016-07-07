import json
import re
import sqlite3
from itertools import permutations
import itertools
from Keywords import *
from SQLWizard import SQLWizard
from KLDWizard import KLDWizard
import operator


def recallAtM(gtquery, rankedWords, M):
    gtqueryTokens = gtquery.split()
    accum = 0
    for word in rankedWords[:M]:
        splitWords = word.split()
        for w in splitWords:
            if w in gtqueryTokens:
                accum += 1
    return accum / M


def precisionAtM(gtquery, rankedWords, M):
    gtqueryTokens = gtquery.split()
    accum = 0
    for word in rankedWords[:M]:
        splitWords = word.split()
        for w in splitWords:
            if w in gtqueryTokens:
                accum += 1
    if len(gtqueryTokens) == 0:
        return 0
    return accum / len(gtqueryTokens)

# removes punctuations from the string
def removePunctuation(str):
    str = re.sub(r'\n', ' ', str)
    str = re.sub("[^A-Za-z\s\d\-']", ' ', str)
    str = re.sub("(?<![A-Za-z\d])'", ' ', str)
    str = re.sub("'(?![A-Za-z\d])", ' ', str)
    str = re.sub("(?<![A-Za-z\d])-", ' ', str)
    str = re.sub("-(?![A-Za-z\d])", ' ', str)
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
    return re.sub(r'https?://(www\.)?([^\/]+)\.[^\s]*\s', '\g<2> ', str)


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


def s_stemmerSmart(tokens):
    def s_stem(word):
        if re.match('.*[^ea]ies$', word):
            return re.sub('ies$', 'y', word)
        if re.match('.*[^oae]es$', word):
            return re.sub('es$', 'e', word)
        if re.match('.*[^us]s$', word):
            return re.sub("(?<!')s$", '', word)
        return word
    uniqTokens = list(set(tokens))

    resultTokens = []
    for t in tokens:
        if s_stem(t) == t:
            resultTokens.append(t)
        else:
            if s_stem(t) in uniqTokens:  # they're not equal
                resultTokens.append(s_stem(t))
                continue
            else:
                resultTokens.append(t)
    return resultTokens


# performs text cleaning. Use this to do all the text cleaning
def preprocessText(text):
    text = removeURLs(text)
    text = removePunctuation(text)
    text = shrinkRepeatedChars(text)
    tokens = text.split(' ')
    tokens = dropStopWords(tokens)
    # tokens = s_stemmer(tokens)
    # tokens = s_stemmerSmart(tokens)
    tokens = removeShortTokens(tokens, 2)
    return ' '.join(tokens)


# given a list of tokens, return all queries of length queryLength
def constructQueries(tokens, queryLength):
    def addOne(queries, tokens):
        newQueries = {}
        for q in queries.items():
            for i in range(q[1] + 1, len(tokens)):
                # check if these tokens (or bigrams) overlap
                if len(set(q[0].split()).intersection(set(tokens[i].split()))) == 0:
                    qq = ' '.join([q[0], tokens[i]])
                    newQueries[qq] = max(q[1], i)
        return newQueries


    queriesOfLengths = {}
    queries = {}

    # sort tokens in order of their occurence in the initial question
    # print('Found collocations: ' + str(findCollocations(rawQuestion)))
    # tokens += findCollocations(rawQuestion)
    # sortedTokens = sortTokens(tokens, rawQuestion)

    # print('raw question :: ' + str(rawQuestion))
    # print('sorted tokens :: ' + str(sortedTokens))

    # start by creating all single word queries
    for i in range(0, len(tokens)):
        queries[tokens[i]] = i
    queriesOfLengths[1] = queries.keys()

    # append one word to existing queries
    for i in range(1, queryLength):
        queries = addOne(queries, tokens)
        queriesOfLengths[i + 1] = queries.keys()

    # print('queries :: ' + str(queriesOfLengths[queryLength]))
    return queriesOfLengths[queryLength]


# order tokens the same way they appear in the question
def sortTokens(tokensToSort, rawQuestion):
    # for every token find its first occurence in the initial string
    # then sort based on these indecies
    rawQuestion = preprocessText(rawQuestion)
    tokensInd = {}
    for t in tokensToSort:
        if t not in tokensInd.keys():
            ind = rawQuestion.find(t)
            if ind == -1:
                ind = rawQuestion.find(t[:-1])
            tokensInd[t] = ind
    # print(tokensInd)
    sortedInd = sorted(tokensInd.items(), key=operator.itemgetter(1))
    sortedTokens = [i[0] for i in sortedInd]

    return sortedTokens


# find collocations and glue them together as a single token
# TODO: add answers text here as well?
def findCollocations(rawQuestion):
    blocks = [b.strip() for b in re.split('[.,\?\!\-\:\;\(\)\{\}\[\]]+', rawQuestion) if b.strip() != '']
    blocksTokens = [preprocessText(b).split() for b in blocks]
    N = 2
    blocksBigrams = [[' '.join(tokens[i: i + N]) for i in range(0, len(tokens) - N + 1)] for tokens in blocksTokens]
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

    return repBigrams


def findCollocations1(rawQuestion):
    blocks = [b.strip() for b in re.split('[.,\?\!\-\:\;\(\)\{\}\[\]]+', rawQuestion) if b.strip() != '']
    blocksTokens = [preprocessText(b).split() for b in blocks]
    # print('Block tokens :: ' + str(blocksTokens))

    goOn = True
    N = 2
    blocksCollocations = []
    while goOn:
        newCollocations = [[' '.join(tokens[i: i + N]) for i in range(0, len(tokens) - N + 1)] for tokens in blocksTokens]
        # print('newCollocations :: ' + str(newCollocations))
        flatBigrams = list(itertools.chain.from_iterable(newCollocations))

        # find repetitive bigrams
        freqBigrams = {}
        for b in flatBigrams:
            if b in freqBigrams.keys():
                freqBigrams[b] += 1
            else:
                freqBigrams[b] = 1
        # print('Freq bigrams ' + str(freqBigrams))
        repBigrams = [b[0] for b in freqBigrams.items() if b[1] > 1]

        if len(repBigrams) == 0:
            goOn = False
        else:
            N += 1
            blocksCollocations += repBigrams

    resCollocations = []
    for c in blocksCollocations:
        curCollocation = c
        intersects = False
        for cc in blocksCollocations:
            if c == cc:
                continue
            if curCollocation in cc:
                intersects = True
                break

        if not intersects:
            resCollocations.append(curCollocation)

    print('resCollocations :: ' + str(resCollocations))
    return resCollocations


def averageSnippetIntersection(snippetTokensSets, topWordsSet, queryTokensSet):
    intersections = []
    # print('Top words :: ' + str(topWordsSet))
    # print('Query tokens :: ' + str(queryTokensSet))
    if len(snippetTokensSets) == 0:
        raise ValueError('Empty set of snippets passed.')

    for singleSnippetTokens in snippetTokensSets:
        # print('Snippet tokens initial:: ' + str(singleSnippetTokens))
        # print('Top words :: ' + str(topWordsSet))
        # print('\n\n')


        # remove query tokens from the snippet
        singleSnippetTokens.difference_update(queryTokensSet)

        # words that are in common btw the snippet and the question
        intersection = singleSnippetTokens.intersection(topWordsSet)
        intersectionLength = len(intersection)

        snippetLength = len(singleSnippetTokens)
        if snippetLength == 0:
            continue
        # print('Intersection :: ' + str(intersection))
        # print('Intersection length :: ' + str(intersectionLength))
        # print('Snippet length :: ' + str(snippetLength))


        # what fraction of the snippet is also in the question
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

    if len(allSnippetsTokensSet) == 0:
        raise ValueError('Empty set of snippet tokens in totalSnippetIntersection.')
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
    # remove the snippets that are the same as each other
    # then remove snippets that are the same as the question

    uniqueSnippets = []
    for s in snippets:
        exists = False
        for us in uniqueSnippets:
            if us.docURL == s.docURL or us.snippet == s.snippet:
                exists = True
                break
        if exists:
            continue
        uniqueSnippets.append(s)


    cleanSnippets = []
    questionTokens = set(preprocessText(' '.join([question.qtitle, question.qbody])).split(' '))
    for s in uniqueSnippets:

        if question.yahooqid and question.yahooqid in s.docURL:
            continue
        snippetTokens = set(preprocessText(s.snippet).split(' '))

        if len(snippetTokens) == 0:
            continue
        intersectionFraction = len(snippetTokens.intersection(questionTokens)) / len(snippetTokens)
        if intersectionFraction > 0.75:
            print('Intersection fraction :: %f' % intersectionFraction)
            print('Dublicate snippet :: %s\n' % s.snippet)
            continue
        cleanSnippets.append(s)
    return cleanSnippets


# rerank words from queries by their score
# given a list of scored queries, calculate the reranking of the query words
# each word would have a score of a sum of all queries it is in
def rerankQueryWordsWithScores(scoredQueries, collocations):
    wordsScores = {}
    for s in scoredQueries:
        queryText = s[0]
        queryScore = s[1]

        if len(collocations) == 0:
            words = queryText.split()
        else:
            queryTokens = []
            for c in collocations:
                if c in queryText:
                    queryTokens.append(c)
                    queryText = queryText.replace(c, '')
            queryTokens += queryText.split()
            words = queryTokens


        for w in words:
            if w in wordsScores.keys():
                wordsScores[w] += queryScore
            else:
                wordsScores[w] = queryScore
    sortedWordsScores = sorted(wordsScores.items(), key=operator.itemgetter(1), reverse=True)
    return sortedWordsScores


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
    missingQueries = open('NoBadAnswers/missingQueries2.txt', 'w')
    intersectFile = open('NoBadAnswers/intersectionsWordsFixedTyposBigrams.txt', 'w')
    sqlWiz = SQLWizard('Snippets.db')
    questions = sqlWiz.getQuestions()


    count = 19

    for question in questions:
        if count != 0:
            count -= 1
            continue

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
        queries = list(constructQueries(top10QuestionWords, 3, ' '.join([question.qtitle, question.qbody])))
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
def importQuestionsFromText(pathToFile, pathToDB):
    if pathToFile == '':
        pathToFile = 'questions.txt'
    if pathToDB == '':
        pathToDB = 'Snippets.db'
    qid = 1
    connection = sqlite3.connect(pathToDB)
    cursor = connection.cursor()
    print('Connected to DB')
    for line in open(pathToFile):
        jQuestion = json.loads(line.strip())
        qtitle = jQuestion['qtitle']
        qbody = jQuestion['qbody']
        bestAnswer = jQuestion['bestanswer']
        # gtquery = jQuestion['gtquery']
        # yahooqid = jQuestion['yahooqid']
        # sql = 'insert into questions (qtitle, qbody, gtquery, yahooqid) values (?, ?, ?, ?);'
        sql = 'insert into questions (qid, qtitle, qbody) values (?, ?, ?);'
        # cursor.execute(sql, (qtitle, qbody, gtquery, yahooqid))
        cursor.execute(sql, (qid, qtitle, qbody))
        # qid = cursor.lastrowid
        answers = jQuestion['answers']
        for a in answers:
            best = False
            if a == bestAnswer:
                best = True
            sql = 'insert into answers (qid, answertext, best) values (?, ?, ?)'
            cursor.execute(sql, (qid, a, best))
        qid += 1
    connection.commit()
    connection.close()


# import snippets from text file to a db
def importSnippetsFromText(pathToFile, pathToDB):
    if pathToDB == '':
        pathToDB = 'Snippets.db'
    connection = sqlite3.connect(pathToDB)
    cursor = connection.cursor()
    print('Connected to DB')
    for line in open(pathToFile):
        jSnippet = json.loads(line.strip())
        query = preprocessText(jSnippet['queryText'].lower())
        print(query)
        docURL = jSnippet['url']
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


def selectDistinctWords():
    """
    Given a set of json questions, select distinct tokens from them.

    Afterwards sort and delete duplicates:
    sort DistinctWords.txt > DistinctWordsSorted.txt
    uniq DistinctWordsSorted.txt > DistinctWordsUniq.txt
    """
    with open('DistinctWordsNew.txt', 'w') as fOut:
        for line in open('SelectedQuestions.txt'):
            qJson = json.loads(line.strip())
            qtitle = qJson['qtitle']
            qbody = qJson['qbody']
            rawQuestion = qtitle + ' ' + qbody
            tokens = set(Utils.preprocessText(rawQuestion).split())
            for q in tokens:
                fOut.write('%s\n' % q)



