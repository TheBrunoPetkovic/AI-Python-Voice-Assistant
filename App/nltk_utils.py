import nltk 
from nltk.stem.porter import PorterStemmer
import numpy as np
 
#nltk.download("punkt")
stemmer = PorterStemmer()

# Funkcija za tokenizaciju recenice - od stringa pravi listu rijeci
def tokenize(sentence):
   return nltk.word_tokenize(sentence)

# Funkcija za stemmanje rijeci - micanje sufiksa
def stem(word):
   return stemmer.stem(word.lower())

# Funkcija za 
def bag_of_words(tokenized_sentence, all_words):
   tokenized_sentence = [stem(w) for w in tokenized_sentence]
   
   bag = np.zeros(len(all_words), dtype = np.float32)
   for index, w in enumerate(all_words):
      if w in tokenized_sentence:
         bag[index] = 1.0
   
   return bag