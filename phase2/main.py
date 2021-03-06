import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from phase2.preproccessor import PreProcessEnglish
from phase2.positional_index import PositionalIndex
from phase2.tf_idf_ntn import vector_tnt
from phase2.classifiers import SoftMarginSVMClassifier, RFClassifier, NaiveBayesClassifier, KNNClassifier
from phase1.tf_idf import TfIdfSearch


class Classifier:
    def __init__(self, preprocessor):
        self.processor = preprocessor
        self.irs_pi = None
        self.irs_doc_ids = None
        self.irs_docs = None

    def read_ted_talk(self):
        file_name = 'data/ted_talks.csv'
        doc = pd.read_csv(file_name)
        ted_docs = self.processor.clean_documents(doc['description'], with_stop_words=True)
        ted_titles = self.processor.clean_documents(doc['title'], with_stop_words=False)
        ted_doc_ids = list(range(len(ted_docs)))
        ted_positional_index = PositionalIndex(name=file_name, docs=ted_docs, ids=ted_doc_ids)
        ted_positional_index.construct_doc_list(ted_titles, ted_doc_ids)
        self.irs_pi = ted_positional_index
        self.irs_doc_ids = ted_doc_ids
        self.irs_docs = ted_docs
        return ted_doc_ids, ted_positional_index

    def read_data(self, file_name):
        doc = pd.read_csv(file_name)
        processed_docs = self.processor.clean_documents(doc['description'], with_stop_words=False)
        processed_titles = self.processor.clean_documents(doc['title'], with_stop_words=True)
        doc_ids = list(range(len(processed_docs)))
        y_true = np.array(doc['views'])
        positional_index = PositionalIndex(name=file_name, docs=processed_docs, ids=doc_ids)
        positional_index.construct_doc_list(processed_titles, doc_ids)
        return doc_ids, y_true, positional_index

    def process_data(self):
        ids_train, y_train, pi_train = self.read_data(file_name='data/train.csv')
        dictionary = pi_train.index.keys()
        x_train = vector_tnt(position_indexes=pi_train.index, dictionary=dictionary,document_ids=ids_train)
        ids_ted, pi_ted = self.read_ted_talk()
        ids_test, y_test, pi_test = self.read_data(file_name='data/test.csv')
        x_test = vector_tnt(position_indexes=pi_test.index, dictionary=dictionary, document_ids=ids_test)
        x_ted_dataset = vector_tnt(position_indexes=pi_ted.index, dictionary=dictionary, document_ids=ids_ted)
        return np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test), np.array(x_ted_dataset),

    def retrieve_tfidf_answer(self, query, no_wanted_outcomes, X, classifier, class_number):
        print('your query: {}'.format(query))
        clean_query = self.processor.clean_query(query=query)

        handler = TfIdfSearch(self.irs_doc_ids, self.irs_pi.index)
        answers_list = handler.answers(query=clean_query, no_wanted_outcomes=int(2.5*no_wanted_outcomes))
        print('tf-idf with classifying:')
        Y = classifier.predict(X)
        count = 0
        for i, (score, doc_id) in enumerate(answers_list):
            if Y[i] == class_number:
                count += 1
                text = self.irs_docs[doc_id]
                print('{}-answer:{} \n score:{}'.format(count, " ".join(text), score))
            if count >= no_wanted_outcomes:
                break

    def search_test(self, prox =False, search_title= False):

        n = len(self.irs_doc_ids)
        k = 10
        p_idx = self.irs_pi.index if search_title else self.irs_pi.index
        # docs = self.title_processed_docs if search_title else ir.processed_docs

        # input query and window size
        query = input(" Enter a correct query: \n")
        if prox:
            w = int(input(" enter proximity window size: \n"))

        processed_query = self.processor.process_data([query], find_stopwords=False)[0]
        print("Initial query: ", query)
        print("Processed query: ", processed_query)
        #
        # retrieve docs
        if prox:
            #TODO  this should be a proximate search with weights
            retrieved = TfIdfSearch.answers(self.irs_doc_ids, self.irs_pi.index)
            print(f'Top {len(retrieved)} doc using proximity search - window size = {w}:')
        else:
            retrieved =  TfIdfSearch.answers(self.irs_doc_ids, self.irs_pi.index)
            print(f'Top {len(retrieved)} doc using tf-idf search:')


        # for i, (doc_id, score) in enumerate(retrieved):
        #     print(f'{i + 1:2d}. ID: {doc_id:5d}, Score: {score:.5f}')
        #     print(docs[ir.doc_ids.index(doc_id)])

    # بخش سوم فاز دوم
    def final_evaluation(self, classifier_name, y_true, y_pred):
        conf_matrix = confusion_matrix(y_true=y_true, y_pred=y_pred)
        tn, fp, fn, tp = conf_matrix.ravel()
        print('counts: tn:{}, fp:{}, fn:{}, tp:{}'.format(tn, fp, fn, tp))
        accuracy = self.accuracy(tn, fp, fn, tp)
        precision_1, precision_2 = self.precision(tn, fp, fn, tp)
        recall_1, recall_2 = self.recall(tn, fp, fn, tp)
        class_1_f1, class_2_f1 = self.f1(precision_1, recall_1, precision_2, recall_2)
        print('Evaluation of {}'.format(classifier_name))
        print('Accuracy is:{}'.format(round(accuracy, 4)))
        print('\n******************************\n')
        print('F1 with beta=1 & alpha=2: ')
        print('first class F1: {}'.format(round(class_1_f1, 4)))
        print('Second class F1: {}'.format(round(class_2_f1, 4)))
        print('\n******************************\n')
        print('Precision:{}, Recall:{}, first class'.format(round(precision_1, 4), round(recall_1, 4)))
        print('Precision:{}, Recall:{} second class'.format(round(precision_2, 4), round(recall_2, 4)))
        print('\n******************************\n')

    @staticmethod
    def accuracy(true_negative, false_positive, false_negative, true_positive):
        accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_negative + false_positive)
        return accuracy

    @staticmethod
    def precision(true_negative, false_positive, false_negative, true_positive):
        class_1_precision = true_positive / (true_positive + false_positive)
        class_2_precision = true_negative / (true_negative + false_negative)
        return class_1_precision, class_2_precision

    @staticmethod
    def recall(true_negative, false_positive, false_negative, true_positive):
        class_1_recall = true_positive / (true_positive + false_negative)
        class_2_recall = true_negative / (true_negative + false_positive)
        return class_1_recall, class_2_recall

    @staticmethod
    def f1(precision_1, recall_1, precision_2, recall_2):
        class_1_f1 = 2 * (precision_1 * recall_1) / (precision_1 + recall_1)
        class_2_f1 = 2 * (precision_2 * recall_2) / (precision_2 + recall_2)
        return class_1_f1, class_2_f1


