# helper class with containters for questions, answers, snippets
# after they have been fetched from a db
import re

class QuestionSQL:
    def __init__(self, qid, qtitle, qbody, gtquery, yahooqid):
        self.qid = qid
        self.qtitle = qtitle.lower()
        self.qbody = qbody.lower()
        if gtquery:
            self.gtquery = gtquery.lower()
        else:
            self.gtquery = None

        if yahooqid:
            self.yahooqid = yahooqid.lower()
        else:
            self.yahooqid = None

class AnswerSQL:
    def __init__(self, aid, qid, answerText):
        if aid:
            self.aid = aid
        self.qid = qid
        self.answerText = re.sub('\n', ' ', answerText.lower())

class SnippetSQL:
    def __init__(self, queryText, docURL, snippet):
        self.queryText = queryText.lower()
        self.docURL = docURL.lower()
        self.snippet = snippet.lower()
