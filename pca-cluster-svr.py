'''Performs PCA, clustering and SVR regression for all datasets.

   Author: William Boyd
   Date: 11/11/2013

   Usage: python pca-cluster-svr.py

   This script iterates through all of the fuel assemblies, tallies, and
   energies, and performs machine learning on the samples via the following
   three steps:

       1) Principal Component Analysis (PCA) on the feature vectors.
       2) KMeans clustering of the PCA-transformed feature vectors
       3) Fits SVR models for the data within each cluster

   The script then predicts the target value (tally value after 1000 batches)
   for each training and test sample and compares it to the reference target
   value to compute the Root Mean Square (RMS) errors for training and 
   testing data. The plots of the RMS errors are overlaid with the Monte Carlo 
   RMS errors in data/targets-batch-rms.h5 and are saved to process/rms-plots/.
'''

import math
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
from cluster import cluster

from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split


################################################################################
##################################    Parameters   #############################
################################################################################

# Number of PCA components
num_components = 3

# Number of clusters to find
num_clusters = 6

# SVR kernel type and parameters
kernel = 'rbf'
C = 1e3
gamma = 0.1


################################################################################
################################    Data Extraction   ##########################
################################################################################

# Create a file handle for the samples file
assemblies = ['Fuel-1.6wo-CRD',
              'Fuel-2.4wo-16BA-grid-56',
              'Fuel-3.1wo-instr-16BA-grid-17']

batches = [10,50,100,200,300,400,500,600,700,800,900,1000]
energies = ['Low Energy', 'High Energy']
tallies = ['Tot. XS', 'Abs. XS', 'Fiss. XS', 'NuFiss. XS']

# Open a handle to the HDF5 file with the Monte Carlo RMS errors for each batch
rms_ref = h5.File('data/target-batch-rms.h5', 'r')


# Iterate over each assembly type
for assembly in assemblies:

    print assembly

    # Open the HDF5 file for access to this assembly's Monte Carlo sample data
    sample_file = h5.File('data/' + assembly + '-samples.h5', 'r')

    # Loop over each tally type
    for tally in tallies:

        print '  ' + tally

        # Initialize a Matplotlib figure for the RMS error vs. batches
        fig = plt.figure()

        # Iterate over energies (Low, High)
        for energy in energies:

            print '    ' + energy

            # Plot the RMS error from Monte Carlo for this tally/energy
            plt.semilogy(rms_ref['Batches'], 
                         rms_ref[assembly][energy][tally][...], linewidth=2)

            # Initialize an array for the SVR RMS error for this tally/energy
            rms = np.zeros(len(batches))

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

                #### Split the data
                split = .33
                training = int((1-split)*len(X))
                testing = int(split*len(X))
                X_train, X_test, y_train, y_test = train_test_split(X, y, \
                                                            test_size=split, \
                                                            random_state=10)

 
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
                X_test = cluster_model.apply_pca_model(X_test)
                X_train = cluster_model.apply_pca_model(X_train)


                ################################################################
                #######################    SVR REGRESSION   ####################
                ################################################################

                # Initialize an empty dictionary to contain SVR models
                # for each cluster, indexed by cluster ID
                models = {}

                # Get the cluster IDs for each training sample
                #     ie, 0 - cluster 0, 1 - cluster 1, ...
                indices = cluster_model.clusterize(X_train)

                # Loop over each cluster and train a model for it's samples
                for c in range(num_clusters):
                    
                    # Extract features/targets for this cluster's samples
                    features = X_train[indices[c],:]
                    targets = y_train[indices[c]]
                    
                    # Fit an SVR model on this cluster's samples
                    models[c] = SVR(kernel=kernel, C=C, gamma=gamma)
                    models[c].fit(features, targets)


                ################################################################
                ###################    CLUSTER/SVR PREDICTION   ################
                ################################################################

                ##########################  TRAINING  ##########################

                # Initialize an empty array for the predicted target values
                y_train_predict = np.zeros(len(y_train))

                # Loop over each cluster and make predictions for each 
                # training sample
                for c in range(num_clusters):

                    # Extract features for this cluster's samples
                    features = X_train[indices[c],:]
                    
                    # Store the predicted values for this cluster's samples
                    y_train_predict[indices[c]] = models[c].predict(features)


                ###########################  TESTING  ##########################
                
                # Get the cluster IDs for each test sample
                #     ie, 0 - cluster 0, 1 - cluster 1, ...
                indices = cluster_model.clusterize(X_test)

                # Initialize an empty array for the predicted target values
                y_test_predict = np.zeros(len(y_test))

                # Loop over each cluster and make predictions for each 
                # test sample
                for c in range(num_clusters):

                    # Extract features for this cluster's samples
                    features = X_test[indices[c]]

                    # Store the predicted values for this cluster's samples
                    y_test_predict[indices[c]] = models[c].predict(features)
    

                ################################################################
                ##################    TRAINING/TESTING ERROR   #################
                ################################################################

                # Compute the RMS error for the training and test samples
                train_error = np.power(y_train_predict - y_train, 2)
                test_error = np.power(y_test_predict - y_test, 2)
                train_error = np.sqrt(np.mean(train_error))
                test_error = np.sqrt(np.mean(test_error))

                # Store the RMS error for this 
                rms[index[0]] = test_error
                
                # Print the results for this case to the screen
                print '        Batch %d \t train err. %.3g \t test err. %0.3g' \
                        % (index[1] , train_error, test_error)

            # Plot the SVR RMS for this tally, energy
            plt.semilogy(batches, rms, linewidth=2)

        # Annotate the plot
        plt.ylabel('Root Mean Squared Error')
        plt.xlabel('Batch #')
        plt.title(assembly + ' ' + tally + ' RMS')
        plt.legend(energies)
        plt.grid(b=True, which='major', color='b', linestyle='-')
        plt.grid(b=True, which='minor', color='r', linestyle='--')
        plt.legend(['Low Energy - Actual', 'Low Energy - RBF', 
                   'High Energy - Actual', 'High Energy - RBF'])

        

        # Save the plot
        filename = tally.replace('.', '').replace(' ', '-').lower()
        filename = 'process/rms-plots/' + assembly + '/' + filename + '.png'
        plt.savefig(filename)
