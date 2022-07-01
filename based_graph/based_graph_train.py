# -*- coding: utf-8 -*-
"""based_graph_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DQ-C7bzYMe5o0-Enq2GT6Tkw1tHD-Wh1
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import pandas as pd
import numpy as np
import ampligraph
from ampligraph.latent_features import ComplEx, TransE, DistMult, HolE

# %tensorflow_version 1.x
import tensorflow as tf
print(tf.__version__)


#get the models
from based_graph_models import(
    complex,
    transe,
    distmult,
    hole
)


model_name = 'ComplEx'

if model_name == "ComplEx":

        model = complex()
    elif model_name == "TransE":
        model = transe()
    elif model_name == "DistMult":
        model = distmult()
    elif model_name == "holE":
        model = hole()


#get the data
train_data = pd.read_csv('../datasets/train-data.csv')
test_data = pd.read_csv('../datasets/test-data.csv')

train_data = train_data.iloc[: , 1:]
test_data = test_data.iloc[: , 1:]

X_train = train_data.to_numpy()
X_test = test_data.to_numpy()


#training
tf.logging.set_verbosity(tf.logging.ERROR)

model.fit(np.concatenate((X_train, X_test)))

from ampligraph.utils import save_model, restore_model

save_model(model, f"{model_name}.pkl")


#evaluation
#we willcompute the rank of each positive tripe against a number of negatives generated on the data

#we need to define our filters
filter_triples = np.concatenate((X_train, X_test))

from ampligraph.evaluation import evaluate_performance

ranks = evaluate_performance(X_test,
                             model=model, 
                             filter_triples=filter_triples,
                             corrupt_side='s+o',
                             verbose =True )

#we compute the metrics by using mrr_score, hits_at_n_score and mr_score functinc to compute as metrics for the evaluation
from ampligraph.evaluation import mr_score, mrr_score, hits_at_n_score

mr = mr_score(ranks)
mrr = mrr_score(ranks)

print("MRR: %.2f" % (mrr))
print("MR: %.2f" % (mr))

hits_10 = hits_at_n_score(ranks, n=10)
print("Hits@10: %.2f" % (hits_10))
hits_3 = hits_at_n_score(ranks, n=3)
print("Hits@3: %.2f" % (hits_3))
hits_1 = hits_at_n_score(ranks, n=1)
print("Hits@1: %.2f" % (hits_1))




#prediction

restore_model = restore_model(f"{model_name}.pkl")
scores = restore_model.predict(X_test)
print(scores)

#Now  transform the scores (real numbers) into probabilities (bound between 0 and 1) using the expit transform.
from scipy.special import expit
probs = expit(scores)

pd.DataFrame(list(zip([' '.join(x) for x in X_test], 
                      ranks, 
                      np.squeeze(scores),
                      np.squeeze(probs))), 
             columns=['statement', 'rank', 'score', 'prob']).sort_values("score")