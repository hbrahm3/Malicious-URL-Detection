# -*- coding: utf-8 -*-
"""Malicious_URL Detection NN.ipynb

Automatically generated by Colaboratory.



This is a continuation of the file in which we explored the problem of detecting malicious URls using various classification techniques such as Naive Bayes, Logistic Regression, and Support Vector Machines using both Binary and Multiclass Classification for each.

## **Neural Network for Classification**
"""

# Load the Dataset
import pandas as pd

df = pd.read_csv("malicious_phish.csv")

df

df.type.unique() # 1 of four class labels

# Now we split our dataset into training and testing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

# Transform the data into numpy arrays to make it easier to apply the functions
URLs = np.array(df.url.values)
labels = np.array(df.type.values)

X_train, X_test, y_train, y_test = train_test_split(URLs, labels, test_size=0.2, random_state=32)

# Now we import everything we need for our keras NN model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from keras.models import Sequential
from keras import layers
from keras.wrappers.scikit_learn import KerasClassifier

tokenizer = Tokenizer() # we use the keras built in text tokenizer
tokenizer.fit_on_texts(X_train) #add the URLs in our training set to the vocabulary

# Then we get the final training and testing URLs by converting each to a sequence of integers (tokenized)
X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

vocab_size = len(tokenizer.word_index) + 1 # all the words that our tokenizer now recognizes have been added to vocab

print(X_train[0]) # This is the transformation of the first URL

len_train = [len(i) for i in X_train]
len_test = [len(i) for i in X_test]
max_train = max(len_train)
max_test = max(len_test)
max_url = max(max_train, max_test)


print(max_url) # length of the largest tokenized url

# So we take all of our urls and add padding (0's) to the end of those that are less than max_url in length
X_train = pad_sequences(X_train, padding='post', maxlen=max_url)
X_test = pad_sequences(X_test, padding='post', maxlen=max_url)

type(X_train)
type(X_test)

encoder = LabelEncoder()
encoder.fit(labels) # adds all the possible labels, so we can do multi-class classification

encoded_y_train = encoder.transform(y_train)
encoded_y_test = encoder.transform(y_test)

dummy_train_labels = np_utils.to_categorical(encoded_y_train)
dummy_test_labels = np_utils.to_categorical(encoded_y_test)
type(dummy_test_labels)

type(dummy_train_labels)

type(X_train)

encoded_y_test

print(encoded_y_test[1:30])

print(y_test[1:30])

"""This helps us know the encoding. 
benign -> 0
defacement -> 1
malware -> 2
phishing -> 3
"""

# Now we can start building the neural network itself
import tensorflow as tf

# Instantiate and start adding to NN model
model = Sequential() # A sequential model

model.add(layers.Flatten())

model.add(layers.Dropout(0.2))

#model.add(layers.GlobalAveragePooling1D())

model.add(layers.Dropout(0.2))

model.add(layers.Dense(512, activation='sigmoid')) # 50 neurons with ReLU activation function

model.add(layers.Dropout(0.2))

model.add(layers.Dense(256, activation='relu')) # 50 neurons with ReLU activation function

model.add(layers.Dropout(0.2))

model.add(layers.Dense(4, activation='softmax')) #softmax function for our final output layer

# Now we compile the model, with the metrics that we will need
model.compile(optimizer='adam',
              loss = 'categorical_crossentropy',
              metrics=['accuracy'])

# Since we know we have a major class imbalance, we can set some class weights to help with this
# We know that there is the following data split:
# Benign (0): 0.66%, Defacement (1): 0.15%, Phishing (3): 0.14%, Malware (2): 0.05%

from sklearn.utils import class_weight

class_weights = {0: 1.,
                 1: 2.,
                 2: 10.,
                 3: 2.}

print(X_train)

X_train = np.asarray(X_train).astype(np.float32)

print(X_train)

# Now we can train the model
history = model.fit(X_train, dummy_train_labels,
                    epochs=1,
                    verbose=True,
                    batch_size=128,
                    validation_split=0.1,
                    shuffle=True,
                    class_weight=class_weights
)

model.summary() # get the summary of the layers in the model

pred = np.argmax(model.predict(X_test), axis=-1)

pred

encoded_y_test

from sklearn.metrics import precision_recall_fscore_support, accuracy_score

accuracy = accuracy_score(encoded_y_test, pred)
print("Accuracy:", accuracy)
precision, recall, f1_score, _ = precision_recall_fscore_support(encoded_y_test, pred)
print("Precision: {}, Recall: {}, F1-score: {}".format(precision, recall, f1_score))

metrics_matrix = confusion_matrix(encoded_y_test, y_pred=pred)

metrics_matrix

import seaborn as sns
import matplotlib.pyplot as plt

"""We can visualize the results in a confusion matrix to understand how the neural network classifier behaves for each of the classes."""

sns.heatmap(metrics_matrix, annot = True, fmt = ".3f", square = True, cmap = plt.cm.Blues)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion matrix')
plt.tight_layout()
plt.show()

"""We can see that it performs fairly well for the benign class, but has trouble with the other classes. However, given the massive class imbalance, this was to be expected, and in fact performs better than we had hoped."""

# Tool to take in a url and predict it's label