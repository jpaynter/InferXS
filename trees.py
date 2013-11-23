'''Performs Tree regression for a single dataset without clustering.

   Author: Jonathan Paynter
   Date: 11/11/2013

   Usage: python trees.py

   This script applies decision trees to learn a single dataset (one assembly, 
   reaction rate, energy, batch). The data is stored as 18-dimensional feature 
   vectors for each sample with a single target value. The feature 
   descriptions are given in process/samples.py. The target values for each 
   sample are the converged (after 1000 batches) pinwise tallies (across the 
   entire 3x3 mesh) for each reaction rate and energy.

   This script splits the samples into training and test sets. The next step
   is to train scikit-learn's decision tree model using the training data. 
   Finally, the model is used to predict the target values for the test samples 
   and the Root Mean Square (RMS) error with respect to the true target values 
   is computed and reported to the bash.
'''

import h5py as h5
import numpy as np
import pylab as pl
from sklearn import tree
from sklearn.cross_validation import train_test_split



################################################################################
################################    DATA EXTRACTION   ##########################
################################################################################

# Create a file handle for the samples file
# 3 Assembly types are available:
#    Fuel-1.6wo-CRD
#    Fuel-2.4wo-16BA-grid-56
#    Fuel-3.1wo-instr-16BA-grid-17
sample_file = h5.File('data/Fuel-1.6wo-CRD-samples.h5', 'r')

# Different batch means are available:
#     10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
batch = 'Batch-1000'

# Two energies are available:
#     Low Energy, High Energy
energy = 'High Energy'

# Different tally types are available:
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'

# Get target regression values for each sample
targets = sample_file[batch][energy][tally]['Targets'][...]
targets = [l[0] for l in targets]

# Get the feature vectors for each sample
features = sample_file[batch][energy][tally]['Features'][...]



################################################################################
#####################    TRAININING/TESTING DATA SPLITTING   ###################
################################################################################

split = .33
training = int((1-split)*len(features))
testing = int(split*len(features))

#### Split the data
X_train, X_test, y_train, y_test = train_test_split(features, targets, \
                                                    test_size=split, \
                                                    random_state=10)


################################################################################
###############################   TREE REGRESSION   ############################
################################################################################

#### Fit regression model
rt_1 = tree.DecisionTreeRegressor(min_samples_leaf=5)
rt_2 = tree.DecisionTreeRegressor(max_depth=3)
rt_1.fit(X_train, y_train)
rt_2.fit(X_train, y_train)



################################################################################
###############################   TREE PREDICTION   ############################
################################################################################

#### Make predictions based on the models
y_test_predict_1 = rt_1.predict(X_test)
y_test_predict_2 = rt_2.predict(X_test)

#### Calculate testing error
error_test_1=0
error_test_2=0

for i in range(testing):
    diff_test_1 = y_test_predict_1[i] - y_test[i]
    diff_test_2 = y_test_predict_2[i] - y_test[i]
    error_test_1 = error_test_1 + diff_test_1*diff_test_1
    error_test_2 = error_test_2 + diff_test_2*diff_test_2

error_test_1 = np.sqrt(error_test_1/testing)
error_test_2 = np.sqrt(error_test_2/testing)

print 'Regression tree 1 testing error is %f' % (error_test_1)
print 'Regression tree 2 testing error is %f' % (error_test_2)
