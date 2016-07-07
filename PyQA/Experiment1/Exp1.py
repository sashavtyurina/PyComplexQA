"""Here we have all the final versions of
functions and all thing ready to run the full experiments from beginning till the end."""

import sys
sys.path.insert(0, '../')

import Keywords
import Utils
import json
from SQLWizard import SQLWizard
import itertools
import QAS


#################################
#       Construct queries       #
#################################
#
def constructAllQueries():
    with open('QueriesFromSelectedQuestions.txt', 'w') as fOut:
        for line in open('SelectedQuestions.txt'):
            qJson = json.loads(line.strip())
            qtitle = qJson['qtitle']
            qbody = qJson['qbody']
            print('qtitle :: ' + qtitle)
            print('qbody :: ' + qbody)
            queries = constructQueriesToGoogle(qtitle, qbody)
            for q in queries:
                fOut.write('%s\n' % q)


def constructQueriesToGoogle(qtitle, qbody):
    """
    There're several ways we can construct queries.

    1. Take top 10 words by KLD for qtitle + qbody -> construct triples
    2. Take top 10 words by KLD for qtitle*2 + qbody -> construct triples
    3. Take top 10 by KLD (title + body) + glue together repeating bigrams and use them as tokens -> construct triples
    4. Take top 10 by KLD (title*2 + body) + glue together repeating bigrams and use them as tokens -> construct triples
    5. Fix typos and 1.
    6. Fix typos and 2.
    7. Fix typos and 3.
    8. Fix typos and 4.
    In this function we will implement 1-4. We can fix typos in the initial corpus and run it again to get 5-8.
    Run this when you want to construct all possible queries for new questions and have them googled.
    """
    rawQuestion = qtitle + ' ' + qbody

    # 1. Top 10 words by KLD
    keywordsSingleTitle = Utils.sortTokens(Keywords.keywordsNFromText(rawQuestion, 10), rawQuestion)
    print('KLD. Single title :: %s\n' % str(keywordsSingleTitle))

    # 2. Top 10 by KLD with doule title
    keywordsDoubleTitle = Utils.sortTokens(Keywords.keywordsNFromText(qtitle + ' ' + rawQuestion, 10), rawQuestion)
    print('KLD. Double title :: %s\n' % str(keywordsDoubleTitle))

    # 3 and 4. repeating collocations
    repCollocations = Utils.findCollocations1(rawQuestion)

    keywordsSingleTitleColloc = Utils.sortTokens(keywordsSingleTitle + repCollocations, rawQuestion)
    print('KLD + collocations. Single title :: %s\n' % str(keywordsSingleTitleColloc))

    keywordsDoubleTitleColloc = Utils.sortTokens(keywordsDoubleTitle + repCollocations, rawQuestion)
    print('KLD + collocations. Double title :: %s\n' % str(keywordsDoubleTitleColloc))


    # Now we have 4 lists of keywords. Construct queries.
    queriesSingleTitle = list(Utils.constructQueries(keywordsSingleTitle, 3))
    queriesDoubleTitle = list(Utils.constructQueries(keywordsDoubleTitle, 3))
    queriesSingleTitleCollocations = list(Utils.constructQueries(keywordsSingleTitleColloc, 3))
    queriesDoubleTitleCollocations = list(Utils.constructQueries(keywordsDoubleTitleColloc, 3))

    # We don't want to google the same query twice, so we will get rid of all the duplicates
    return set(queriesSingleTitle + queriesDoubleTitle +
               queriesSingleTitleCollocations + queriesDoubleTitleCollocations)


def constructQueriesKLDSingleTitle(qtitle, qbody):
    # 1. Top 10 words by KLD
    rawQuestion = qtitle + ' ' + qbody
    keywordsSingleTitle = Utils.sortTokens(Keywords.keywordsNFromText(rawQuestion, 10), rawQuestion)
    queriesSingleTitle = list(Utils.constructQueries(keywordsSingleTitle, 3))
    return queriesSingleTitle


