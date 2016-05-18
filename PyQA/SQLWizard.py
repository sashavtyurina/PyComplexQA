import sqlite3
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

    # get all distinct snippets for a give query
    def getSnippetForQuery(self, queryText):
        connection = sqlite3.connect(self.dbPath)
        sql = 'select distinct snippet, sid, qid, queryText, docURL from snippets where querytext="' + queryText + '";'
        cursor = connection.execute(sql)
        snippets = []
        for row in cursor:
            snippet = row[0]
            sid = row[1]
            qid = row[2]
            queryText = row[3]
            docURL = row[4]
            snippet = SnippetSQL(sid, qid, queryText, docURL, snippet)
            snippets.append(snippet)
        connection.close()
        return snippets


