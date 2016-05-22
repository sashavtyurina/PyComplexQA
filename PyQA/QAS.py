# helper class with containters for questions, answers, snippets
# after they have been fetched from a db
import re

class QuestionSQL:
    def __init__(self, qid, qtitle, qbody, gtquery, yahooqid):
        self.qid = qid
        self.qtitle = qtitle.lower()
        self.qbody = qbody.lower()
        self.gtquery = gtquery.lower()
        self.yahooqid = yahooqid.lower()

class AnswerSQL:
    def __init__(self, aid, qid, answerText):
        self.aid = aid
        self.qid = qid
        self.answerText = re.sub('\n', ' ', answerText.lower())

class SnippetSQL:
    def __init__(self, queryText, docURL, snippet):
        self.queryText = queryText.lower()
        self.docURL = docURL.lower()
        self.snippet = snippet.lower()