def constructQueriesKLDDoubleTitle(qtitle, qbody):
    # 2. Top 10 by KLD with doule title
    rawQuestion = qtitle + ' ' + qbody
    keywordsDoubleTitle = Utils.sortTokens(Keywords.keywordsNFromText(qtitle + ' ' + rawQuestion, 10), rawQuestion)
    queriesDoubleTitle = list(Utils.constructQueries(keywordsDoubleTitle, 3))
    return queriesDoubleTitle


def constructQueriesSingleTitleCollocations(qtitle, qbody):
    # 3 and 4. repeating collocations
    rawQuestion = qtitle + ' ' + qbody
    repCollocations = Utils.findCollocations1(rawQuestion)
    keywordsSingleTitle = Utils.sortTokens(Keywords.keywordsNFromText(rawQuestion, 10), rawQuestion)
    keywordsSingleTitleColloc = Utils.sortTokens(keywordsSingleTitle + repCollocations, rawQuestion)
    queriesSingleTitleCollocations = list(Utils.constructQueries(keywordsSingleTitleColloc, 3))
    return queriesSingleTitleCollocations


def constructQueriesDoubleTitleCollocations(qtitle, qbody):
    # 3 and 4. repeating collocations
    rawQuestion = qtitle + ' ' + qbody
    repCollocations = Utils.findCollocations1(rawQuestion)
    keywordsDoubleTitle = Utils.sortTokens(Keywords.keywordsNFromText(qtitle + ' ' + rawQuestion, 10), rawQuestion)
    keywordsDoubleTitleColloc = Utils.sortTokens(keywordsDoubleTitle + repCollocations, rawQuestion)
    queriesDoubleTitleCollocations = list(Utils.constructQueries(keywordsDoubleTitleColloc, 3))
    return queriesDoubleTitleCollocations

#################################
#     Construct queries end     #
#################################


#################################
#          Score query          #
#################################


def constructNGramsForText(text, N):
    text = Utils.preprocessText(text)
    if len(text) < N:
        return []
    return [text[i:i + N] for i in range(0, len(text) - N + 1)]


def scoreQueryWithCharNGramOverlap(query, sqlWiz, question, questionNGrams, answersNGrams, N):
    missingQueriesFile = open('missingQueries.txt', 'a')

    snippets = sqlWiz.getNSnippetsForQuery(query, -1)
    if (len(snippets) == 0):
        missingQueriesFile.write('%s\n' % query)
        return (0, 0, 0, 0)

    snippets = Utils.filterOutDuplicateSnippets(snippets, question)
    snippets = snippets[:10]
    if len(snippets) == 0:
        return (0, 0, 0, 0)

    snippetsNgrams = [set(constructNGramsForText(s.snippet, N)) for s in snippets]


    aveIntersectionWQuestion = Utils.averageSnippetIntersection(snippetsNgrams, questionNGrams, set([]))
    aveIntersectionWAnswers = Utils.averageSnippetIntersection(snippetsNgrams, answersNGrams, set([]))
    totalIntersectionWQuestion = Utils.totalSnippetIntersection(snippetsNgrams, questionNGrams, set([]))
    totalIntersectionWAnswers = Utils.totalSnippetIntersection(snippetsNgrams, answersNGrams, set([]))

    return (aveIntersectionWQuestion, aveIntersectionWAnswers, totalIntersectionWQuestion, totalIntersectionWAnswers)


