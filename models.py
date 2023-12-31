# models.py
import math
import time
from collections import Counter

import nltk
import numpy as np
import spacy
import random

from sentiment_data import *
from utils import *


class FeatureExtractor(object):
    """
    Feature extraction base type. Takes a sentence and returns an indexed list of features.
    """

    def get_indexer(self):
        raise Exception("Don't call me, call my subclasses")

    def extract_features(self, sentence: List[str], add_to_indexer: bool = False) -> Counter:
        """
        Extract features from a sentence represented as a list of words. Includes a flag add_to_indexer to
        :param sentence: words in the example to featurize
        :param add_to_indexer: True if we should grow the dimensionality of the featurizer if new features are encountered.
        At test time, any unseen features should be discarded, but at train time, we probably want to keep growing it.
        :return: A feature vector. We suggest using a Counter[int], which can encode a sparse feature vector (only
        a few indices have nonzero value) in essentially the same way as a map. However, you can use whatever data
        structure you prefer, since this does not interact with the framework code.
        """
        raise Exception("Don't call me, call my subclasses")


# FIXME: Part 1. PERCEPTRON
class UnigramFeatureExtractor(FeatureExtractor):
    """
    Extracts unigram bag-of-words features from a sentence. It's up to you to decide how you want to handle counts
    and any additional preprocessing you want to do.
    """

    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def get_indexer(self):
        return self.indexer

    def extract_features(self, sentence: List[str], add_to_indexer: bool = False) -> Counter:
        features = Counter()
        for word in sentence:
            word = word.lower() # lowercase
            if self.indexer.contains(word):
                # 0 or 1 feature space
                features[self.indexer.index_of(word)] = 1
            else:
                if add_to_indexer:
                    features[self.indexer.add_and_get_index(word)] = 1
        return features




class BigramFeatureExtractor(FeatureExtractor):
    """
    Bigram feature extractor analogous to the unigram one.
    """

    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def get_indexer(self):
        return self.indexer

    def extract_features(self, sentence: List[str], add_to_indexer: bool = False) -> Counter:
        features = Counter()
        for i in range(len(sentence)-1):
            bigram = sentence[i] + " " + sentence[i+1]
            bigram = bigram.lower()
            if self.indexer.contains(bigram):
                # 0 or 1 feature space
                features[self.indexer.index_of(bigram)] = 1
            else:
                if add_to_indexer:
                    features[self.indexer.add_and_get_index(bigram)] = 1
        return features




class BetterFeatureExtractor(FeatureExtractor):
    """
    Better feature extractor...try whatever you can think of!
    """

    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def get_indexer(self):
        return self.indexer

    def extract_features(self, sentence: List[str], add_to_indexer: bool = False) -> Counter:
        features = Counter()
        for i in range(len(sentence) - 2):
            trigram = sentence[i] + " " + sentence[i + 1] + " " + sentence[i+2]
            trigram = trigram.lower()
            if self.indexer.contains(trigram):
                # 0 or 1 feature space
                features[self.indexer.index_of(trigram)] = 1
            else:
                if add_to_indexer:
                    features[self.indexer.add_and_get_index(trigram)] = 1
        return features


class SentimentClassifier(object):
    """
    Sentiment classifier base type
    """

    def predict(self, sentence: List[str]) -> int:
        """
        :param sentence: words (List[str]) in the sentence to classify
        :return: Either 0 for negative class or 1 for positive class
        """
        raise Exception("Don't call me, call my subclasses")


class TrivialSentimentClassifier(SentimentClassifier):
    """
    Sentiment classifier that always predicts the positive class.
    """

    def predict(self, sentence: List[str]) -> int:
        return 1


# FIXME: Part 1. PERCEPTRON
class PerceptronClassifier(SentimentClassifier):
    """
    Implement this class -- you should at least have init() and implement the predict method from the SentimentClassifier
    superclass. Hint: you'll probably need this class to wrap both the weight vector and featurizer -- feel free to
    modify the constructor to pass these in.
    """

    def __init__(self, weight_vector, featurizer):
        self.weight_vector = weight_vector
        self.featurizer = featurizer

    def predict(self, sentence: List[str]) -> int:  #FIXME: implement this
        features = self.featurizer.extract_features(sentence)
        predicted_val = 0

        for f in features:
            predicted_val += features[f]*self.weight_vector[f]


        if predicted_val > 0:
            return 1
        else:
            return 0



class LogisticRegressionClassifier(SentimentClassifier):
    """
    Implement this class -- you should at least have init() and implement the predict method from the SentimentClassifier
    superclass. Hint: you'll probably need this class to wrap both the weight vector and featurizer -- feel free to
    modify the constructor to pass these in.
    """

    def __init__(self, weight_vector, featurizer):
        self.weight_vector = weight_vector
        self.featurizer = featurizer

    def predict(self, sentence: List[str]) -> int:
        P_1_X = self.p_1_x(sentence)

        if P_1_X > 0.5:
            return 1
        else:
            return 0

    def p_1_x(self, sentence):
        features = self.featurizer.extract_features(sentence)
        p_1_x = 0
        for f in features:
            p_1_x += features[f]*self.weight_vector[f] #w_t_fx
        p_1_x = math.exp(p_1_x) / (1+math.exp(p_1_x))
        return p_1_x

    def p_1_neg_x(self, sentence):
        features = self.featurizer.extract_features(sentence)
        P_1_NEG_X = 0
        for f in features:
            P_1_NEG_X += features[f]*self.weight_vector[f] #w_t_fx

        P_1_NEG_X = 1/(1+math.exp(P_1_NEG_X))
        return P_1_NEG_X





