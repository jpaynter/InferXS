import h5py as h5
import numpy as np
import pylab as pl
from sklearn import tree
from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split

######################

# Run regression and trees for a given quantity for all batches, and compare

######################

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
Batches = ['Batch-10','Batch-50','Batch-100','Batch-200','Batch-300', \
           'Batch-400','Batch-500','Batch-600','Batch-700','Batch-800', \
           'Batch-900','Batch-1000']

# Two energies are available:
#     Low Energy, High Energy
energy = 'High Energy'

# Different tally types are available:
#    Flux
#    Tot. RXN Rate, Abs. RXN Rate, Fiss. RXN Rate, NuFiss. RXN Rate
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'

#############################LOOP OVER ALL BATCHES#######################

error_test_tree1=[0 for batch in Batches]
error_test_tree2=[0 for batch in Batches]
error_test_rbf=[0 for batch in Batches]
error_test_lin=[0 for batch in Batches]
error_test_poly=[0 for batch in Batches]
count = 0

for batch in Batches:

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
    rt_1 = tree.DecisionTreeRegressor(min_samples_leaf=5)
    rt_2 = tree.DecisionTreeRegressor(max_depth=3)
    rt_1.fit(X_train, y_train)
    rt_2.fit(X_train, y_train)
    
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    svr_rbf.fit(X_train, y_train)
    svr_lin.fit(X_train, y_train)
    svr_poly.fit(X_train, y_train)
    
    #### Make predictions based on the models
    y_test_predict_tree1 = rt_1.predict(X_test)
    y_test_predict_tree2 = rt_2.predict(X_test)

    y_test_predict_rbf = svr_rbf.predict(X_test)
    y_test_predict_lin = svr_lin.predict(X_test)
    y_test_predict_poly = svr_poly.predict(X_test)

    #### Calculate testing error  
    for i in range(testing):
        # trees
        diff_test_tree1 = y_test_predict_tree1[i] - y_test[i]
        diff_test_tree2 = y_test_predict_tree2[i] - y_test[i]
        error_test_tree1[count] = error_test_tree1[count] + diff_test_tree1*diff_test_tree1
        error_test_tree2[count] = error_test_tree2[count] + diff_test_tree2*diff_test_tree2
        # regression
        diff_test_rbf = y_test_predict_rbf[i] - y_test[i]
        diff_test_lin = y_test_predict_lin[i] - y_test[i]
        diff_test_poly = y_test_predict_poly[i] - y_test[i]
        error_test_rbf[count] = error_test_rbf[count] + diff_test_rbf*diff_test_rbf
        error_test_lin[count] = error_test_lin[count] + diff_test_lin*diff_test_lin
        error_test_poly[count] = error_test_poly[count] + diff_test_poly*diff_test_poly

    error_test_tree1[count] = np.sqrt(error_test_tree1[count]/testing)
    error_test_tree2[count] = np.sqrt(error_test_tree2[count]/testing)
    error_test_rbf[count] = np.sqrt(error_test_rbf[count]/testing)
    error_test_lin[count] = np.sqrt(error_test_lin[count]/testing)
    error_test_poly[count] = np.sqrt(error_test_poly[count]/testing)

    count = count + 1

####################END BATCH LOOP##################################


####################OUTPUT##################################
print 'TESTING ERROR EVALUATION'
print 'Tree 1 uses "min samples leaf = 5"'
print 'Tree 2 uses "max depth = 3"'
print 'SV Regression 1 uses a Radial Basis Function kernel (C=1e3, gamma=.1)'
print 'SV Regression 2 uses a linear kernel (C=1e3)'
print 'SV Regression 3 uses a polynomial kernel (C=1e3, gamma=2)'
print ' '

count = 0
for batch in Batches:
    print batch
    print 'For ' + batch + ', Regression tree 1 testing error is %f' % (error_test_tree1[count])
    print 'For ' + batch + ', Regression tree 2 testing error is %f' % (error_test_tree2[count])
    print 'For ' + batch + ', RBF kernel testing error is %f' % (error_test_rbf[count])
    print 'For ' + batch + ', Linear kernel testing error is %f' % (error_test_lin[count])
    print 'For ' + batch + ', Polynomial, 2nd degree, testing error is %f' % (error_test_poly[count])
    count = count + 1

####################GRAPH##################################

x_plot = [10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
pl.figure()
pl.plot(x_plot, error_test_tree1, c="g", label="Tree 1", linewidth=2)
pl.plot(x_plot, error_test_tree2, c="b", label="Tree 2", linewidth=2)
pl.plot(x_plot, error_test_rbf, c="y", label="RBF", linewidth=2)
pl.plot(x_plot, error_test_lin, c="r", label="Linear", linewidth=2)
pl.plot(x_plot, error_test_poly, c="k", label="Poly", linewidth=2)
pl.xlabel("Batch")
pl.ylabel("RMS Error")
pl.title("Decision Tree and SV Kernel Regression")
pl.legend()
pl.show()

# Close the plot to see the better one!

pl.figure()
pl.plot(x_plot, error_test_tree1, c="g", label="Tree 1", linewidth=2)
pl.plot(x_plot, error_test_tree2, c="b", label="Tree 2", linewidth=2)
pl.xlabel("Batch")
pl.ylabel("RMS Error")
pl.title("Decision Tree and SV Kernel Regression")
pl.legend()
pl.show()
