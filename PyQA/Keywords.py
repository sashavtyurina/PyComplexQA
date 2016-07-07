"""These functions will be responsible for extracting keywords from text."""

from KLDWizard import KLDWizard
import Utils
import json
from operator import itemgetter
import operator
import numpy
import itertools

kldWiz = KLDWizard()




def keywordsNFromText(text, N):
    """Preprocess text, split into tokens. Return top N scored words by KL-divergence."""
    tokens = Utils.preprocessText(text).split(' ')
    sortedScoredWords = [i[0] for i in kldWiz.topNWordsFromTokens(tokens, N)]
    return sortedScoredWords


def scoredKeywordsNFromText(text, N):
    """Preprocess text, split into tokens. Return top N scored words by KL-divergence."""
    tokens = Utils.preprocessText(text).split(' ')
    return kldWiz.topNWordsFromTokens(tokens, N)


# given a list of answers extract N top words from them
# for the foreground model we use frequency of a term between answers as opposed to within answer
def keywordsFromAnswers(answers, N):
    def foregroundDistributionAnswers(_answers):
        # compose a string that would respresent between answer frequency
        numAnswers = len(_answers) * 1.0

        foregroundDistribution = {}
        cleanAnswers = [Utils.preprocessText(a.answerText) for a in _answers]
        cleanAnswers = [a for a in cleanAnswers if not a == '']
        answersTokens = [a.split(' ') for a in cleanAnswers]
        for aTokens in answersTokens:
            uniqueTokens = set(aTokens)

            for ut in uniqueTokens:
                if ut not in foregroundDistribution:
                    foregroundDistribution[ut] = 1.0
                else:
                    foregroundDistribution[ut] += 1.0

        foregroundDistribution.update((k, v / numAnswers) for k, v in foregroundDistribution.items())
        return foregroundDistribution

    # if there're 3 answers or less we use regular KL divergence
    if len(answers) < 4:
        return keywordsNFromText(' '.join([a.answerText for a in answers]), N)

    foregroundDistribution = foregroundDistributionAnswers(answers)
    return kldWiz.topNWordsFromTokensForeground(foregroundDistribution, N)


def allWeights():
    weights = []
    for i in range(0, 11):
        for j in range(0, 11 - i):
            for k in range(0, 11 - i - j):
                weights.append((round(i * 0.1, 2), round(j * 0.1, 2), round(k * 0.1, 2), round((10 - i - j - k) * 0.1, 2)))

    # weights = []
    # for i in range(0, 11):
    #     weights.append((round(i * 0.1, 2), round((10 - i) * 0.1, 2)))
    return weights


# given a gtquery and a list of sorted queries find the rank of the gtquery
def gtRankInDictionary(gtquery, scoredScoredProbes):
    counter = 1
    for item in scoredScoredProbes:
        if gtquery == item[0]:
            return counter
        counter += 1
    return counter


def topMWordsFromQueriesByOrder(queryTokens, M):
    """Return a list of M words from the list."""
    topMWords = []
    for t in queryTokens:
        if t not in topMWords:
            topMWords.append(t)
    return topMWords[:M]


def topMWordsbyfrequency(queryTokens, M):
    sortedTokensScored = sorted(KLDWizard.foregroundModel(queryTokens).items(), key=itemgetter(1), reverse=True)
    sortedTokens = [item[0] for item in sortedTokensScored[:M]]
    return sortedTokens


# given partial intersections for a single query and weights(4 numbers tuple) find query score
def queryScoreWithWeights(partialIntersections, weights):
    aveWAns = partialIntersections['aveWAns']
    aveWQuest = partialIntersections['aveWQuest']
    totalWAns = partialIntersections['totWAns']
    totWQuest = partialIntersections['totWQuest']
    return weights[0] * aveWAns + weights[1] * aveWQuest + weights[2] * totalWAns + weights[3] * totWQuest
    # return weights[0] * totalWAns + weights[1] * totWQuest  # param 1 dominates: 38, param 2 dominates: 34, mixed: 10
    # return weights[0] * aveWAns + weights[1] * aveWQuest  # param 1 dominates (> 0.8): 44, param 2 dominates: 27, mixed: 11