def scoreQueryWithWordOverlap(query, sqlWiz, question, questionTopWords, answersTopWords):

    # query: Str
    # questionTopWords: set(Str)
    # answersTopWords: set(Str)

    missingQueriesFile = open('missingQueries.txt', 'a')

    snippets = sqlWiz.getNSnippetsForQuery(query, -1)

    print('Found snippets for query :: %s' % query)
    print([s.snippet for s in snippets])
    if (len(snippets) == 0):
        missingQueriesFile.write('%s\n' % query)
        return (0, 0, 0, 0)

    snippets = Utils.filterOutDuplicateSnippets(snippets, question)
    snippets = snippets[:10]
    if len(snippets) == 0:
        return (0, 0, 0, 0)

    for s in snippets:
        print(s.snippet)

    print('\n**************\n')
    snippetTokens = [set(Utils.preprocessText(s.snippet).split()) for s in snippets]
    print(snippetTokens)

    queryTokens = set(query.split(' '))

    aveIntersectionWQuestion = Utils.averageSnippetIntersection(snippetTokens, questionTopWords, queryTokens)
    aveIntersectionWAnswers = Utils.averageSnippetIntersection(snippetTokens, answersTopWords, queryTokens)

    totalIntersectionWQuestion = Utils.totalSnippetIntersection(snippetTokens, questionTopWords, queryTokens)
    totalIntersectionWAnswers = Utils.totalSnippetIntersection(snippetTokens, answersTopWords, queryTokens)

    print((aveIntersectionWQuestion, aveIntersectionWAnswers, totalIntersectionWQuestion, totalIntersectionWAnswers))
    # input()
    return (aveIntersectionWQuestion, aveIntersectionWAnswers, totalIntersectionWQuestion, totalIntersectionWAnswers)


#################################
#        Score query end        #
#################################


#################################
#       Utilitiy functions      #
#################################

def selectDistinctWordsFromDatabase(pathToDB):
    missingWords = open('missingWords.txt', 'a')
    sqlWiz = SQLWizard(pathToDB)
    questions = sqlWiz.getQuestions()

    for question in questions:
        allAnswers = sqlWiz.getAnswersForQID(question.qid)
        allAnswersText = ' '.join([a.answerText for a in allAnswers])
        aTokens = set(Utils.preprocessText(allAnswersText).split())

        rawQuestion = question.qtitle + ' ' + question.qbody
        qtokens = set(Utils.preprocessText(rawQuestion).split())

        allTokens = aTokens.union(qtokens)
        for t in allTokens:
            missingWords.write('%s\n' % t)

    missingWords.close()


def formatQuestionsForManualLabeling(pathToDB, outputfile):
    output = open(outputfile, 'w')
    sqlWiz = SQLWizard(pathToDB)
    questions = sqlWiz.getQuestions()

    count = 1
    for question in questions:
        output.write('%d. %s\n%s\n\n*******\n\n' % (count, question.qtitle, question.qbody))
        count += 1

#################################
#     Utilitiy functions end    #
#################################


