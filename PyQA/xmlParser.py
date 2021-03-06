"""
Select questions from WebScope dataset.

Read xml file with WebScope questions and their answers.
Select questions that satisfy our conditions (using goodQuestion function).
Save all selected questions to a text file in JSON format.
"""

from xml.etree.cElementTree import iterparse
import json


# this predicate function returns true if we want to consider this question
def goodQuestion(qtitle, qbody, bestanswer, answers, existingQuestions):
    if qtitle in existingQuestions:
        return False
    qtext = qtitle.strip() + qbody.strip()
    return (len(qtext) >= 150) and (len(answers) >= 3)


qtitle = ''
qbody = ''
qlang = ''
bestanswer = ''
answers = []
questionCount = 500

existingQuestions = []
for line in open('questions.txt'):
    q = json.loads(line.strip())
    existingQuestions.append(q['qtitle'])

with open('SelectedQuestions.txt', 'w') as out:
    source = 'FullOct2007.xml'
    # source = 'small_sample.xml'
    context = iterparse(source, events=("start", "end"))
    context = iter(context)
    event, root = context.__next__()
    for event, elem in context:
        if event == "end" and elem.tag == 'subject':
            qtitle = elem.text.lower()
            root.clear()
        if event == "end" and elem.tag == 'content':
            qbody = elem.text.lower()
            root.clear()
        if event == "end" and elem.tag == 'bestanswer':
            bestanswer = elem.text.lower()
            root.clear()
        if event == "end" and elem.tag == 'answer_item':
            answers.append(elem.text.lower())
            root.clear()
        if event == "end" and elem.tag == 'qlang':
            qlang = elem.text
            root.clear()
        if event == "end" and elem.tag == 'uri':
            if qtitle == '' and qbody == '':
                continue
            if qlang != 'en':
                continue
            if goodQuestion(qtitle, qbody, bestanswer, answers, existingQuestions):
                jsonQ = json.dumps({'qtitle': qtitle, 'qbody': qbody,
                                    'bestanswer': bestanswer, 'answers': answers})
                out.write('%s\n' % str(jsonQ))
                questionCount -= 1
                if questionCount == 0:
                    break

            qtitle = ''
            qbody = ''
            bestanswer = ''
            qlang = ''
            answers = []
            root.clear()


#     for event, elem in iterparse('FullOct2007.xml'):
#         if elem.tag == 'subject':
#             qtitle = elem.text.lower()
#             elem.clear()
#         if elem.tag == 'content':
#             qbody = elem.text.lower()
#             elem.clear()
#         if elem.tag == 'bestanswer':
#             bestanswer = elem.text.lower()
#             elem.clear()
#         if elem.tag == 'answer_item':
#             answers.append(elem.text.lower())
#             elem.clear()
#         if elem.tag == 'qlang':
#             qlang = elem.text
#             elem.clear()
#         if elem.tag == 'uri':
#             if qtitle == '' and qbody == '':
#                 continue
#             if qlang != 'en':
#                 continue
#             jsonQ = json.dumps({'qtitle': qtitle, 'qbody': qbody, 'bestanswer': bestanswer, 'answers': answers})
#             out.write('%s\n' % str(jsonQ))
#             # lengths.append(len(Utils.preprocessText(qtitle + ' ' + qbody).split(' ')))
#             qtitle = ''
#             qbody = ''
#             bestanswer = ''
#             answers = []
#             elem.clear()
# # print(lengths)
# # print(sum(lengths) / len(lengths))
