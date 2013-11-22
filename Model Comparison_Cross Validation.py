'''
Model selection script that uses cross-validation to determine parameter
settings for a variety of models and then displays the test error for the best
parameters.

The file takes most of the previous Tree / SVR / PCA-cluster-SVR files and
first runs the models through a cross-validation scoring, and then uses
the evaluation and output for the best parameters from PCA-cluster-SVR.

Predictions are setup for one assembly ("1.6-wo-CRD") and the main tally
of interest, "Tot. XS". All batches are considered.

Models considered, with parameters:
    1) SVR - RBF kernel with: width (gamma), and penalty (C)
    2) CART1 - Regression tree with: samples per leaf (min_samples_leaf)
    3) Cluster/SVR - Kmeans cluster with varying k; SVR as (1)
    
'''

import math
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
from cluster import cluster
from sklearn import tree
from sklearn.svm import SVR
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split

################################################################################
##################################    Parameters   #############################
################################################################################

# SVR kernel type and parameters
kernel = 'rbf'
C = [1,10,100,500,750,1000]
gamma = [.001,.01,0.1,.2,.3,.4,.5,.6,.7,.8,.9,1,10]

# CART parameters
min_samples_leaf = [3,5,8,10,12,15,17,20,23]
max_depth = [2,3,4,5,6]

# Number of PCA components
num_components = 3

# Number of clusters to find
num_clusters = 6

################################################################################
################################    Data Extraction   ##########################
################################################################################

# Open a handle to the HDF5 file with the Monte Carlo RMS errors for each batch
rms_ref = h5.File('data/target-batch-rms.h5', 'r')

# Create a file handle for the samples file
assemblies = ['Fuel-1.6wo-CRD',
              'Fuel-2.4wo-16BA-grid-56',
              'Fuel-3.1wo-instr-16BA-grid-17']
batches = [10,50,100,200,300,400,500,600,700,800,900,1000]
energies = ['Low Energy', 'High Energy']
tallies = ['Tot. XS', 'Abs. XS', 'Fiss. XS', 'NuFiss. XS']

assembly = 'Fuel-1.6wo-CRD'
tally = 'Tot. XS'

sample_file = h5.File('data/' + assembly + '-samples.h5', 'r')

fig = plt.figure()

# Initialize arrays for the RMS error for this energy
rms_SVR = [[0 for x in range(len(batches))] for energy in energies]
rms_CART = [[0 for x in range(len(batches))] for energy in energies]
rms_CLSVR = [[0 for x in range(len(batches))] for energy in energies]