if __name__ == '__main__':
    # در اینجا به تست و ترین تقسیم می‌کنیم
    classify = Classifier(preprocessor=PreProcessEnglish())
    X_train_validation, Y_train_validation, X_test, Y_test, X_ted = classify.process_data()

    # اینجا خود داده ترین را به ولیدیشن و ترین تقسیم کرده
    X_train, X_validation, Y_train, Y_validation = train_test_split(
        X_train_validation, Y_train_validation, test_size=0.1, random_state=42
    )
    # SVM
    # در اینجا بهترین مقدار C را برای soft-margin-svm پیدا می‌کنیم
    c_values = [0.5, 1, 1.5, 2]
    best_C = 0
    best_validation_acc = 0
    best_C_Y_pred_test = None
    best_C_Y_pred_train = None
    for C in c_values:
        svm = SoftMarginSVMClassifier(x_train=X_train, y_train=Y_train, C=C)
        svm.fit()
        y_pred_val = svm.predict(X_validation)
        y_pred_test = svm.predict(X_test)
        Y_pred_train = svm.predict(X_train)
        validation_acc = (y_pred_val == Y_validation).mean()
        if validation_acc > best_validation_acc:
            best_validation_acc = validation_acc
            best_C = C
            best_C_Y_pred_test = y_pred_test
            best_C_Y_pred_train = Y_pred_train
        print('svm C:{} validation acc: {}'.format(C, validation_acc))

    classify.final_evaluation('Soft margin SVM On Training', Y_train, best_C_Y_pred_train)
    classify.final_evaluation('Soft margin SVM On Test', Y_test, best_C_Y_pred_test)
    classify.retrieve_tfidf_answer(
        query='how are you my friend?',
        no_wanted_outcomes=10,
        X=X_ted, classifier=svm,
        class_number=1
    )

    # Random Forest
    random_forest = RFClassifier(x_train=X_train_validation, y_train=Y_train_validation)
    random_forest.fit()
    rf_y_pred_train = random_forest.predict(X_train_validation)
    classify.final_evaluation("Random Forest On Training", Y_train_validation, rf_y_pred_train)
    rf_y_pred_test = random_forest.predict(X_test)
    classify.final_evaluation("Random Forest on Test", Y_test, rf_y_pred_test)

    # Naive Bayes
    naive_bayes = NaiveBayesClassifier(X_train_validation, Y_train_validation)
    naive_bayes.fit()
    nb_y_pred_train = naive_bayes.predict(X_train_validation)
    classify.final_evaluation("Naive Bayes On Training", Y_train_validation, nb_y_pred_train)
    nb_y_pred_test = naive_bayes.predict(X_test)
    classify.final_evaluation("Naive Bayes On Test", Y_test, nb_y_pred_test)

    # KNN
    K_VALUES = [1, 5, 9]
    best_K = 0
    best_knn_validation_acc = 0
    best_K_Y_pred_test = None
    best_K_Y_pred_train = None

    for k in K_VALUES:
        knn = KNNClassifier(k=k,x_train=X_train, y_train=Y_train)
        knn.fit()
        knn_y_pred_val = knn.predict(X_validation)
        knn_validation_acc = (knn_y_pred_val == Y_validation).mean()
        knn_y_pred_test = knn.predict(X_test)
        knn_y_pred_train = knn.predict(X_train)
        if knn_validation_acc > best_knn_validation_acc:
            best_K = k
            best_K_Y_pred_test = knn_y_pred_test
            best_K_Y_pred_train = knn_y_pred_train
        print('k-nn K:{} validation acc: {}'.format(k, knn_validation_acc))

    classify.final_evaluation("{}NN On Validation".format(best_K), Y_train_validation, best_K_Y_pred_train)
    classify.final_evaluation("{}NN On Test".format(best_K), Y_test, best_K_Y_pred_test)
