"""Train doc2vec."""


from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
# from gensim import doc2vec
# from doc2vec import TaggedDocument, TaggedLineDocument, Doc2Vec
import json
from TextWizard import TextWizard


def get_questions(filename):
    with open(filename) as f_in:
        for item_no, line in enumerate(f_in):
            json_object = json.loads(line.strip().lower())
            question = json_object['qtitle'] + json_object['qbody']

            yield TaggedDocument(TextWizard.preprocessText(question).split(), [item_no])


for q in get_questions('../data/SelectedQuestions.txt'):
    print(q)

question_model = Doc2Vec(get_questions('../data/SelectedQuestions.txt'), size=5, min_count=3)
sim = question_model.docvecs.most_similar(0)
print(sim)