# FIXME: Part 1. PERCEPTRON
def train_perceptron(train_exs: List[SentimentExample], feat_extractor: FeatureExtractor) -> PerceptronClassifier:
    """
    Train a classifier with the perceptron.
    :param train_exs: training set, List of SentimentExample objects
    :param feat_extractor: feature extractor to use
    :return: trained PerceptronClassifier model
    """
    random.seed(10)
    alpha = 0.05 #FIXME: arbitrary choice
    epochs = 50 #FIXME: arbitrary choice
    weight_vector = [0 for i in range(len(feat_extractor.get_indexer()))]

    perceptron_classifier = PerceptronClassifier(weight_vector, feat_extractor)
    for e in range(epochs):
        random.shuffle(train_exs)
        for train_ex in train_exs:
            if train_ex.label == perceptron_classifier.predict(train_ex.words):
                continue
            else:
                features = feat_extractor.extract_features(train_ex.words, True) # cuz we are 'training'
                for i in range(len(feat_extractor.get_indexer()) - len(perceptron_classifier.weight_vector)):
                    perceptron_classifier.weight_vector.append(0)
                perceptron_classifier.weight_vector.append(0)
                if train_ex.label == 1:
                    for word_idx in features:
                        perceptron_classifier.weight_vector[word_idx] += alpha * features[word_idx]
                elif train_ex.label == 0:
                    for word_idx in features:
                        perceptron_classifier.weight_vector[word_idx] -= alpha * features[word_idx]
                else:
                    print("This should not happen")
    return perceptron_classifier



def train_logistic_regression(train_exs: List[SentimentExample],
                              feat_extractor: FeatureExtractor) -> LogisticRegressionClassifier:
    """
    Train a logistic regression model.
    :param train_exs: training set, List of SentimentExample objects
    :param feat_extractor: feature extractor to use
    :return: trained LogisticRegressionClassifier model
    """
    random.seed(2324) #FIXME: return here
    alpha = 0.1
    epochs = 15
    weight_vector = [0 for i in range(len(feat_extractor.get_indexer()))]

    lr_classifier = LogisticRegressionClassifier(weight_vector, feat_extractor)
    for e in range(epochs):
        random.shuffle(train_exs)
        for train_ex in train_exs:
            features = feat_extractor.extract_features(train_ex.words, True)  # cuz we are 'training'
            for i in range(len(feat_extractor.get_indexer()) - len(lr_classifier.weight_vector)):
                lr_classifier.weight_vector.append(0)

            lr_classifier.weight_vector.append(0)
            if train_ex.label == 1:
                if lr_classifier.predict(train_ex.words) == 1:
                    continue
                for f in features:
                    weight_vector[f] += alpha*(1-lr_classifier.p_1_x(train_ex.words))
            else:
                if lr_classifier.predict(train_ex.words) == 0:
                    continue
                for f in features:
                    weight_vector[f] -= alpha*(1-lr_classifier.p_1_neg_x(train_ex.words))
    return lr_classifier



def train_model(args, train_exs: List[SentimentExample], dev_exs: List[SentimentExample]) -> SentimentClassifier:
    """
    Main entry point for your modifications. Trains and returns one of several models depending on the args
    passed in from the main method. You may modify this function, but probably will not need to.
    :param args: args bundle from sentiment_classifier.py
    :param train_exs: training set, List of SentimentExample objects
    :param dev_exs: dev set, List of SentimentExample objects. You can use this for validation throughout the training
    process, but you should *not* directly train on this data.
    :return: trained SentimentClassifier model, of whichever type is specified
    """
    # Initialize feature extractor
    if args.model == "TRIVIAL":
        feat_extractor = None
    elif args.feats == "UNIGRAM":
        # Add additional preprocessing code here
        feat_extractor = UnigramFeatureExtractor(Indexer())
    elif args.feats == "BIGRAM":
        # Add additional preprocessing code here
        feat_extractor = BigramFeatureExtractor(Indexer())
    elif args.feats == "BETTER":
        # Add additional preprocessing code here
        feat_extractor = BetterFeatureExtractor(Indexer())
    else:
        raise Exception("Pass in UNIGRAM, BIGRAM, or BETTER to run the appropriate system")

    # Train the model
    if args.model == "TRIVIAL":
        model = TrivialSentimentClassifier()
    elif args.model == "PERCEPTRON":
        model = train_perceptron(train_exs, feat_extractor)
    elif args.model == "LR":
        model = train_logistic_regression(train_exs, feat_extractor)
    else:
        raise Exception("Pass in TRIVIAL, PERCEPTRON, or LR to run the appropriate system")
    return model
