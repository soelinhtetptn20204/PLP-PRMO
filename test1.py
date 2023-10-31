import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans
"""
training_data = [
    {
        'text': 'Could u give me 3 geometry problems?', 
        'entities': [(16, 17, 'QUANTITY'), (18, 26, 'TOPIC')]
    },
    {
        'text': 'Can u please recommend me 4 geo problems?', 
        'entities': [(26, 27, 'QUANTITY'), (28, 31, 'TOPIC')]
    },
    {
        'text': 'I would like to do one combi problem.', 
        'entities': [(19, 22, 'QUANTITY'), (23, 28, 'TOPIC')]
    },
    {
        'text': 'I want to try three combinatorics problems.',
        'entities': [(14, 19, 'QUANTITY'), (20, 33, 'TOPIC')]
    }
]
nlp = spacy.blank("en")
doc_bin = DocBin()
for training_example in tqdm(training_data):
     text = training_example['text']
     labels = training_example['entities']
     doc = nlp.make_doc(text)
     ents = []
     for start, end, label in labels:
         span = doc.char_span(start, end, label=label, alignment_mode="contract")
         if span is None:
             print("Skipping entity")
         else:
             ents.append(span)
     filtered_ents = filter_spans(ents)
     doc.ents = filtered_ents
     doc_bin.add(doc)

doc_bin.to_disk("train.spacy")
"""

NER = spacy.load("model-last")
raw = "hey, could u suggest me three algebra problems?"
text = NER(raw)
for word in text.ents:
    print(word.text, word.label_)
