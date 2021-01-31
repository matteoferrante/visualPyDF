import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import matplotlib.pyplot as plt
from wordcloud import WordCloud


class TextStatistics:
    def __init__(self,text):
        """
        Parameters:
        ------------
        text: str, text to analyze


        """
        self.text=text.lower()


    def tokenizeWords(self,remove_stop=True,extra_stop=None):
        """
        Function to tokenize word
        Parameters
        -----------
        remove_stop: boolean to check if remove or not stopwords
        extra_stop:  list of document specific words to remove

        Return:
        -----------
        clean_tokens: list of tokens
        """
        if extra_stop is None:
            extra_stop=[]

        tokens=word_tokenize(self.text)
        clean_tokens=tokens[:]
        if remove_stop:
            sr=stopwords.words('english')
            for token in tokens:
                if token in sr or token in extra_stop:
                    clean_tokens.remove(token)
        clean_tokens=[i for i in clean_tokens if i.isalnum()]

        return clean_tokens

    def bigramFrequence(self,outputDir=None,extra_stop=None):


        """
        Compute the frequence of bigrams

        Parameters:
        -----------
        outputDir: str, default None. If set, an image of output will be saved in that Path


        Return:
        ------------
        fr_sorted: sorted frequency list

        """

        clean_tokens=self.tokenizeWords(extra_stop=extra_stop)
        lemmatizer = WordNetLemmatizer()
        lemmas=[lemmatizer.lemmatize(i) for i in clean_tokens]          #riduco le parole nella loro forma base

        bigrams=nltk.bigrams(lemmas)
        b=list(bigrams)
        freq = nltk.FreqDist(nltk.bigrams(lemmas))
        fr=list(freq.items())
        fr_sorted=sorted(fr,key=lambda x: x[1],reverse=True)           #questo è un elenco dei bigrammi più frequenti

        fig = plt.figure(figsize = (10,4))
        plt.gcf().subplots_adjust(bottom=0.15) # to avoid x-ticks cut-off
        a=freq.plot(25, cumulative=False)

    #    plt.show()
        if outputDir is not None:
            fig.savefig(outputDir, bbox_inches = "tight")
        else:
            plt.show()
            plt.close()
        return fr_sorted,fig

    def computeFreq(self,extra_stop=None):
        """Compute a dictionary of frequence for single tokens
        Parameters:
        ------------
        extra_stop: list of extra stop words

        """

        clean_tokens=self.tokenizeWords(extra_stop=extra_stop)
        return nltk.FreqDist(clean_tokens)


    def wordCloud(self,outputDir,background_color="#101010",height=720,width=1080,extra_stop=None):
        """
        Generate a word cloud

        Parameters:
        -------------
        outputDir: string, path to save image
        background color: hesadecimal color string, default dark gray
        height: int, height of image
        width: int, height of image


        """
        word_cloud = WordCloud(
            background_color=background_color,
            width=width,
            height=height)

        freq=self.computeFreq(extra_stop=extra_stop)
        wordcloudimg=word_cloud.generate_from_frequencies(freq)
        if outputDir is not None:
                word_cloud.to_file(outputDir)
        fig,ax=plt.subplots(1)
        ax.imshow(wordcloudimg)
        return fig