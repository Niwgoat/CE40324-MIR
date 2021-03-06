import matplotlib.pyplot as plt
from typing import List, Dict


class PreProcess:
    def __init__(self):
        self.stop_words = []
        self.stop_words_dict = {}

    def get_stop_words(self, documents):
        if not self.stop_words:
            self.find_stopwords(documents)

    @staticmethod
    def remove_punctuation(tokens: List) -> List:
        return [word for word in tokens if word.isalpha()]

    def plot_stop_words(self):
        plt.bar(range(len(self.stop_words_dict)), list(self.stop_words_dict.values()), align='center')
        plt.xticks(range(len(self.stop_words_dict)), list(self.stop_words_dict.keys()))
        plt.show()

    def remove_stopwords(self, tokens):
        return [token for token in tokens if token not in self.stop_words]

    # remove stop_words or not
    def clean_documents(self, documents, with_stop_words=False):
        normalized_docs = self.normalize(documents=documents)
        if not with_stop_words:
            self.get_stop_words(documents)
            normalized_docs = [self.remove_stopwords(normalized_doc) for normalized_doc in normalized_docs]

        return normalized_docs

    def clean_query(self, query):
        normalized_query = self.normalization(query)
        return self.remove_stopwords(normalized_query)

    def normalize(self, documents):
        return [self.normalization(document) for document in documents]

    def normalization(self, text):
        raise NotImplementedError

    def tokenization(self, text) -> List:
        raise NotImplementedError

    def find_stopwords(self, documents: List) -> Dict[str, int]:
        raise NotImplementedError

    def stemming(self, tokens):
        raise NotImplementedError
