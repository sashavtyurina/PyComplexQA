# ACCOUNT_KEY = '/Mf56CFpuSUUQKdutUsoquPduXPWJBjflVKxHC3GQAk' # sasha.vtyurina account
ACCOUNT_KEY = 'yxckQrsJG08opmtaZroAT9hMrAiD6CBgxK/NbWYFQns=' # mal.raynolds account
# ACCOUNT_KEY = '7ntaEOCRdOwFmQQg3NkTfwv/g+xfo2ZCHnxnMvpFdnQ' # ross.thedivorcer@outlook.com
# ACCOUNT_KEY = 'mTrHvU3N4LLH6yl2RvjAJpkqhRG++wf7Jl4IjU8VN6w' # monica.velula.geller@outlook.com
TOP_DOC = 10
import bing
from os import listdir
from os.path import isfile, join
import json


def ask_bing(query, filename):

    # with open('FullProbes/BingSearchResultsQuest27.txt', 'a') as f:
    with open(filename, 'a') as f:
        bing_api = bing.Api(ACCOUNT_KEY)
        json_results = bing_api.query(query, source_type='Web', top=TOP_DOC)

        for result in json_results:
            snippet = result['Title'] + ' ' + result['Description']
            url = result['Url']
            searchHit = {'queryText' : query, 'snippet' : snippet, 'url': url}
            f.write('%s\n' % json.dumps(searchHit))
            print('%s\n' % json.dumps(searchHit))

    print('Done with query :: ' + query)






# def main ():
#     mypath = '/home/avtyurin/ComplexQA/data/gtQueries/'
#     onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
#     for ff in onlyfiles:
#         with open(mypath + ff) as f:
#             counter = 0
#             for line in f:
#                 line = line.strip()
#                 if (line == ''):
#                     continue

#                 print('Working with query %d :: %s' % (counter, line))
#                 counter += 1

#                 questID = ff[ff.index('gtQuery')+len('gtQuery'):ff.index(".txt")]
#                 print(questID)
#                 newFilename = mypath + ff[0:ff.index(".txt")] + "SearchResults.txt"
#                 ask_bing(line, newFilename, questID)

def main():
    infile = 'absentQueries1.txt'
    outfile = 'absentQueries2SearchResults.txt'
    counter = 0
    with open(infile) as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            query = line
            print(query)

            print('Working with query %d :: query :: %s' % (counter, query))
            ask_bing(query, outfile)
            counter += 1



if __name__ == '__main__':
    main()

