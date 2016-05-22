# these functions will be responsible for extracting keywords from text
from KLDWizard import KLDWizard
from Utils import *
from operator import itemgetter
import operator

kldWiz = KLDWizard()

def keywordsNFromText(text, N):
    tokens = preprocessText(text).split(' ')
    return kldWiz.topNWordsFromTokens(tokens, N)

# given a list of answers extract N top words from them
# for the foreground model we use frequency of a term between answers as opposed to within answer
def keywordsFromAnswers(answers, N):
    def foregroundDistributionAnswers(_answers):
        # compose a string that would respresent between answer frequency
        numAnswers = len(_answers)*1.0

        foregroundDistribution = {}
        cleanAnswers = [preprocessText(a.answerText) for a in _answers]
        cleanAnswers = [a for a in cleanAnswers if not a == '']
        answersTokens = [a.split(' ') for a in cleanAnswers]
        for aTokens in answersTokens:
            uniqueTokens = set(aTokens)

            for ut in uniqueTokens:
                if ut not in foregroundDistribution:
                    foregroundDistribution[ut] = 1.0
                else:
                    foregroundDistribution[ut] += 1.0

        foregroundDistribution.update((k, v/numAnswers) for k,v in foregroundDistribution.items())
        return foregroundDistribution


    # if there're 3 answers or less we use regular KL divergence
    if len(answers) < 4:
        return keywordsNFromText(' '.join([a.answerText for a in answers]), N)

    foregroundDistribution = foregroundDistributionAnswers(answers)
    return kldWiz.topNWordsFromTokensForeground(foregroundDistribution, N)



def parameterSweep(inFilepath, outFilepath):
    def allWeights():
        weights = []
        for i in range(0,11):
            for j in range(0, 11 - i):
                for k  in range(0, 11 - i - j):
                    weights.append((round(i*0.1,2), round(j*0.1,2), round(k*0.1,2), round((10-i-j-k)*0.1, 2)))
        return weights

    # given a tuple of 4 weights and a list of probes, find the rank of the gtquery for the gievn weights
    def probeRankForWeights(probeScores, weights, gtquery):
        scoredProbes = {}
        for ps in probeScores:
            probe = ps['query']

            aveWAns = ps['aveWAns']
            aveWQuest = ps['aveWQuest']
            totalWAns = ps['totWAns']
            totWQuest = ps['totWQuest']

            score = w[0]*aveWAns + w[1]*aveWQuest + w[2]*totalWAns + w[3]*totWQuest
            scoredProbes[probe] = score

        sortedProbes = sorted(scoredProbes.items(), key=operator.itemgetter(1))

        counter = 1
        for item in sortedProbes:
            if item[0] == gtquery:
                return counter
            counter += 1
        return counter


    # given a gtquery and a list of sorted queries find the rank of the gtquery
    def gtRankInDictionary(gtquery, scoredScoredProbes):
        counter = 1
        for item in scoredScoredProbes:
            if gtquery == item[0]:
                return counter
            counter += 1

    # given partial intersections for a single query and weights(4 numbers tuple) find query score
    def queryScoreWithWeights(partialIntersections, weights):
        aveWAns = partialIntersections['aveWAns']
        aveWQuest = partialIntersections['aveWQuest']
        totalWAns = partialIntersections['totWAns']
        totWQuest = partialIntersections['totWQuest']
        return weights[0]*aveWAns + weights[1]*aveWQuest + weights[2]*totalWAns + weights[3]*totWQuest

    def gtqueryRankForWeights(partialIntersectionsList, gtquery, weights):
        scores = {}
        for pi in partialIntersectionsList:
            curQuery = pi['query']
            scores[curQuery] = scoreWithWeights(pi, w)
        sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        gtQueryRankForWeight = gtRankInDictionary(gtquery, sortedScores)



    weights = allWeights()
    ranks = []
    with open(outFilepath, 'w') as outfile:

        for line in open(inFilepath):
            question = json.loads(line)
            qtitle = question['qtitle']
            qbody = question['qbody']
            gtquery = preprocessText(question['gtquery'])
            partialIntersections = question['probes']

            ranksWeightsMap = {}
            for w in weights:
                ranksWeightsMap[w] = gtqueryRankForWeights(partialIntersections, gtquery, w)

            sortedRanks = sorted(ranksWeightsMap.items(), key=operator.itemgetter(1))
            rankWithEqualWeights = gtqueryRankForWeights(partialIntersections, gtquery, (0.25, 0.25, 0.25, 0.25))


            # logging to the output file
            outfile.write('Question :: %s %s\n' % (qtitle, qbody))
            outfile.write('Rank with all weights equal to 0.25 :: %d\n' % rankWithEqualWeights)
            outfile.write('Ranks after parameter sweep :: \n' )
            for r in sortedRanks:
                outfile.write(str(r) + '\n')
            outfile.write('\n*******\n')


            # ranks.append(w, probeRankForWeights(probeScores, w, gtquery))

        # sortedRanks = sorted(ranks.items(), key=operator.itemgetter(1))





