#Using keras to create a text classifier
#Highly inspired from https://github.com/iampukar/toxic-comments-classification

#importing libraries
import os
import re
import sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import RNN, GRU, LSTM, Dense, Input, Embedding, Dropout, Activation, concatenate
from keras.layers import Bidirectional, GlobalAveragePooling1D, GlobalMaxPooling1D
from keras.models import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import initializers, regularizers, constraints, optimizers, layers

#Loading the dataset
train_data = pd.read_csv('AI/train.csv')

#Extracting the labels
classes = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
y = train_data[classes].values

#Lowercase
train_sentences = train_data["comment_text"].fillna("fillna").str.lower()

max_features = 100000
max_len = 150
embed_size = 300

#Tokenize (creates a word index, converting the most recurrent words into floats)
tokenizer = Tokenizer(max_features)
tokenizer.fit_on_texts(list(train_sentences))

#Convert the sentences of the dataset into lists of floats using the tokenizer
tokenized_train_sentences = tokenizer.texts_to_sequences(train_sentences)

#Pad the lists with zeroes so that every list has the same size to be fed to the neural network
train_padding = pad_sequences(tokenized_train_sentences, max_len)

word_index = tokenizer.word_index
nb_words = min(max_features, len(word_index))

#Complex neural network
image_input = Input(shape=(max_len, ))
X = Embedding(max_features, embed_size)(image_input)
X = Bidirectional(GRU(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2))(X)
avg_pl = GlobalAveragePooling1D()(X)
max_pl = GlobalMaxPooling1D()(X)
conc = concatenate([avg_pl, max_pl])
X = Dense(6, activation="sigmoid")(conc)
model = Model(inputs=image_input, outputs=X)

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

saved_model = "cp.ckpt"
cp_callback = ModelCheckpoint(saved_model, save_weights_only=True, verbose=1, save_best_only=True)

#Training
batch_sz = 32
epoch = 2
model.fit(train_padding, y, batch_size=batch_sz, epochs=epoch, validation_split=0.1, callbacks=[cp_callback], steps_per_epoch = 1024)