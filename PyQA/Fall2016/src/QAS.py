"""Helper class with containters for questions, answers, snippets after they have been fetched from a db."""
import re


class QuestionSQL:
    """Container for question, extracted from SQLite database.

    Attributes:
        qid             Autoincremented id for internal db use.
        qtitle          Question title, as provided by Yahoo! Answers. Usually is a short string.
        qbody           Question body, as provided by Yahoo! Answers. Serves as a longer description.
        gtquery         Ground truth query, created manually. Is considered to be the perfect query for the question.
        yahooqid        A short string, ex. 1006021700955, from Y!A url.
        bestAnswer      Best answer, as selected by the asker
        qtitleOtiginal  Same as qtite, only with original upper case letters for easier identification of named entities
        qbodyOriginal   Same as qbody, only with original upper case letters
    """

    def __init__(self, qid, qtitle, qbody, gtquery, yahooqid, bestanswer):
        """Constructor."""
        self.qid = qid
        self.qtitle = qtitle.lower()
        self.qbody = qbody.lower()

        self.qtitleOriginal = qtitle
        self.qbodyOriginal = qbody
        if gtquery:
            self.gtquery = gtquery.lower()
        else:
            self.gtquery = None

        if yahooqid:
            self.yahooqid = yahooqid.lower()
        else:
            self.yahooqid = None

        if bestanswer:
            self.bestanswer = bestanswer.lower()
        else:
            self.bestanswer = None


class AnswerSQL:
    """
    Container for answer, extracted from SQLite database.

    Attributes:
        aid                 autoincremented answer id, for internal use in DB.
        qid                 id of the corresponding question.
        answerText          text of the answer
        answerTextOriginal  text of the answer with original upper case letters
    """

    def __init__(self, aid, qid, answerText):
        """Constructor."""
        if aid:
            self.aid = aid
        self.qid = qid
        self.answerText = re.sub('\n', ' ', answerText.lower())
        self.answerTextOriginal = re.sub('\n', ' ', answerText)


class SnippetSQL:
    """Container for snippet, extracted from SQLite database.

    Attributes:
        sid             snippet id, for internal use in DB
        qid             id of the question, the snippet was fetched for
        queryText       text of the query that yeilded the snippet
        docURL          the url for which the snippet was fetched
        snippet         the text of the snippet
        snippetOriginal the text of the snippet with original upper case letters
    """

    def __init__(self, sid, qid, queryText, docURL, snippet):
        """Constructor."""
        self.sid = sid
        self.qid = qid
        self.queryText = queryText.lower()
        self.docURL = docURL.lower()
        self.snippet = snippet.lower()
        self.snippetOriginal = snippet
