import pandas as pd
from itertools import product
import pickle
from sklearn.feature_extraction.text import CountVectorizer

filename = 'finalized_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))
count_vect = pickle.load(open("vectorizer.pickle", 'rb'))

class stringcheck():

    def __init__(self):
        pass
    
    def method(self,object):
        request = {1:'Request1',0:'Request2'}
        split_body = object.Body.split('From:')[0]
        xvalid_count =  pd.Series(object.Body)

        xvalid_count = count_vect.transform(xvalid_count)
        # load the model
        result = loaded_model.predict(xvalid_count)
        return request[result[0]]