def gtqueryRankForWeights(partialIntersectionsList, gtquery, weights):
    scores = {}
    for pi in partialIntersectionsList:
        curQuery = pi['query']
        scores[curQuery] = queryScoreWithWeights(pi, weights)
    sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    gtQueryRankForWeight = gtRankInDictionary(gtquery, sortedScores)
    return gtQueryRankForWeight


def scoreQueriesWithWeight(partialIntersectionsList, weights):
    scores = {}
    for pi in partialIntersectionsList:
        curQuery = pi['query']
        scores[curQuery] = queryScoreWithWeights(pi, weights)
    sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    return sortedScores


def bestWeightsForQuestion(questionline):
    """
    Question line is a json object, containing a question text, gtquery.

    All probes abd their intersection scores.
    """
    weights = allWeights()

    question = json.loads(questionline)
    gtquery = Utils.preprocessText(question['gtquery'])
    partialIntersections = question['probes']

    ranksWeightsMap = {}
    for w in weights:
        ranksWeightsMap[w] = gtqueryRankForWeights(partialIntersections, gtquery, w)

    sortedRanks = sorted(ranksWeightsMap.items(), key=operator.itemgetter(1))
    bestWeights = sortedRanks[0][0]
    return bestWeights


def parameterSweep(inFilepath, outFilepath):

    weights = allWeights()
    equalWeights = (0.25, 0.25, 0.25, 0.25)

    with open(outFilepath, 'w') as outfile:

        for line in open(inFilepath):
            question = json.loads(line)
            qtitle = question['qtitle']
            qbody = question['qbody']
            gtquery = Utils.preprocessText(question['gtquery'])
            partialIntersections = question['probes']

            ranksWeightsMap = {}
            for w in weights:
                ranksWeightsMap[w] = gtqueryRankForWeights(partialIntersections, gtquery, w)

            sortedRanks = sorted(ranksWeightsMap.items(), key=operator.itemgetter(1))
            ranksOnly = [i[1] for i in sortedRanks]
            standartDev = numpy.std(ranksOnly)
            medianRank = numpy.median(ranksOnly)

            bestWeights = sortedRanks[0][0]
            scoredQueriesWithBestWeights = scoreQueriesWithWeight(partialIntersections, bestWeights)[:20]
            scoredQueriesWithEqualWeights = scoreQueriesWithWeight(partialIntersections, equalWeights)[:20]

            rankWithBestWeights = gtqueryRankForWeights(partialIntersections, gtquery, bestWeights)
            rankWithEqualWeights = gtqueryRankForWeights(partialIntersections, gtquery, equalWeights)

            # logging to the output file
            outfile.write('Question :: %s %s\n\n' % (qtitle, qbody))
            outfile.write('Ground truth query :: %s\n\n' % gtquery)

            outfile.write('Rank with best weights :: %d\n\n' % rankWithBestWeights)
            outfile.write('Rank with all weights equal to 0.25 :: %d\n\n' % rankWithEqualWeights)

            outfile.write('Standart deviation of ranks :: %f \n' % standartDev)
            outfile.write('Median of ranks :: %f \n\n' % medianRank)


            outfile.write('Scored queries with best weights %s :: \n' % str(bestWeights))
            for scoredQuery in scoredQueriesWithBestWeights:
                outfile.write('%s :: %f\n' % (scoredQuery[0], scoredQuery[1]))
            outfile.write('\n')

            outfile.write('Scored queries with equal weights ::\n')
            for scoredQuery in scoredQueriesWithEqualWeights:
                outfile.write('%s :: %f\n' % (scoredQuery[0], scoredQuery[1]))
            outfile.write('\n')

            outfile.write('Ranks after parameter sweep :: \n')
            for r in sortedRanks:
                outfile.write(str(r) + '\n')
            outfile.write('\n\n*******\n\n')


