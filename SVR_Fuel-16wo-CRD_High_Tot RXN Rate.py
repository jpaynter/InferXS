import h5py as h5
import numpy as np
import pylab as pl
from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split

################################################################################
################################    Data Extraction   ##########################
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
#    Flux
#    Tot. RXN Rate, Abs. RXN Rate, Fiss. RXN Rate, NuFiss. RXN Rate
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'

# Get target regression values for each sample
targets = sample_file[batch][energy][tally]['Targets'][...]
targets = [l[0] for l in targets]
# Get the feature vectors for each sample
features = sample_file[batch][energy][tally]['Features'][...]

############################DATA ANALYSIS#######################################
split = .33
training = int((1-split)*len(features))
testing = int(split*len(features))

#### Split the data
X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=split, random_state=10)

#### Fit regression model
print 'regression'
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
svr_lin = SVR(kernel='linear', C=1e3)
svr_poly = SVR(kernel='poly', C=1e3, degree=2)

y_train_rbf = svr_rbf.fit(X_train, y_train).predict(X_train)
y_train_lin = svr_lin.fit(X_train, y_train).predict(X_train)
y_train_poly = svr_poly.fit(X_train, y_train).predict(X_train)

#### Make predictions based on the models

y_test_rbf = svr_rbf.predict(X_test)
y_test_lin = svr_lin.predict(X_test)
y_test_poly = svr_poly.predict(X_test)

#### Calculate training and testing error
print 'calc'
error_train_rbf=0
error_train_lin=0
error_train_poly=0
for i in range(training):
    diff_train_rbf = y_train_rbf[i] - y_train[i]
    diff_train_lin = y_train_lin[i] - y_train[i]
    diff_train_poly = y_train_poly[i] - y_train[i]
    error_train_rbf = error_train_rbf + diff_train_rbf*diff_train_rbf
    error_train_lin = error_train_lin + diff_train_lin*diff_train_lin
    error_train_poly = error_train_poly + diff_train_poly*diff_train_poly
error_train_rbf = error_train_rbf/training
error_train_lin = error_train_lin/training
error_train_poly = error_train_poly/training

error_test_rbf=0
error_test_lin=0
error_test_poly=0
for i in range(testing):
    diff_test_rbf = y_test_rbf[i] - y_test[i]
    diff_test_lin = y_test_lin[i] - y_test[i]
    diff_test_poly = y_test_poly[i] - y_test[i]
    error_test_rbf = error_test_rbf + diff_test_rbf*diff_test_rbf
    error_test_lin = error_test_lin + diff_test_lin*diff_test_lin
    error_test_poly = error_test_poly + diff_test_poly*diff_test_poly
error_test_rbf = error_test_rbf/testing
error_test_lin = error_test_lin/testing
error_test_poly = error_test_poly/testing

print 'RBF kernel training error is %f' % (error_train_rbf)
print 'Linear kernel training error is %f' % (error_train_lin)
print 'Polynomial, 2nd degree, training error is %f' % (error_train_poly)

print 'RBF kernel testing error is %f' % (error_test_rbf)
print 'Linear kernel testing error is %f' % (error_test_lin)
print 'Polynomial, 2nd degree, testing error is %f' % (error_test_poly)
