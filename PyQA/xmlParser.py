"""A."""
import Utils
from xml.etree.cElementTree import iterparse
import json
qtitle = ''
qbody = ''
qlang = ''
bestanswer = ''
answers = []
# lengths = [
with open('smallSampleText.txt', 'w') as out:
    source = 'small_sample.xml'
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
            jsonQ = json.dumps({'qtitle': qtitle, 'qbody': qbody, 'bestanswer': bestanswer, 'answers': answers})
            out.write('%s\n' % str(jsonQ))
            # lengths.append(len(Utils.preprocessText(qtitle + ' ' + qbody).split(' ')))
            qtitle = ''
            qbody = ''
            bestanswer = ''
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
