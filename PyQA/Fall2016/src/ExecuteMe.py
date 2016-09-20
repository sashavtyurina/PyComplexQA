"""Executable code needed for different purposes."""

from SQLWizard import SQLWizard
from TextWizard import TextWizard
from KLDWizard import KLDWizard
from Utils import Utils
from QueryWizard import QueryWizard
import json
import subprocess

dbPath = '../data/Snippets.db'
jsonFile = '../data/SelectedQuestions.txt'
wordFrequenciesFilename = '../data/WordFrequencies.txt'


def selectDistinctWordsFromJSON(fromFilename, toFilename):
    """Select all distinct words from questions and answers."""
    with open(toFilename, 'w') as fOut:
        for line in open(fromFilename):
            q = json.loads(line.strip())
            rawQuestion = q['qtitle'] + ' ' + q['qbody']
            answer = ' '.join(q['answers'])

            qTokens = set(TextWizard.preprocessText(rawQuestion).split())
            aTokens = set(TextWizard.preprocessText(answer).split())
            allTokens = set.union(qTokens, aTokens)
            for token in allTokens:
                fOut.write('%s\n' % token)

    # delete repeating words from the file
    sortPipe = subprocess.Popen(['sort', toFilename], stdout=subprocess.PIPE,)
    tempFilename = 'temp.txt'
    with open(tempFilename, 'w') as fOut:
        subprocess.Popen(['uniq'], stdin=sortPipe.stdout, stdout=fOut,)

    subprocess.call(['mv', tempFilename, toFilename])




def main():
    kldWiz = KLDWizard(wordFrequenciesFilename)
    sqlWiz = SQLWizard(dbPath)
    questions = sqlWiz.getQuestions()

    for q in questions:
        qtext = q.qtitleOriginal + ' ' + q.qbodyOriginal
        print(qtext)

        answers = sqlWiz.getAnswersForQID(q.qid)

        for a in answers:
            anwerTokens = TextWizard.preprocessText(a.answerText).split()
            topTokens = Utils.extractFromTupleList(kldWiz.topNWordsFromTokens(anwerTokens, -1), 0)

            print(a.answerText)
            print(topTokens)
            print('\n***\n')
            input()



        # Select keywords and compose queries
        # tokens = TextWizard.preprocessText(q.qtitle + ' ' + q.qbody)
        # topTokens = kldWiz.topNWordsFromTokens(tokens.split(), 20)
        # topTokens = Utils.extractFromTupleList(topTokens, 0)
        # print('Unsorted :: ' + str(topTokens))
        # topTokens = QueryWizard.sortTokens(tokens, topTokens)
        # print('Initial :: ' + str(tokens))
        # print('Sorted :: ' + str(topTokens))
        # queries = QueryWizard.generateQueries(topTokens, 3)
        # print(len(queries))
        # print(queries)
        # print('\n***\n')
        # input()

    # 2. selecting all different words from questions and answers
    # selectDistinctWordsFromJSON('../data/SelectedQuestions.txt', '../data/DistinctWords.txt')

    # 1. initially insert questions and their answers into the db
    # sqlWiz = SQLWizard(dbPath)
    # sqlWiz.initialImportFromJSON(jsonFile)

if __name__ == '__main__':
    main()
