# helper class with containters for questions, answers, snippets
# after they have been fetched from a db

class QuestionSQL:
    def __init__(self, qid, qtitle, qbody, gtquery, yahooqid):
        self.qid = qid
        self.qtitle = qtitle
        self.qbody = qbody
        self.gtquery = gtquery
        self.yahooqid = yahooqid

class AnswerSQL:
    def __init__(self, aid, qid, answerText):
        self.aid = aid
        self.qid = qid
        self.answerText = answerText

class SnippetSQL:
    def __init__(self, sid, qid, queryText, docURL, snippet):
        self.sid = sid
        self.qid = qid
        self.queryText = queryText
        self.docURL = docURL
        self.snippet = snippet
