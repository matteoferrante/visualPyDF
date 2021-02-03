from sklearn.feature_extraction.text import TfidfVectorizer
from termcolor import colored
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import pandas as pd
import numpy as np
import progressbar
from nltk.cluster.util import cosine_distance
import networkx as nx

nltk.download('punkt')

class TextResume:
    def __init__(self,text,method):
        """
        Parameters:
        ------------
        text: str to handle
        method: str to identify the algorithm to be used to generate the resume
        methods: list of available methods

        Attributes:
        ------------
        self.resume: str, resumed text

        """

        self.methods={"td_idf":self.td_idf,"abstractive":self.abstractive}

        self.text=text
        if method in self.methods.keys():
            self.method=method
        else:
            print(colored(f"[ERROR] selected method is not available, you can choose any method in {self.methods}",'red'))

        self.resume=""


    def make_resume(self,over_mean=1.2,extra_stop=None):
        """
        Parameters:
        -------------
        over_mean: float, default 1.2. Use this parameter to set how greedy the algorithm will be. Higher means to shorter resumes
                   in case of td_idf algorithm it choose the sentences which have a computed value greater than over_mean times the mean.
                   In case of abstractive algorithm it choose the best n/over_mean sentences. In any case, the greater over_mean the shorter the resume.
        extra_stop:  list of document specific words to remove

        Return:
        ---------
        resumed_text: str of most informative sentences

        """
        return self.methods[self.method](over_mean,extra_stop)


    def td_idf(self,over_mean,extra_stop=None):
        """
        Term document frequency - Inverse term frequency algorithm.

        Parameters:
        -------------
        over_mean: float, default 1.2. Use this parameter to set how greedy the algorithm will be. Higher means to shorter resumes
        extra_stop:  list of document specific words to remove

        Return:
        ---------
        resumed_text: str of most informative sentences

        """

        if extra_stop is None:
            extra_stop=[]
        print("[Generating a resume using the TD-IDF algorithm]")
        sent_tokens=sent_tokenize(self.text)
        cleaned_sent=[]
        sr=stopwords.words('english')
        sr=sr+extra_stop
        widgets = ["[INFO] Cleaning text: ", progressbar.Percentage(), " ",progressbar.Bar(), " ", progressbar.ETA()]
        pbar = progressbar.ProgressBar(maxval=len(sent_tokens),widgets=widgets).start()

        #Cleaning text
        for (i,sent) in enumerate(sent_tokens):
            cleaned=""
            words=word_tokenize(sent)

            for word in words:
                if word not in sr:
                    cleaned+=word+" "
            cleaned_sent.append(cleaned)
            pbar.update(i)
        pbar.finish()
        ### ALGORITMO TF-IDF  ###

        widgets = ["Computing term frequency and inverse document frequency: ", progressbar.Percentage(), " ",progressbar.Bar(), " ", progressbar.ETA()]
        pbar = progressbar.ProgressBar(maxval=len(sent_tokens),widgets=widgets).start()

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(cleaned_sent)
        feature_names = vectorizer.get_feature_names()
        dense = vectors.todense()
        denselist = dense.tolist()
        df = pd.DataFrame(denselist, columns=feature_names)
        s=df.sum(axis=1)
        s_mean=s.mean()
        best_sentences=[]
        for i in range(len(df)):

            if s[:][i]>s_mean*over_mean:
                best_sentences.append(sent_tokens[i])

            pbar.update(i)

        summary="\n".join(best_sentences)
        pbar.finish()
        self.resume=summary
        return summary

    def abstractive(self,over_mean,extra_stop=None):

        """
        Compute the summary using a similarity criteria.
        Parameters:
        --------------
        over_mean: float, default 1.2. Use this parameter to set how greedy the algorithm will be. Higher means to shorter resumes


        extra_stop:  list of document specific words to remove

        Return:
        --------------
        resume: str, summarized text.

        """


        if extra_stop is None:
            extra_stop=[]
        print("[Generating a resume using the abstractive similarity algorithm]")
        sentences=sent_tokenize(self.text)
        stop_words=stopwords.words('english')
        stop_words+=extra_stop

        sentence_similarity_martix = self.build_similarity_matrix(sentences, stop_words) #costruisco la matrice di similarità basandomi sulla somiglianza dei coseni

        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix) #pagerank per trovare le migliori
        scores = nx.pagerank(sentence_similarity_graph)

        # Prendo le migliori
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)

        top_n=int(len(sentences)/over_mean)
        summarize_text=[]
        for i in range(top_n):
            summarize_text.append(str(ranked_sentence[i][1]))


        #Le riordino per come appaiono nel testo, così da avere un riassunto coerente

        indices=[sentences.index(i) for i in summarize_text]
        indices=sorted(indices)
        final_list=[]
        for i in indices:
            final_list.append(sentences[i])


        self.resume="\n".join(final_list)
        return self.resume

    def sentence_similarity(self,sent1, sent2, stopwords=None):      #similarità coseni per due frasi sent1 e sent2
        if stopwords is None:
            stopwords = []

        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]

        all_words = list(set(sent1 + sent2))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        for w in sent1:
            if w in stopwords:
                continue
            vector1[all_words.index(w)] += 1

        for w in sent2:
            if w in stopwords:
                continue
            vector2[all_words.index(w)] += 1

        return 1 - cosine_distance(vector1, vector2)

    def build_similarity_matrix(self,sentences, stop_words):
        similarity_matrix = np.zeros((len(sentences), len(sentences)))

        widgets = ["[INFO] Building the similarity matrix: ", progressbar.Percentage(), " ",progressbar.Bar(), " ", progressbar.ETA()]
        pbar = progressbar.ProgressBar(maxval=len(sentences)**2,widgets=widgets).start()


        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2: #Escludo la diagonale principale
                    continue
                similarity_matrix[idx1][idx2] = self.sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
                pbar.update((idx1+1)*(idx2+1))

        pbar.finish()
        return similarity_matrix





        return self.resume



    def save(self,outputDir):
        """
        Parameters:
        outputDir: str, path to save the resumed text
        """

        file=open(outputDir,"w")
        file.write(self.resume)
        file.close()
