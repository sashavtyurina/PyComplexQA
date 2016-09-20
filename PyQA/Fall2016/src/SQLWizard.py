"""This class is responsible for communicating with the database."""


import sqlite3
import json
from QAS import QuestionSQL, AnswerSQL, SnippetSQL


class SQLWizard:
    """This class is responsible for communicating with the database."""

    def __init__(self, dbPath):
        """Initialize new class instance with a database path."""
        self.dbPath = dbPath


    def getQuestions(self):
        """
        Retrieve all the questions from the DB. Return a list of question objects declared in QAS file.

        Pay attention at the sql string. If DB schema changes, this will raise an exception.
        """
        connection = sqlite3.connect(self.dbPath)
        sql = 'select qid, qtitle, qbody, gtquery, yahooqid, bestanswer from questions;'
        cursor = connection.execute(sql)
        questions = []
        for row in cursor:
            qid = row[0]
            qtitle = row[1]
            qbody = row[2]
            gtquery = row[3]
            yahooqid = row[4]
            bestanswer = row[5]
            q = QuestionSQL(qid, qtitle, qbody, gtquery, yahooqid, bestanswer)
            questions.append(q)
        connection.close()
        return questions


    def getAnswersForQID(self, qid):
        """Fetch all answers for a given question id."""
        connection = sqlite3.connect(self.dbPath)
        sql = 'select aid, qid, answerText from answers where qid=' + str(qid) + ';'
        cursor = connection.execute(sql)
        answers = []
        for row in cursor:
            aid = row[0]
            qid = row[1]
            answerText = row[2]
            answer = AnswerSQL(aid, qid, answerText)
            answers.append(answer)
        connection.close()
        return answers


    def getBestAnswerForQID(self, qid):
        """Return selected best answer for a given question."""
        connection = sqlite3.connect(self.dbPath)

        sql = 'select bestanswer questions where qid=' + str(qid) + ';'
        cursor = connection.execute(sql)
        row = cursor.fetchone()
        answerText = row[0]

        sql = 'select aid from answers where qid=' + qid + ' and answerText="' + answerText + '";'
        cursor = connection.execute(sql)
        row = cursor.fetchone()
        aid = row[0]

        bestAnswer = AnswerSQL(aid, qid, answerText)
        connection.close()

        return bestAnswer

    def initialImportFromJSON(self, filename):
        """Import questions and answers from a JSON file to SQLite database."""
        connection = sqlite3.connect(self.dbPath)
        cursor = connection.cursor()

        for line in open(filename):
            q = json.loads(line.strip())
            qtitle = q['qtitle']
            qbody = q['qbody']
            bestanswer = q['bestanswer']
            answers = q['answers']

            # insert into questions
            sql = 'insert into questions (qtitle, qbody, bestanswer) values (?, ?, ?)'
            cursor.execute(sql, (qtitle, qbody, bestanswer))

            insertedQid = cursor.lastrowid

            for answer in answers:
                # insert into answers.
                sql = 'insert into answers (qid, answertext) values (?, ?)'
                cursor.execute(sql, (insertedQid, answer))

        connection.commit()
        connection.close()


##########
# REVIEW #
##########
    def getNSnippetsForQuery(self, queryText, N):
        """Get N distinct snippets for a given query."""
        connection = sqlite3.connect(self.dbPath)
        if N == -1:
            sql = 'select distinct snippet, queryText, docURL from snippets where querytext="' + \
                  queryText.strip() + '";'
        else:
            sql = 'select distinct snippet, queryText, docURL from snippets where querytext="' + \
                  queryText + '" limit ' + str(N) + ';'

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


    def exportQuestionsToJSON(self, filename):
        """Export all questions from the DB to a JSON file."""
        with open(filename, 'w') as f:
            questions = self.getQuestions()
            for q in questions:
                jsonObj = json.dumps({'qid': q.qid, 'qtitle': q.qtitle, 'qbody': q.qbody,
                                      'gtquery': q.gtquery, 'yahooqid': q.yahooqid})
                f.write('%s\n' % str(jsonObj))


    def importQuestionsFromJSON(self, filename):
        """Import questions from a JSON file to SQLite database."""
        sql = 'insert into questions (qid, qtitle, qbody, gtquery, yahooqid) values (?, ?, ?, ?, ?)'
        connection = sqlite3.connect(self.dbPath)
        for line in open(filename):
            q = json.loads(line.strip())
            connection.execute(sql, (q['qid'], q['qtitle'], q['qbody'], q['gtquery'], q['yahooqid']))

        connection.commit()
        connection.close()