# Iterate over energies (Low, High)
count = 0
for energy in energies:

    print ' '
    print '    ' + energy

    # Iterate over batches
    for index in enumerate(batches):
    
        # Construct the batch identifier for the HDF5 dataset
        batch = 'Batch-' + str(index[1])

        # Get target regression values for each sample
        y = sample_file[batch][energy][tally]['Targets'][...]
        y = np.reshape(y, 2890)

        # Get the feature vectors for each sample
        X = sample_file[batch][energy][tally]['Features'][...]
        
        ################################################################
        ############    TRAININING/TESTING DATA SPLITTING   ############
        ################################################################

        scores = list()
        scores_std = list()

        #### Split the data
        split = .33
        training = int((1-split)*len(X))
        testing = int(split*len(X))
        X_train, X_test, y_train, y_test = train_test_split(X, y, \
                                                            test_size=split, \
                                                            random_state=10)

        ################################################################
        #######################   SVR REGRESSION   #####################
        ################################################################
        # We will store scores, g, and c in this list
        scores_SVR = [[] for x in range(3)]
        scores_std_SVR = list()
                    
        # Extract features/targets for this cluster's samples
        features = X_train
        targets = y_train

        # Loop over each possible parameter setting
        for c in C:
            for g in gamma:
                    
                # Fit an SVR model on these samples
                model_SVR = SVR(kernel=kernel, C=c, gamma=g)
                model_SVR.fit(features, targets)

                this_scores = cross_validation.cross_val_score(model_SVR, features, targets, \
                                                               scoring='mean_squared_error')
                scores_SVR[0].append(np.mean(this_scores))
                scores_std_SVR.append(np.std(this_scores))
                scores_SVR[1].append(c)
                scores_SVR[2].append(g)           
        
        # Optimal c, g found from the index of the max value    
        best_c = scores_SVR[1][scores_SVR.index(max(scores_SVR))]
        best_gamma = scores_SVR[2][scores_SVR.index(max(scores_SVR))]

        print 'For SVR, the best gamma is %f, and the best C is %f' %(best_gamma, best_c)

        # Retrain the model for the best parameters
        model_SVR = SVR(kernel=kernel, C=best_c, gamma=best_gamma)
        model_SVR.fit(features, targets)

        ################################################################
        ############################   CART    #########################
        ################################################################

        scores_CART = [[] for x in range(3)]
        scores_std_CART = list()
                    
        # Extract features/targets for this cluster's samples
        features = X_train
        targets = y_train

        # Loop over each possible parameter setting
        for leaf in min_samples_leaf:
                    
            # Fit a CART model on these samples
            model_CART = tree.DecisionTreeRegressor(min_samples_leaf=leaf)
            model_CART.fit(features, targets)

            this_scores = cross_validation.cross_val_score(model_CART, features, targets, \
                                                               scoring='mean_squared_error')
            scores_CART[0].append(0)
            scores_CART[1].append(leaf)
            scores_CART[2].append(np.mean(this_scores))
            scores_std_CART.append(np.std(this_scores))

        for depth in max_depth:

            # Fit a CART model on these samples
            model_CART = tree.DecisionTreeRegressor(max_depth=depth)
            model_CART.fit(features, targets)

            this_scores = cross_validation.cross_val_score(model_CART, features, targets, \
                                                               scoring='mean_squared_error')
            scores_CART[0].append(1)
            scores_CART[1].append(depth)
            scores_CART[2].append(np.mean(this_scores))
            scores_std_CART.append(np.std(this_scores))

        best_param_type = scores_CART[0][scores_CART[2].index(max(scores_CART[2]))]
        best_param = scores_CART[1][scores_CART[2].index(max(scores_CART[2]))]
        types = ['min samples per leaf', 'max depth']
        print 'For CART, best parameter is %s of %0.2g' %(types[best_param_type], best_param)
    
        # Retrain the model for the best parameters
        if best_param_type == 0:
            model_CART = tree.DecisionTreeRegressor(min_samples_leaf=best_param)
        else:
            model_CART = tree.DecisionTreeRegressor(max_depth=best_param)
        model_CART.fit(features, targets)
        
        ################################################################
        #########################    CLUSTERING   ######################
        ################################################################

        # Build a cluster model using PCA transformation and KMeans
        cluster_model = cluster.Cluster(X_train)
        cluster_model.build_pca_model(num_components=num_components)
        cluster_model.build_clusters(method='kmeans', 
                                        num_clusters=num_clusters)

        # Apply PCA feature space transformation to the input features
        # NOTE: This means that SVR is being performed in the lower
        #       dimensional space spanned by the SVD singular vectors
        X_test_PCA = cluster_model.apply_pca_model(X_test)
        X_train_PCA = cluster_model.apply_pca_model(X_train)

        ################################################################
        #####################   CL SVR REGRESSION   ####################
        ################################################################

        # Initialize an empty dictionary to contain SVR models
        # for each cluster, indexed by cluster ID
        models_CLSVR = {}

        # Get the cluster IDs for each training sample
        #     ie, 0 - cluster 0, 1 - cluster 1, ...
        indices = cluster_model.clusterize(X_train_PCA)

        # Loop over each cluster and train a model for it's samples
        best_gamma=[0 for x in range(num_clusters)]
        best_c=[0 for x in range(num_clusters)]
        for c in range(num_clusters):

            scores_CLSVR = [[] for x in range(3)]
            scores_std_CLSVR = list()
                    
            # Extract features/targets for this cluster's samples
            features = X_train_PCA[indices[c],:]
            targets = y_train[indices[c]]

            # Loop over each possible parameter setting
            for p in C:
                for g in gamma:
                    
                    # Fit an SVR model on this cluster's samples
                    models_CLSVR[c] = SVR(kernel=kernel, C=p, gamma=g)
                    models_CLSVR[c].fit(features, targets)

                    this_scores = cross_validation.cross_val_score(models_CLSVR[c], features, targets, \
                                                               scoring='mean_squared_error')
                    scores_CLSVR[0].append(np.mean(this_scores))
                    scores_std_CLSVR.append(np.std(this_scores))
                    scores_CLSVR[1].append(p)
                    scores_CLSVR[2].append(g)

            best_c[c] = scores_CLSVR[1][scores_CLSVR[0].index(max(scores_CLSVR[0]))]
            best_gamma[c] = scores_CLSVR[2][scores_CLSVR[0].index(max(scores_CLSVR[0]))]
   
            # Retrain the model for the best parameters
            models_CLSVR[c] = SVR(kernel=kernel, C=best_c[c], gamma=best_gamma[c])
            models_CLSVR[c].fit(features, targets)

        print 'In CL SVR, the best gammas are: %0.3g, %0.3g, %0.3g, %0.3g, %0.3g, %0.3g' \
              %(best_gamma[0], best_gamma[1], best_gamma[2], best_gamma[3], \
                best_gamma[4], best_gamma[5])
        print 'In CL SVR, the best Cs are: %0.3g, %0.3g %0.3g, %0.3g, %0.3g, %0.3g' \
              %(best_c[0], best_c[1], best_c[2], best_c[3], \
                best_c[4], best_c[5])

        ################################################################
        #######################    SVR PREDICTION   ####################
        ################################################################

        ##########################  TRAINING  ##########################

        # Initialize an empty array for the predicted target values
        y_train_predict_SVR = np.zeros(len(y_train))
                    
        # Store the predicted values for this cluster's samples
        y_train_predict_SVR = model_SVR.predict(X_train)

        ###########################  TESTING  ##########################

        # Initialize an empty array for the predicted target values
        y_test_predict_SVR = np.zeros(len(y_test))

        # Store the predicted values for this cluster's samples
        y_test_predict_SVR = model_SVR.predict(X_test)

        ################################################################
        ###################### CART PREDICTION   #######################
        ################################################################

        ##########################  TRAINING  ##########################

        # Initialize an empty array for the predicted target values
        y_train_predict_CART = np.zeros(len(y_train))
                    
        # Store the predicted values for this cluster's samples
        y_train_predict_CART = model_CART.predict(X_train)

        ###########################  TESTING  ##########################

        # Initialize an empty array for the predicted target values
        y_test_predict_CART = np.zeros(len(y_test))

        # Store the predicted values for this cluster's samples
        y_test_predict_CART = model_CART.predict(X_test)
          
        ################################################################
        #####################    CL SVR PREDICTION   ###################
        ################################################################

        ##########################  TRAINING  ##########################

        # Initialize an empty array for the predicted target values
        y_train_predict_CLSVR = np.zeros(len(y_train))

        # Loop over each cluster and make predictions for each 
        # training sample
        for c in range(num_clusters):

            # Extract features for this cluster's samples
            features = X_train_PCA[indices[c],:]
                    
            # Store the predicted values for this cluster's samples
            y_train_predict_CLSVR[indices[c]] = models_CLSVR[c].predict(features)


        ###########################  TESTING  ##########################
                
        # Get the cluster IDs for each test sample
        #     ie, 0 - cluster 0, 1 - cluster 1, ...
        indices = cluster_model.clusterize(X_test_PCA)

        # Initialize an empty array for the predicted target values
        y_test_predict_CLSVR = np.zeros(len(y_test))

        # Loop over each cluster and make predictions for each 
        # test sample
        for c in range(num_clusters):

            # Extract features for this cluster's samples
            features = X_test_PCA[indices[c]]

            # Store the predicted values for this cluster's samples
            y_test_predict_CLSVR[indices[c]] = models_CLSVR[c].predict(features)
    
        ################################################################
        ##################    TRAINING/TESTING ERROR   #################
        ################################################################

        # Compute the RMS error for the training and test samples
        train_error_SVR = np.power(y_train_predict_SVR - y_train, 2)
        test_error_SVR = np.power(y_test_predict_SVR - y_test, 2)
        train_error_SVR = np.sqrt(np.mean(train_error_SVR))
        test_error_SVR = np.sqrt(np.mean(test_error_SVR))
        
        # Compute the RMS error for the training and test samples
        train_error_CART = np.power(y_train_predict_CART - y_train, 2)
        test_error_CART = np.power(y_test_predict_CART - y_test, 2)
        train_error_CART = np.sqrt(np.mean(train_error_CART))
        test_error_CART = np.sqrt(np.mean(test_error_CART))
        
        # Compute the RMS error for the training and test samples
        train_error_CLSVR = np.power(y_train_predict_CLSVR - y_train, 2)
        test_error_CLSVR = np.power(y_test_predict_CLSVR - y_test, 2)
        train_error_CLSVR = np.sqrt(np.mean(train_error_CLSVR))
        test_error_CLSVR = np.sqrt(np.mean(test_error_CLSVR))
        
        # Store the RMS error for this 
        rms_SVR[count][index[0]] = test_error_SVR

        # Store the RMS error for this 
        rms_CART[count][index[0]] = test_error_CART

        # Store the RMS error for this 
        rms_CLSVR[count][index[0]] = test_error_CLSVR
        
        # Print the results for this case to the screen
        print ' Batch %d' %(index[1])
        print '     SVR: \t train err. %0.3g \t test err. %0.3g' \
                % (train_error_SVR, test_error_SVR)
        print '     CART: \t train err. %0.3g \t test err. %0.3g' \
                % (train_error_CART, test_error_CART)
        print '     CL SVR: \t train err. %0.3g \t test err. %0.3g' \
                % (train_error_CLSVR, test_error_CLSVR)

    count = count + 1

