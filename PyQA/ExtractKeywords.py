import json
import re
import itertools
import sqlite3
from SQLWizard import SQLWizard
from KLDWizard import KLDWizard
from Utils import *
from Keywords import *


def main():

    equalWeights = (0.25, 0.25, 0.25, 0.25)
    for line in open('intersectionsChar3Grams.txt'):
        question = json.loads(line)
        qtitle = question['qtitle']
        qbody = question['qbody']
        print(' '.join([qtitle, qbody]))
        # gtquery = Utils.preprocessText(question['gtquery'])
        partialIntersections = question['probes']
        scoredProbes = scoreQueriesWithWeight(partialIntersections, equalWeights)
        for s in scoredProbes:
            print(s)
        print('\n****\n')

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
