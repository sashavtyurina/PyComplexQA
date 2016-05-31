import json
import re
import itertools
import sqlite3
from SQLWizard import SQLWizard
from KLDWizard import KLDWizard
from Utils import *
from Keywords import *


def main():
    M = 3
    equalWeights = (0.25, 0.25, 0.25, 0.25)
    avgRecallAtM = []

    for line in open('intersectionsChar3Grams.txt'):
        question = json.loads(line)
        qtitle = question['qtitle']
        qbody = question['qbody']
        gtqueryTokens = preprocessText(question['gtquery']).split(' ')
        print(' '.join([qtitle, qbody]))
        # gtquery = Utils.preprocessText(question['gtquery'])
        partialIntersections = question['probes']
        scoredProbes = scoreQueriesWithWeight(partialIntersections, equalWeights)[:M]
        topProbeWords = list(itertools.chain(*[p[0].split(' ') for p in scoredProbes[:M]]))
        topWords = []
        for w in topProbeWords:
            if w not in topWords:
                topWords.append(w)
        topWords = topWords[:M]
        print('top words :: ' + str(topWords))
        print('gt query :: ' + str(gtqueryTokens))

        recallAtM = len(set(topWords).intersection(gtqueryTokens)) / len(gtqueryTokens)
        print(recallAtM)
        avgRecallAtM.append(recallAtM)

        for s in scoredProbes:
            print(s)
        print('\n****\n')
    print(sum(avgRecallAtM) / len(avgRecallAtM))

    # characterNGramSimilarity('intersectionsCharNGrams.txt', 3)
    # print('done')
    # input()


    # print('M = 10')
    # precisionAtM('intersectionsChar3Grams.txt', 10)
    # print('done')
    # input()


    # parameterSweep('intersections.txt', 'paramSweep.txt')
    # print('done')
    # input()



if __name__ == "__main__":
    main()