################################################################
###########################    PLOTS   #########################
################################################################

# Plot the RMS for this tally, low energy

energy = 'Low Energy'
plt.semilogy(rms_ref['Batches'],rms_ref[assembly][energy][tally][...], linewidth=2)
plt.semilogy(batches, rms_SVR[0], linewidth=2)
plt.semilogy(batches, rms_CART[0], linewidth=2)
plt.semilogy(batches, rms_CLSVR[0], linewidth=2)
    
# Annotate the plot
plt.ylabel('Root Mean Squared Error')
plt.xlabel('Batch #')
plt.title(assembly + ' ' + tally + ' Low Energy' + ' RMS')
plt.grid(b=True, which='major', color='b', linestyle='-')
plt.grid(b=True, which='minor', color='r', linestyle='--')
plt.legend(['Low Energy - Actual','Low Energy - RBF SVR', 'Low Energy - CART',
            'Low Energy - RBF CL SVR'])

# Save the plot
filename = 'Low-Energy' + tally.replace('.', '').replace(' ', '-').lower()
filename = 'process/rms-plots/' + assembly + '/' + filename + '.png'
plt.savefig(filename)

plt.show()

# Plot the RMS for this tally, high energy

energy = 'High Energy'
plt.semilogy(rms_ref['Batches'],rms_ref[assembly][energy][tally][...], linewidth=2)
plt.semilogy(batches, rms_SVR[1], linewidth=2)
plt.semilogy(batches, rms_CART[1], linewidth=2)
plt.semilogy(batches, rms_CLSVR[1], linewidth=2)
    
# Annotate the plot
plt.ylabel('Root Mean Squared Error')
plt.xlabel('Batch #')
plt.title(assembly + ' ' + tally + ' High Energy' + ' RMS')
plt.grid(b=True, which='major', color='b', linestyle='-')
plt.grid(b=True, which='minor', color='r', linestyle='--')
plt.legend(['High Energy - Actual','High Energy - RBF SVR', 'High Energy - CART',
            'High Energy - RBF CL SVR'])

# Save the plot
filename = 'High-Energy' + tally.replace('.', '').replace(' ', '-').lower()
filename = 'process/rms-plots/' + assembly + '/' + filename + '.png'
plt.savefig(filename)

plt.show()