def precisionAtM(inFilepath, M):
    counter = 0
    pAtM = 0
    recallAtM = 0

    for line in open(inFilepath):
        counter += 1
        question = json.loads(line)
        qtitle = question['qtitle']
        gtquery = Utils.preprocessText(question['gtquery'])
        partialIntersections = question['probes']

        equalWeights = (0.25, 0.25, 0.25, 0.25)
        bestWeights = bestWeightsForQuestion(line)

        # Precision at M
        gtQueryRank = gtqueryRankForWeights(partialIntersections, gtquery, equalWeights)
        if gtQueryRank < M:
            pAtM += 1

        # Recall at M
        gttokens = set(gtquery.split(' '))
        scoredTopQueries = scoreQueriesWithWeight(partialIntersections, equalWeights)[:M]
        topQueriesNoScores = [item[0] for item in scoredTopQueries]
        topQueriesTokens = [query.split(' ') for query in topQueriesNoScores]
        topQueriesUniqueTokens = set(itertools.chain.from_iterable(topQueriesTokens))
        proportionOfGtTokens = len(topQueriesUniqueTokens.intersection(gttokens)) / len(gttokens)
        recallAtM += proportionOfGtTokens

        print('Qtitle :: ' + qtitle)
        print('GTQuery :: ' + gtquery)
        print('GTQuery rank :: %d' % gtQueryRank)
        print('Proportion of gt tokens in the top M queries :: %f' % proportionOfGtTokens)
        # print(scoreQueriesWithWeight(partialIntersections, equalWeights)[:M])
        print('\n***\n')

    pAtM /= counter
    recallAtM /= counter
    print('Total questions :: %d\n Precision at M :: %f' % (counter, pAtM))
    print('Total questions :: %d\n Recall at M :: %f' % (counter, recallAtM))


