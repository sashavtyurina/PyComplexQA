import json
import re
import itertools
import sqlite3
from SQLWizard import SQLWizard
from KLDWizard import KLDWizard
from Utils import *
from Keywords import *

def main():
    print('M = 10')
    precisionAtM('intersections.txt', 10)

    # print('M = 5')
    # precisionAtM('intersections.txt', 5)

    print('done')
    input()

    """
    Equal weights (0.25, 0.25, 0.25, 0.25)
    M = 10
    Total questions :: 82
    Precision at M :: 0.292683 (gtquery)
    Total questions :: 82
    Recall at M :: 0.798780 (gt query tokens)

    M = 5
    Total questions :: 82
    Precision at M :: 0.109756 (gt query)
    Total questions :: 82
    Recall at M :: 0.689431 (gt query tokens)
    """

    parameterSweep('intersections.txt', 'paramSweep.txt')
    print('done')
    input()

    intersectFile = open('intersections.txt', 'w')
    sqlWiz = SQLWizard('Snippets.db')
    kldWiz = KLDWizard()
    questions = sqlWiz.getQuestions()

    for question in questions:

        # extract top words from answers
        print('Extracting top answer words...')
        answers = sqlWiz.getAnswersForQID(question.qid)
        top20AnswersWords = [item[0] for item in keywordsFromAnswers(answers, 20)]

        # extract top words from question
        print('Extracting top question words...')
        qtext = ' '.join([question.qtitle, question.qtitle, question.qbody])
        top20QuestionWords = [item[0] for item in keywordsNFromText(qtext, 20)]

        # compose queries
        print('Composing queries...')
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
            if (len(snippets) == 0):
                continue

            cleanSnippetTokens = [set(preprocessText(s.snippet).split()) for s in snippets]

            questionTopWords = set(top20QuestionWords)
            answersTopWords = set(top20AnswersWords)

            aveIntersectionWQuestion = averageSnippetIntersection(cleanSnippetTokens, questionTopWords, set(query.split(' ')))
            aveIntersectionWAnswers = averageSnippetIntersection(cleanSnippetTokens, answersTopWords, set(query.split(' ')))
            totalIntersectionWQuestion = totalSnippetIntersection(cleanSnippetTokens, questionTopWords, set(query.split(' ')))
            totalIntersectionWAnswers = totalSnippetIntersection(cleanSnippetTokens, answersTopWords, set(query.split(' ')))

            probeIntersections = {'query': query, 'aveWQuest':aveIntersectionWQuestion, 'aveWAns':aveIntersectionWAnswers, 'totWQuest':totalIntersectionWQuestion, 'totWAns':totalIntersectionWAnswers}
            allProbesIntersections.append(probeIntersections)

        questionIntersections = {'qid':question.qid, 'qtitle':question.qtitle, 'qbody':question.qbody, 'gtquery':question.gtquery, 'yahooqid':question.yahooqid, 'probes':allProbesIntersections}
        intersectFile.write('%s\n' % json.dumps(questionIntersections))
    intersectFile.close()




if __name__ == "__main__":
    main()


