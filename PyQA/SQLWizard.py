import sqlite3
import json
from QAS import *

class SQLWizard:
    def __init__(self, dbPath):
        self.dbPath = dbPath

    # retrieves all the questions from the DB
    def getQuestions(self):
        connection = sqlite3.connect(self.dbPath)
        sql = 'select qid, qtitle, qbody, gtquery, yahooqid from questions;'
        cursor = connection.execute(sql)
        questions = []
        for row in cursor:
            qid = row[0]
            qtitle = row[1]
            qbody = row[2]
            gtquery = row[3]
            yahooqid = row[4]
            q = QuestionSQL(qid, qtitle, qbody, gtquery, yahooqid)
            questions.append(q)
        connection.close()
        return questions


# fetches all answers for a given question id
    def getAnswersForQID(self, qid):
        connection = sqlite3.connect(self.dbPath)
        # sql = 'select aid, qid, answerText from answers where qid=' + str(qid) + ';'
        sql = 'select qid, answerText from answers where qid=' + str(qid) + ';'
        cursor = connection.execute(sql)
        answers = []
        for row in cursor:
            # aid = row[0]
            aid = None
            qid = row[0]
            answerText = row[1]
            answer = AnswerSQL(aid, qid, answerText)
            answers.append(answer)
        connection.close()
        return answers


    def getBestAnswerForQID(self, qid):
        connection = sqlite3.connect(self.dbPath)
        # sql = 'select aid, qid, answerText from answers where qid=' + str(qid) + ';'
        sql = 'select qid, answerText from answers where qid=' + str(qid) + ' and best=1;'
        cursor = connection.execute(sql)
        bestAnswer = None
        for row in cursor:
            # aid = row[0]
            aid = None
            qid = row[0]
            answerText = row[1]
            bestAnswer = AnswerSQL(aid, qid, answerText)
        connection.close()
        return bestAnswer

    # get all distinct snippets for a give query
    def getNSnippetsForQuery(self, queryText, N):
        connection = sqlite3.connect(self.dbPath)
        if N == -1:
            sql = 'select distinct snippet, queryText, docURL from snippets where querytext="' + queryText.strip() + '";'
        else:
            sql = 'select distinct snippet, queryText, docURL from snippets where querytext="' + queryText + '" limit ' + str(N) + ';'
        cursor = connection.execute(sql)
        snippets = []
        for row in cursor:
            snippet = row[0]
            queryText = row[1]
            docURL = row[2]
            snippet = SnippetSQL(queryText, docURL, snippet)
            snippets.append(snippet)
        if (N != -1) and (len(snippets) < N):
            print('Not enough snippets for :: ' + queryText + '. Wanted ' + str(N) + " fetched " + str(len(snippets)))

        connection.close()
        return snippets

    # exports all questions from the DB to a JSON file
    def exportQuestionsToJSON(self, filename):
        with open(filename, 'w') as f:
            questions = self.getQuestions()
            for q in questions:
                jsonObj = json.dumps({'qid': q.qid, 'qtitle': q.qtitle, 'qbody': q.qbody,
                                      'gtquery': q.gtquery, 'yahooqid': q.yahooqid})
                f.write('%s\n' % str(jsonObj))

    def importQuestionsFromJSON(self, filename):
        sql = 'insert into questions (qid, qtitle, qbody, gtquery, yahooqid) values (?, ?, ?, ?, ?)'
        connection = sqlite3.connect(self.dbPath)
        for line in open(filename):
            q = json.loads(line.strip())
            connection.execute(sql, (q['qid'], q['qtitle'], q['qbody'], q['gtquery'], q['yahooqid']))

        connection.commit()
        connection.close()


