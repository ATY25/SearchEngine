import re
import math
from collections import defaultdict


def tokenize(text):
    return re.findall(r"[a-zA-Z]{2,}", text.lower())


class InvertedIndex:
    def __init__(self):
        self.docs = []
        self.index = defaultdict(dict)

    def build(self, docs):
        self.docs = docs
        self.index.clear()

        for doc_id, doc in enumerate(docs):
            tokens = tokenize(doc["title"])

            for token in tokens:
                self.index[token][doc_id] = self.index[token].get(doc_id, 0) + 1

    def search(self, query):
        tokens = tokenize(query)
        scores = defaultdict(float)
        N = len(self.docs)

        for token in tokens:
            if token not in self.index:
                continue
            postings = self.index[token]
            df = len(postings)
            idf = math.log((N + 1) / (df + 1))

            for doc_id, tf in postings.items():
                scores[doc_id] += tf * idf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.docs[i], score) for i, score in ranked]
