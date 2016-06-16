"""I will try and see what results ROUGE gives.

Package pyrouge is coming from https://github.com/bheinzerling/pyrouge.
This seems to be working.
The output provided contains all possible ROUGE scores, averaged between all system summaries.
"""

from pyrouge import Rouge155

r = Rouge155()
r.system_dir = '/Users/Alex/Documents/UWaterloo/PyComplexQA/ROUGE/systemSummaries'
r.model_dir = '/Users/Alex/Documents/UWaterloo/PyComplexQA/ROUGE/goldenSummaries'
r.system_filename_pattern = 'system.(\d+).txt'
r.model_filename_pattern = 'golden.[A-Z].#ID#.txt'

output = r.convert_and_evaluate()
print(output)
output_dict = r.output_to_dict(output)
# print('\n------------------------\n')

# for item in output_dict.items():
    # print(str(item[0]) + ' :: ' + `str(item[1]))
# print(output_dict)
