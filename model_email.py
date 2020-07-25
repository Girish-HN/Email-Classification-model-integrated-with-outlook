import pandas as pd
import numpy as np
import regex as re
import math
import collections
from keywords_v1 import TextRank4Keyword
import nltk


class return_mail_category():
    def mail_contents(self,body, to_details ):
        
        source_path = r'C:\Users\girish.hn\Desktop\ML code integration with outlook\Email Classification model\Preprocessed_v1_1905.xlsx'
        xls = pd.ExcelFile(source_path)

        raw_data = pd.DataFrame(columns = ['Body','Category','To: (Name)'])
        raw_data['Body'] = [body]
        raw_data['To: (Name)'] = to_details
        keywords = pd.read_excel(xls,'Keywords')
        priority_keywords = pd.read_excel(xls,'Prioritised Keywords')

        
        def tokenizer(sample):
            tokenizer = nltk.RegexpTokenizer(r"\w+")
            new_words = tokenizer.tokenize(sample)
            new_words = " ".join(new_words)
            return new_words
        raw_data = raw_data.fillna('')
        print(raw_data)
        raw_data['BPML.COE'] = raw_data['To: (Name)'].apply(lambda x: True if 'BPML.COE' in x else False)

        def cat(x):
            if x:
                return 'Navigator issues/ defects + Data Download'
            else:
                return ""
        raw_data['Prediction'] = raw_data['BPML.COE'].apply(lambda x: cat(x))

        bpml_data = raw_data[raw_data['Prediction']=='Navigator issues/ defects + Data Download']
        
        if not bpml_data.empty:
            bpml_data = bpml_data[['Body','Prediction']]        
        print('Passed bpml data')
        #bpml_data.to_excel('BPML_COE in To predictions.xlsx')
        raw_data = raw_data[raw_data['Prediction']!='Navigator issues/ defects + Data Download']
        priority_prediction = pd.DataFrame()
        secondary_prediction = pd.DataFrame()

        if not raw_data.empty:
            print('Passed raw data')
            raw_data = raw_data[['Body','Prediction','Category']]
            raw_data['Body'] = raw_data['Body'].map(lambda x: str(x).partition('From:')[0])
            raw_data['Body'] = raw_data['Body'].map(lambda x: tokenizer(str(x)))

            pr_kw_without_category = priority_keywords.drop(columns = 'CATEGORY',axis=1).columns.tolist()

            def find_word(text, search):
                result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
                if len(result)>0:
                    return True
                else:
                    return False

            def predict(raw_data, pr_kw_without_category, priority_keywords):
                predictions = {}
                for i in raw_data['Body']:
                    predictions[i] = []
                    for column in pr_kw_without_category:
                        for j in priority_keywords[column]:
                            if find_word(i.lower(),str(j).lower()) and not (pd.isnull(j)) and not (pd.isnull(i)):
                                a = priority_keywords[priority_keywords[column]==j].index[0]
                                predictions[i].append(priority_keywords['CATEGORY'][a])
                    raw_data['Prediction'][raw_data[raw_data['Body']== i].index[0]] = predictions[i]
                return raw_data, predictions

            def outcome(a,b):
                result = []
                for i,j in zip(a,b):
                    if str(i) == str(j):
                        result.append(100)
                    elif str(i) in j:
                        result.append(100)
                    else:
                        result.append(0)
                return result

            raw_data, priority_predictions_dict = predict(raw_data, pr_kw_without_category, priority_keywords)

            #Stage 1: Priority keywords based prediction
            priority_prediction = raw_data[[len(i) > 0 for i in raw_data['Prediction']]]

            priority_prediction.to_excel('Priority predictions.xlsx')

            #Filter empty predictions
            raw_data = raw_data[[len(i) == 0 for i in raw_data['Prediction']]]

            #Stage 2: Secondary keywords based prediction
            pr_kw_with_category = keywords.drop(columns = ['CATEGORY','POCs'],axis=1).columns.tolist()
            raw_data, secondary_predictions_dict  = predict(raw_data, pr_kw_with_category, keywords)
            secondary_prediction = raw_data[[len(i) > 0 for i in raw_data['Prediction']]]

            secondary_prediction.to_excel('Secondary predictions.xlsx')
            print('Passed secondary predictions data')

            #Filter empty predictions
            raw_data = raw_data[[len(i) == 0 for i in raw_data['Prediction']]]
            raw_data.to_excel('raw_data.xlsx')
            raw_data = raw_data.reset_index(drop=True)
            tr4w = TextRank4Keyword()

            fullText =  raw_data.copy()#pd.read_excel(r'C:\Users\girish.hn\Desktop\Email Classification\keyword_approach\keyword_approach\raw_data.xlsx')
            if not fullText.empty:
                fullText['Body'] = fullText['Body'].astype(str)
                #to drop rows with black Body

                keyword_text = []

                for i in range(len(fullText)):

                    text = fullText['Body'][i]

                    tr4w.analyze(text, candidate_pos = ['NOUN', 'VERB', 'ADJ', 'ADP'], window_size=4, lower=False)
                    keywords_extract= tr4w.get_keywords(10)
                    keywords_extract = ','.join([str(elem) for elem in keywords]) 
                    keyword_text.append(keywords)
                    
                #keyword_text = ' '.join([str(elem) for elem in keyword_text])     
                    
                fullText['Keywords'] = keyword_text    

                fullText.to_excel(r'C:\Users\girish.hn\Desktop\Email Classification\keyword_approach\keyword_approach\keywords_sub.xlsx',index=False)
                fullText = fullText.reset_index(drop=True)

                #Stage 3: Derived keyword based predictions

                derived_keywords = pd.read_excel(r'C:\Users\girish.hn\Desktop\Email Classification\keyword_approach\keyword_approach\keywords_sub.xlsx')
                email_keywords = derived_keywords.copy()
                derived_keywords = derived_keywords.dropna().groupby('Category')['Keywords'].apply(','.join).reset_index()
                from random import shuffle

                def shuffle_list(x):
                    x = x.split(',')
                    shuffle(x)
                    x = x[:25]
                    return x

                derived_keywords['Keywords'] = derived_keywords['Keywords'].apply(lambda x: shuffle_list(x))

                #email_keywords = pd.read_excel(r'C:\Users\girish.hn\Desktop\Email Classification\keyword_approach\keyword_approach\keywords_sub.xlsx')
                print(email_keywords.shape)
                final_email = []
                final_class = []
                email_keywords['Keywords'] = email_keywords['Keywords'].fillna('')

                for i in range(len(email_keywords['Keywords'])):
                    email_class = email_keywords['Keywords'][i]
                    email_class = email_class.split(",")
                    classifier = {}
                    list_length = [0]
                    email_classified = []

                    for col in range(len(derived_keywords)):
                        print(col)
                        keyword_class = derived_keywords['Keywords'][col]
                        common = list(set(email_class) & set(keyword_class))
                        if (max(list_length) < (len(common))):
                            list_length.clear()
                            email_classified.clear()
                            email_classified.append(keywords['CATEGORY'][col])
                            list_length.append(len(common))
                        elif max(list_length) == len(common):
                            email_classified.append(keywords['CATEGORY'][col])
                            list_length.append(len(common))    
                    final_class.append(email_classified)

                print(len(raw_data),len(final_class))
                raw_data['Prediction'] = final_class

                raw_data.to_excel('Non priority.xlsx')

        priority_prediction = pd.concat([bpml_data,priority_prediction,secondary_prediction,raw_data],axis = 0)
        priority_prediction = priority_prediction.sort_index()
        print(priority_prediction)
            #priority_prediction.to_excel("Remodeled_outcome.xlsx",sheet_name = 'Outcome')


new = return_mail_category()

new.mail_contents('New string value shared with the team','girish.hn@accenture.com')