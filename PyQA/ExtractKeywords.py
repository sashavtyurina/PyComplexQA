import json
import re
import itertools
import sqlite3
from SQLWizard import SQLWizard
from KLDWizard import KLDWizard
from Utils import *
from Keywords import *


def main():
    # Utils.importSnippetsFromText('NoBadAnswers/MissingQueriesSearchResult.txt')
    # extractMissingQueries()
    # sqlWiz = SQLWizard('Snippets.db')
    # questions = sqlWiz.getQuestions()
    # for q in questions:
    #     words = keywordsNFromText(' '.join([q.qtitle, q.qbody]), -1)
    #     print('\n'.join([w[0] + ' ' + str(w[1]) for w in words]))
    #     print('\n**********\n')

    # calcIntersections()
    # characterNGramSimilarity('char3GramsGoogAnsOnly.txt', 3)
    # # findMisspelledWords('misspelled.txt')
    # print('done')
    # input()


    # M = 7
    # precisionAtM('char3GramsGoogAnsOnly.txt', M)
    # input()

    equalWeights = (0.25, 0.25, 0.25, 0.25)
    avgRecallAtM = []

    output = open('NoBadAnswers/intersectionsWordsFixedTyposBigramsBeg.html', 'w')

    for line in open('NoBadAnswers/intersectionsWordsFixedTyposBigramsBeg.txt'):
        question = json.loads(line)
        qtitle = question['qtitle']
        qbody = question['qbody']
        gtqueryTokens = preprocessText(question['gtquery']).split(' ')
        # print(' '.join([qtitle, qbody]))
        output.write('%s<br/>\n' % ' '.join([qtitle, qbody]))
        # gtquery = Utils.preprocessText(question['gtquery'])
        partialIntersections = question['probes']
        scoredProbes = scoreQueriesWithWeight(partialIntersections, equalWeights)

        # topProbeWords = list(itertools.chain(*[p[0].split(' ') for p in scoredProbes[:M]]))
        # topWords = []
        # for w in topProbeWords:
        #     if w not in topWords:
        #         topWords.append(w)
        # topWords = topWords[:M]
        # print('top words :: ' + str(topWords))
        # print('gt query :: ' + str(gtqueryTokens))
        output.write('gt query :: %s<br/>\n' % str(gtqueryTokens))

        # recallAtM = len(set(topWords).intersection(gtqueryTokens)) / len(gtqueryTokens)
        # print(recallAtM)
        # avgRecallAtM.append(recallAtM)

        gt = ' '.join(gtqueryTokens)
        scoredWords = rerankQueryWordsWithScores(scoredProbes)
        for s in scoredProbes[:20]:
            queryStr = s[0]
            searchRef = 'http://www.google.com/search?hl=en&q=' + queryStr
            if queryStr == gt:
                # print('->' + s[0] + ' :: ' + str(s[1]))
                output.write('-><a href=\"%s\">%s</a> :: %s <br/>\n' % (searchRef, queryStr, str(s[1])))
            else:
                output.write('<a href=\"%s\">%s</a> :: %s <br/>\n' % (searchRef, queryStr, str(s[1])))

        output.write('<br/>\n<b>%s</b><br/>\n' % 'Reranked words:')
        for w in scoredWords:
            output.write('%s -- %f<br/>\n' % (w[0], w[1]))

        kldSoredWords = keywordsNFromText(' '.join([qtitle, qtitle, qbody]), 10)
        output.write('<br/>\n<b>%s</b><br/>\n' % 'Ranked by KLD words:')
        for w in kldSoredWords:
            output.write('%s -- %f<br/>\n' % (w[0], w[1]))


        # print('\n****\n')
        output.write('%s<br/>\n' % '\n****\n')
    # print(sum(avgRecallAtM) / len(avgRecallAtM))




    # print('M = 10')
    # precisionAtM('intersectionsChar3Grams.txt', 10)
    # print('done')
    # input()


    # parameterSweep('intersections.txt', 'paramSweep.txt')
    # print('done')
    # input()



if __name__ == "__main__":
    main()