# sort queries by their score, sort their tokens by frequency
# calculate R@M, P@M
def precisionAtMFreqTokens(inFilepath, M):
    counter = 0

    recallKLDSingleTitle = 0
    recallKLDDoubleTitle = 0

    recalRerankedOrderEqWeights = 0
    recalRerankedFrequencyEqWeights = 0

    recallRerankedOrderBestWeights = 0
    recalRerankedFrequencyBestWeights = 0

    lengths = []


    for line in open(inFilepath):
        counter += 1
        question = json.loads(line)
        qtitle = question['qtitle']
        qbody = question['qbody']

        qtextSingleTitle = ' '.join([qtitle, qbody])
        lengths.append(len(qtextSingleTitle))
        continue


        gtquery = Utils.preprocessText(question['gtquery'])
        gttokens = set(gtquery.split(' '))
        partialIntersections = question['probes']

        # KLD
        qtextSingleTitle = ' '.join([qtitle, qbody])
        KLDTokensSingleTitle = set([item[0] for item in keywordsNFromText(qtextSingleTitle, M)])
        intersectionKLDSingle = len(KLDTokensSingleTitle.intersection(gttokens)) / len(gttokens)
        recallKLDSingleTitle += intersectionKLDSingle
        print('KLDTokensSingleTitle :: ' + str(KLDTokensSingleTitle))

        qtextDoubleTitle = ' '.join([qtitle, qtitle, qbody])
        KLDTokensDoubleTitle = set([item[0] for item in keywordsNFromText(qtextDoubleTitle, M)])
        intersectionKLDDouble = len(KLDTokensDoubleTitle.intersection(gttokens)) / len(gttokens)
        recallKLDDoubleTitle += intersectionKLDDouble
        print('KLDTokensDoubleTitle :: ' + str(KLDTokensDoubleTitle))

        # Reranked queries equal weights
        equalWeights = (0.25, 0.25, 0.25, 0.25)
        scoredTopQueries = scoreQueriesWithWeight(partialIntersections, equalWeights)[:M]
        topQueriesTokens = [item[0].split(' ') for item in scoredTopQueries]
        topQueriesFlatTokens = list(itertools.chain.from_iterable(topQueriesTokens))
        topMWordsByOrder = set(topMWordsFromQueriesByOrder(topQueriesFlatTokens, M))
        topMWordsByFrequency = set(topMWordsbyfrequency(topQueriesFlatTokens, M))

        intersectionQueriesEqWeightsOrder = len(topMWordsByOrder.intersection(gttokens)) / len(gttokens)
        intersectionQueriesEqWeightsFrequency = len(topMWordsByFrequency.intersection(gttokens)) / len(gttokens)
        print('Equal weights topMWordsByOrder :: ' + str(topMWordsByOrder))
        print('Equal weights topMWordsByFrequency :: ' + str(topMWordsByFrequency))

        recalRerankedOrderEqWeights += intersectionQueriesEqWeightsOrder
        recalRerankedFrequencyEqWeights += intersectionQueriesEqWeightsFrequency

        # Reranked queriesbest weights
        bestWeights = bestWeightsForQuestion(line)
        scoredTopQueries = scoreQueriesWithWeight(partialIntersections, bestWeights)[:M]
        topQueriesTokens = [item[0].split(' ') for item in scoredTopQueries]
        topQueriesFlatTokens = list(itertools.chain.from_iterable(topQueriesTokens))
        topMWordsByOrder = set(topMWordsFromQueriesByOrder(topQueriesFlatTokens, M))
        topMWordsByFrequency = set(topMWordsbyfrequency(topQueriesFlatTokens, M))

        intersectionQueriesBestWeightsOrder = len(topMWordsByOrder.intersection(gttokens)) / len(gttokens)
        intersectionQueriesBestWeightsFrequency = len(topMWordsByFrequency.intersection(gttokens)) / len(gttokens)

        print('Best weights topMWordsByOrder :: ' + str(topMWordsByOrder))
        print('Best weights topMWordsByFrequency :: ' + str(topMWordsByFrequency))

        recallRerankedOrderBestWeights += intersectionQueriesBestWeightsOrder
        recalRerankedFrequencyBestWeights += intersectionQueriesBestWeightsFrequency

        print('\n-----\n')

        gtQueryRank = gtqueryRankForWeights(partialIntersections, gtquery, equalWeights)
        print(gtQueryRank < M)

        print('Qtitle :: ' + qtitle)
        print('GTQuery :: ' + gtquery)
        print('Intersection at KLD single title :: %f' % intersectionKLDSingle)
        print('Intersection at KLD double title :: %f' % intersectionKLDDouble)

        print('Intersection reranked queries equal weights by order :: %f' % intersectionQueriesEqWeightsOrder)
        print('Intersection reranked queries equal weights by frequency :: %f' % intersectionQueriesEqWeightsFrequency)

        print('Intersection reranked queries best weights by order :: %f' % intersectionQueriesBestWeightsOrder)
        print('Intersection reranked queries best weights by frequency :: %f' % recalRerankedFrequencyBestWeights)

        print('\n***\n')

    print(lengths)
    print(sum(lengths) / len(lengths))

    # recallKLDSingleTitle /= counter
    # recallKLDDoubleTitle /= counter
    # recalRerankedOrderEqWeights /= counter
    # recalRerankedFrequencyEqWeights /= counter
    # recallRerankedOrderBestWeights /= counter
    # recalRerankedFrequencyBestWeights /= counter


    # print('Total questions :: %d' % counter)
    # print('recallKLDSingleTitle :: %f' % recallKLDSingleTitle)
    # print('recallKLDDoubleTitle :: %f' % recallKLDDoubleTitle)
    # print('recalRerankedOrderEqWeights :: %f' % recalRerankedOrderEqWeights)
    # print('recalRerankedFrequencyEqWeights :: %f' % recalRerankedFrequencyEqWeights)
    # print('recallRerankedOrderBestWeights :: %f' % recallRerankedOrderBestWeights)
    # print('recalRerankedFrequencyBestWeights :: %f' % recalRerankedFrequencyBestWeights)

    print('\n***\n')



if __name__ == '__main__':
    parameterSweep('intersections.txt', 'paramSweep.txt')