# calculate intersections of words
def calculateIntersections(pathToDB):
    missingQueries = open('missingQueries.txt', 'a')
    intersectFile = open('ResultsOldDataset/NoStem_SingleTitleColloc_WordOverlap.txt', 'w')
    sqlWiz = SQLWizard(pathToDB)
    questions = sqlWiz.getQuestions()

    questionCounter = 0
    skipQuestions = 0
    upTo = 100

    for question in questions:
        questionCounter += 1

        if skipQuestions != 0:
            skipQuestions -= 1
            continue

        if questionCounter > upTo:
            continue

        # with gt query?
        gtquery = question.gtquery

        rawQuestion = question.qtitle + ' ' + question.qbody
        print('%d. Raw question :: %s\n' % (questionCounter, rawQuestion))

        # queries = constructQueriesToGoogle(question.qtitle, question.qbody)
        # for q in queries:
        #     snippets = sqlWiz.getNSnippetsForQuery(q, -1)
        #     if len(snippets) < 10:
        #         missingQueries.write('%s\n' % q)
        # continue


        # extract top words from question
        top20QWords = Keywords.keywordsNFromText(rawQuestion, 20)
        setTop20QWords = set(top20QWords)
        # print('top20QuestionWords :: %s\n' % str(top20QWords))



        # extract top words from answers

        # 1. using best answer only (best as selected by user)
        # bestAnswer = sqlWiz.getBestAnswerForQID(question.qid).answerText
        # top20BAWords = Keywords.keywordsNFromText(bestAnswer, 20)
        # setTop20AWords = set(top20BAWords)
        # answersForCharNGramOverlap = [bestAnswer]
        # print('top20BestAnswerWords :: %s\n' % str(top20BAWords))

        # 2. using all answers
        allAnswers = sqlWiz.getAnswersForQID(question.qid)
        top20AWords = Keywords.keywordsFromAnswers(allAnswers, 20)
        setTop20AWords = set(top20AWords)
        answersForCharNGramOverlap = [a.answerText for a in allAnswers]
        print('top20AnswersWords :: %s\n' % str(setTop20AWords))

        # construct queries
        queries = constructQueriesKLDSingleTitle(question.qtitle, question.qbody)
        queries.append(gtquery)

        allProbesIntersections = []
        for query in queries:
            print('Working with query :: %s' % query)

            # word overlap
            queryScores = scoreQueryWithWordOverlap(query, sqlWiz, question, setTop20QWords, setTop20AWords)


            # character N-gram overlap
            # N = 3
            # questionNGrams = set(constructNGramsForText(rawQuestion, N))
            # answersNGrams = [set(constructNGramsForText(a, N)) for a in answersForCharNGramOverlap]
            # answersNGrams = set(itertools.chain(*answersNGrams))
            # queryScores = scoreQueryWithCharNGramOverlap(query, sqlWiz, question, questionNGrams, answersNGrams, 3)


            probeIntersections = {'query': query, 'aveWQuest': queryScores[0],
                                  'aveWAns': queryScores[1], 'totWQuest': queryScores[2],
                                  'totWAns': queryScores[3]}

            allProbesIntersections.append(probeIntersections)


        questionIntersections = {'qid': question.qid, 'qtitle': question.qtitle,
                                 'qbody': question.qbody, 'gtquery': question.gtquery,
                                 'yahooqid': question.yahooqid, 'probes': allProbesIntersections}

        intersectFile.write('%s\n' % json.dumps(questionIntersections))

    intersectFile.close()
    missingQueries.close()


