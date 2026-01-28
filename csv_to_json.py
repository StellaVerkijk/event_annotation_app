import pandas as pd
import json

def split_at_newlines(lst):
    '''
    Written by Claude
    '''
    result = []
    current_group = []
    
    for item in lst:
        if item == "\\n":
            if current_group:  # Only add non-empty groups
                result.append(current_group)
                current_group = []
        else:
            current_group.append(item)
    
    # Don't forget the last group
    if current_group:
        result.append(current_group)
    
    return result

def tojson(sentences, sentence_annotations, outfile):
    with open(outfile, 'w') as f:
        for i in range(0, len(sentences)):
            tokens, labels = sentences[i], sentence_annotations[i]
            json.dump({'words': tokens, 'events': labels}, f)
            f.write("\n")

def check_length_of_longest():
    longest = max(sentences, key=len)
    print(len(longest))

INFILE = '1812.csv'
OUTFILE = '1812.json'

df = pd.read_csv(INFILE, index_col=0, encoding='utf-8')

sentences = split_at_newlines(df['word'].tolist())
sentence_annotations = split_at_newlines(df['manual_resolve'].tolist())

print(len(sentences))
print(len(sentence_annotations))

tojson(sentences, sentence_annotations, OUTFILE)





