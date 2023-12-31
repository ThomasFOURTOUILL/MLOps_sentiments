# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 00:30:02 2023

@author: t.fourtouill
"""

import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_title="Satisfaction Client")
with open('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/style.css') as f: 
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 

image_poing = Image.open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/images/OIP.png")
st.sidebar.image(image_poing)
st.sidebar.markdown("Developed by Yvon-Arnaud GBE and Thomas FOURTOUILL using [Streamlit](https://www.streamlit.io)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.2")

import pandas as pd
from pathlib import Path
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import tensorflow as tf
import keras

from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.models import load_model
from joblib import dump, load
import pickle

pd.options.display.max_colwidth=800
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

# vectorisation pour des notes de 1 à 5
cdiscount = pd.read_csv('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/cdiscount2.csv')
cdiscount = cdiscount[cdiscount['commentaire'].isna()==False]
X = cdiscount['commentaire']
y = cdiscount['note'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# vectorisation pour les sentiments négatifs et positif
cdiscount_0_1 = pd.read_csv('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/cdiscount_0_1.csv')
cdiscount_0_1 = cdiscount_0_1[cdiscount_0_1['commentaire'].isna()==False]
X1 = cdiscount_0_1['commentaire']
y1 = cdiscount_0_1['note'].values

X_train1, X_test1, y_train1, y_test1 = train_test_split(X1, y1, test_size=0.2, random_state=123)

# instanciation des pages ici 3
page = st.sidebar.radio(label='page n°', options=[1, 2, 3])

# contenu de la 1ère page
if page==1:
    
    st.title("Projet satisfaction clients")
    st.markdown(""" 
                l'objectif est de prédire la note à attribuer en fonction d'un commentaire
                """)      
    st.write("présentation des données") 
    st.write("voici un aperçu du jeu de données qui a servi à la construction des modèles : ")
    
    with st.spinner(text="Les données sont en cours de chargement ...."):
        st.dataframe(cdiscount)
   
    # mise en cache du DataFrame cdiscount qui a servi à construire les modèles pour téléchargement dans stramlit
    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(cdiscount)
    st.download_button(label="Download", data=csv, file_name="commentaire_cdiscount.csv", help="si vous souhaitez télécharger le fichier qui contient les 120000 commentaires cdiscount avec les notes qui on servies à construire les modèles de prédiction, cliquer sur ce bouton")
    
    st.write("")
    st.write("Répartition des notes de notre jeu de données :")
    barre = cdiscount['note'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax1 = plt.subplot(1,1,1)
    ax1.bar(barre.index, barre)
    plt.grid(True, axis='y')
    st.pyplot(fig)
    
    st.write("")
    st.write("Répartition des sentiments de notre jeu de données :")
    barre = cdiscount_0_1['note'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax1 = plt.subplot(1,1,1)
    ax1.bar(barre.index, barre)
    plt.xticks([0, 1])
    plt.grid(True, axis='y')
    st.pyplot(fig)
    
    st.write("")
    st.markdown("""
                Affichons les mots le plus fréquement contenus dans les commentaires négatifs et dans les commentaires positifs
                """)
    
    image = Image.open('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/images/cloud_negatif.png')
    st.image(image, caption=' les 100 mots négatifs les plus représentés')
    st.write("")
    st.write("")
    image = Image.open('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/images/cloud_positif.png')
    st.image(image, caption=' les 100 mots positifs les plus représentés')
   

# contenu de la 2ème page
elif page==2:
   
    st.markdown("Merci de saisir le commentaire à prédire")
    
    # saisie du commentaire
    comment = st.text_input("saisir un commentaire :")
    
    # Vectorization du commentaire pour les modèles de Deep Learning
    comment_DL = [comment]
    num_words = 5000
    
    tk = Tokenizer(num_words=num_words)
    tk.fit_on_texts(X_train)
    check_seq = tk.texts_to_sequences(comment_DL)
   
    tk_0_1 = Tokenizer(num_words=num_words)
    tk_0_1.fit_on_texts(X_train1)    
    check_seq_0_1 = tk_0_1.texts_to_sequences(comment_DL) 
    
    # mise sous matrice numpy
    max_words = 130
    check_pad = pad_sequences(check_seq, maxlen=max_words, padding='post')
    check_pad_0_1 = pad_sequences(check_seq_0_1, maxlen=max_words, padding='post')
    
    st.markdown("""
                Merci de sélectionner le modèle que vous souhaitez
                appliquer sur le dataset
                """)
    
    notation = st.radio(label = "Choisissez le type de prédictions :",
             options = ["notation de 1 à 5",
                        "Commentaire négatif ou positif"])
    
    if notation == "notation de 1 à 5":    
    
        selection_method = st.radio(label = "choisissez la méthode :",
                 options = ["Machine Learning",
                            "Deep Learning"])
     
        if selection_method == "Machine Learning":
            
            selection_model_ML = st.radio(label = "choisissez un modèle de machine learning à évaluer :",
                     options = ["RandomForest",
                                "DecisionTreeClassifier",
                                "Random_Forest_ngram"
                                ])      
        
            st.markdown("affichage de la vectorisation du commentaire test")
        
            if selection_model_ML == "RandomForest":
                # Vectorization du commentaire pour les modèles de Machine Learning   
                vectorizer = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/rfc.pkl", "rb")))
                comment_ML = pd.Series(comment)
                comment_to_predict = vectorizer.transform(comment_ML).todense()
                st.write(comment_to_predict)
               
                model = load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_rf.joblib')
                check_predict = model.predict(comment_to_predict)
                st.write("la note attribuée par le modèle est :")
                st.write(check_predict)
        
            elif selection_model_ML == "DecisionTreeClassifier":
                # Vectorization du commentaire pour les modèles de Machine Learning   
                vectorizer = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/dtc.pkl", "rb")))
                comment_ML = pd.Series(comment)
                comment_to_predict = vectorizer.transform(comment_ML).todense()
                st.write(comment_to_predict)
               
                model = load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_dtc.joblib')
                check_predict = model.predict(comment_to_predict)
                st.write("la note attribuée par le modèle est :")
                st.write(check_predict)

            elif selection_model_ML == "Random_Forest_ngram":
                # Vectorization du commentaire pour les modèles de Machine Learning   
                vectorizer = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/rfc_ngram12.pkl", "rb")))
                comment_ML = pd.Series(comment)
                comment_to_predict = vectorizer.transform(comment_ML).todense()
                st.write(comment_to_predict)
               
                model = load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_rf_ngrams_1_2.joblib')
                check_predict = model.predict(comment_to_predict)
                st.write("la note attribuée par le modèle est :")
                st.write(check_predict)

        elif selection_method == "Deep Learning":
        
            selection_model_DL = st.radio(label = "choisissez un modèle de deep learning à évaluer :",
                     options = ["Embedding-Dense",
                                "Embedding-RNN-LTSM",
                                'Embedding-RNN-GRU'
                                ])
            
            st.markdown("affichage de la vectorisation du commentaire test")
            st.write(check_pad)
                
            if selection_model_DL == "Embedding-Dense":
                model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_embedding7')
                check_predict = model.predict(check_pad, verbose=1)
                check_predict_class = check_predict.argmax(axis=1)
                st.write("la note attribuée par le modèle est :")
                st.write(check_predict_class)
                
            elif selection_model_DL == "Embedding-RNN-LTSM":
                model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_embedding4')
                check_predict = model.predict(check_pad, verbose=1)
                check_predict_class = check_predict.argmax(axis=1)
                st.write("la note attribuée par le modèle est :")
                st.write(check_predict_class)
                
            elif selection_model_DL == "Embedding-RNN-GRU":
                model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_embedding8')
                check_predict = model.predict(check_pad, verbose=1)
                check_predict_class = check_predict.argmax(axis=1)
                st.write("la note attribuée par le modèle est :")
                st.write(check_predict_class)
            
    elif notation == "Commentaire négatif ou positif":    
    
        selection_method = st.radio(label = "choisissez la méthode :",
                 options = ["Machine Learning",
                            "Deep Learning"])
     
        if selection_method == "Machine Learning":
            
            selection_model_ML = st.radio(label = "choisissez un modèle de machine learning à évaluer :",
                     options = ["RandomForest",
                                "DecisionTreeClassifier",
                                "Random_Forest_ngram"
                                ])      
                
            st.markdown("affichage de la vectorisation du commentaire test")
        
            if selection_model_ML == "RandomForest":
                vectorizer_0_1 = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/rfc_0_1.pkl", "rb")))
                comment_ML = pd.Series(comment)
                comment_to_predict_0_1 = vectorizer_0_1.transform(comment_ML).todense()
                st.write(comment_to_predict_0_1)
                
                model = load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_rf_0_1_tfidf.joblib')
                check_predict_0_1 = model.predict(comment_to_predict_0_1)
                if check_predict_0_1==0:
                    st.write('le commentaire est négatif')
                else:
                    st.write('le commentaire est postif')  
        
            elif selection_model_ML == "DecisionTreeClassifier":
                # Vectorization du commentaire pour les modèles de Machine Learning   
                vectorizer_0_1 = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/dtc_0_1.pkl", "rb")))
                comment_ML = pd.Series(comment)
                comment_to_predict_0_1 = vectorizer_0_1.transform(comment_ML).todense()
                st.write(comment_to_predict_0_1)
                
                model = load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_dtc_0_1.joblib')
                check_predict_0_1 = model.predict(comment_to_predict_0_1)
                if check_predict_0_1==0:
                    st.write('le commentaire est négatif')
                else:
                    st.write('le commentaire est postif')  
        
            elif selection_model_ML == "Random_Forest_ngram":
                # Vectorization du commentaire pour les modèles de Machine Learning   
                vectorizer_0_1 = CountVectorizer(decode_error="replace", vocabulary=pickle.load(open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/rfc_ngram12_0_1.pkl", "rb")))
                comment_ML = pd.Series(comment)
                comment_to_predict_0_1 = vectorizer_0_1.transform(comment_ML).todense()
                st.write(comment_to_predict_0_1)
                
                model = load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_rf_0_1_ngrams_1_2.joblib')
                check_predict_0_1 = model.predict(comment_to_predict_0_1)
                if check_predict_0_1==0:
                    st.write('le commentaire est négatif')
                else:
                    st.write('le commentaire est postif')  


        elif selection_method == "Deep Learning":
        
            selection_model_DL = st.radio(label = "choisissez un modèle de deep learning à évaluer :",
                     options = ["Embedding-Dense",
                                "Embedding-RNN-LTSM",
                                'Embedding-RNN-GRU'
                                ])
        
            st.markdown("affichage de la vectorisation du commentaire test")
            st.write(check_pad_0_1)
        
            if selection_model_DL == "Embedding-Dense":
                
                np.load('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/matrices/X_pad_embedding7.npy')
                
                model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_0_1_embedding7')
                check_predict_0_1 = model.predict(check_pad_0_1, verbose=1)
                check_predict_class_0_1 = check_predict_0_1.argmax(axis=1)
                if check_predict_class_0_1==0:
                    st.write('le commentaire est négatif')
                else:
                    st.write('le commentaire est postif')  
                
            elif selection_model_DL == "Embedding-RNN-LTSM":
                model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_0_1_embedding4')
                check_predict_0_1 = model.predict(check_pad_0_1, verbose=1)
                check_predict_class_0_1 = check_predict_0_1.argmax(axis=1)
                if check_predict_class_0_1==0:
                    st.write('le commentaire est négatif')
                else:
                    st.write('le commentaire est postif')  
                    
            elif selection_model_DL == "Embedding-RNN-GRU":
                model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/models/model_0_1_embedding8')
                check_predict_0_1 = model.predict(check_pad_0_1, verbose=1)
                check_predict_class_0_1 = check_predict_0_1.argmax(axis=1)
                if check_predict_class_0_1==0:
                    st.write('le commentaire est négatif')
                else:
                    st.write('le commentaire est postif')  
  
# contenu de la 2ème page
elif page==3:
    st.title("Documentation du projet")
    st.markdown(""" 
                Ci-desosus vous trouverez la documentation qui a été présentée lors du projet
                """)  
    
    with open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients/documentation.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(label="Download PDF Tutorial", 
        data=PDFbyte,
        file_name="documentation.pdf",
        mime='application/octet-stream')