def rankQueries(pathToDB, pathToIntersectionsFile, outputFile, withCollocations):


    sqlWiz = SQLWizard(pathToDB)
    output = open(outputFile, 'w')
    equalWeights = (0.25, 0.25, 0.25, 0.25)

    M = 3
    recallAtMAccum = 0
    precisionAtMAccum = 0
    counter = 0

    newlyCreatedQueries = open('newlyCreatedQueries.txt', 'w')

    for line in open(pathToIntersectionsFile):
        question = json.loads(line)
        qid = question['qid']
        qtitle = question['qtitle']
        qbody = question['qbody']
        questionObj = QAS.QuestionSQL(qid, qtitle, qbody, None, None)
        rawQuestion = qtitle + ' ' + qbody

        gtquery = question['gtquery'] if question['gtquery'] else ''

        output.write('%s<br/>\n' % ' '.join([qtitle, qbody]))

        partialIntersections = question['probes']
        scoredProbes = Keywords.scoreQueriesWithWeight(partialIntersections, equalWeights)

        if withCollocations:
            collocations = Utils.findCollocations1(' '.join([qtitle, qbody]))
        else:
            collocations = []

        scoredWords = Utils.rerankQueryWordsWithScores(scoredProbes, collocations)

        # question top words
        top20QWords = Keywords.keywordsNFromText(rawQuestion, 20)
        setTop20QWords = set(top20QWords)

        # answers top words
        allAnswers = sqlWiz.getAnswersForQID(questionObj.qid)
        top20AWords = Keywords.keywordsFromAnswers(allAnswers, 20)
        setTop20AWords = set(top20AWords)

        # deal with the newly created question
        newlyCreatedQuery = ' '.join([w[0] for w in scoredWords[:5]])
        newlyCreatedQueryScores = scoreQueryWithWordOverlap(newlyCreatedQuery, sqlWiz, questionObj, setTop20QWords, setTop20AWords)
        newlyCreatedQueryScoresJSON = {"query": newlyCreatedQuery, "totWQuest": newlyCreatedQueryScores[0],
                                       "aveWQuest": newlyCreatedQueryScores[1],
                                       "totWAns": newlyCreatedQueryScores[2],
                                       "aveWAns": newlyCreatedQueryScores[3]}
        partialIntersections.append(newlyCreatedQueryScoresJSON)
        scoredProbes = Keywords.scoreQueriesWithWeight(partialIntersections, equalWeights)
        scoredNewlyCreatedQuery = Keywords.scoreQueriesWithWeight([newlyCreatedQueryScoresJSON], equalWeights)


        for s in scoredProbes[:20]:
            queryStr = s[0]
            searchRef = 'http://www.google.com/search?hl=en&q=' + queryStr
            highlight = '->' if queryStr == newlyCreatedQuery else ''
            output.write('%s <a href=\"%s\">%s</a> :: %s <br/>\n' % (highlight, searchRef, queryStr, str(s[1])))

        searchRef = 'http://www.google.com/search?hl=en&q=' + newlyCreatedQuery
        output.write('Newly created query :: <a href=\"%s\">%s</a> :: %s <br/>\n' % (searchRef, newlyCreatedQuery, str(scoredNewlyCreatedQuery[0][1])))
        # output.write('Newly created query :: <br/>\n %s' % str(scoredNewlyCreatedQuery))

        output.write('<br/>\n<b>%s</b><br/>\n' % 'Reranked words:')
        for w in scoredWords:
            output.write('%s -- %f<br/>\n' % (w[0], w[1]))


        rankedWordsOnly = [w[0] for w in scoredWords]
        recallAtM = Utils.recallAtM(gtquery, rankedWordsOnly, M)
        precisionAtM = Utils.precisionAtM(gtquery, rankedWordsOnly, M)

        recallAtMAccum += recallAtM
        precisionAtMAccum += precisionAtM
        counter += 1

        output.write('<br/>\nRecall at %d :: %f<br/>\n' % (M, recallAtM))
        output.write('Precision at %d :: %f<br/>\n' % (M, precisionAtM))
        output.write('%s<br/>\n' % '\n****\n')

        newlyCreatedQuery = ' '.join([w[0] for w in scoredWords[:5]])
        newlyCreatedQueries.write('%s\n' % newlyCreatedQuery)


    output.write('%s<br/>Total:<br/>\n' % '\n****\n')
    output.write('Recall at %d :: %f<br/>\n' % (M, recallAtMAccum / counter))
    output.write('Precision at %d :: %f<br/>\n' % (M, precisionAtMAccum / counter))
    output.close()
    newlyCreatedQueries.close()


def main():
    # rankQueries('SnippetsExp1.db', 'Results/WordOverlap/NoStem_WordOverlap_AllAnswers_KLDDoubleTitle.txt',
                # 'Results/WordOverlap/NoStem_WordOverlap_AllAnswers_KLDDoubleTitle.html', False)
    # calculateIntersections('../Snippets.db')
    # formatQuestionsForManualLabeling('SnippetsExp1.db', 'ForManualLabeling.txt')
    # constructAllQueries()
    # selectDistinctWordsFromDatabase('../Snippets.db')
    # Utils.importSnippetsFromText('newlyCreatedQueriesSearchResults.txt', 'SnippetsExp1.db')
    # Utils.importQuestionsFromText('SelectedQuestionsDone.txt', 'SnippetsExp1.db')


if __name__ == "__main__":
    main()
