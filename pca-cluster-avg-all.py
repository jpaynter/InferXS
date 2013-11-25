'''Performs PCA, clustering and SVR regression for all datasets.

   Author: William Boyd
   Date: 11/23/2013

   Usage: python pca-cluster-avg-all.py

   This script is an extension of cluster-svr.py to include PCA dimensionality
   reduction prior to clustering. The data is stored as 18-dimensional feature
   vectors for each sample with a single target value. The feature descriptions
   are given in process/samples.py. The target values for each sample are
   the converged (after 1000 batches) pinwise tallies (across the entire 3x3
   mesh) for each reaction rate and energy.

   This script iterates through all of the fuel assemblies, tallies, and
   energies, and performs machine learning on the samples via the following
   three steps:

       1) Principal Component Analysis (PCA) on the feature vectors.
       2) KMeans clustering of the PCA-transformed feature vectors
       3) Fits KMeans average cluster models for the data within each cluster

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
##################################    PARAMETERS   #############################
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
#################################   DATA EXTRACTION  ###########################
################################################################################

# Create a file handle for the samples file
assemblies = ['Fuel-1.6wo-CRD']
#              'Fuel-2.4wo-16BA-grid-56',
#              'Fuel-3.1wo-instr-16BA-grid-17']

batches = [10,50,100,200,300,400,500,600,700,800,900,1000]
energies = ['Low Energy']
tallies = ['Tot. XS'] #, 'Abs. XS', 'Fiss. XS', 'NuFiss. XS']

# Open a handle to the HDF5 file with the Monte Carlo RMS errors for each batch
rms_ref = h5.File('data/target-batch-rms.h5', 'r')



################################################################################
############################   MODEL FITTING/PREDICTION  #######################
################################################################################

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
            rms_model1 = np.zeros(len(batches))
            rms_model2 = np.zeros(len(batches))

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
                X_test_pca = cluster_model.apply_pca_model(X_test)
                X_train_pca = cluster_model.apply_pca_model(X_train)


                ################################################################
                #######################    SVR REGRESSION   ####################
                ################################################################

                # Fit an averaging model for samples within each cluster
                target_avg_model = cluster.AveragingModel(cluster_model)
                feature_avg_model = cluster.AveragingModel(cluster_model)
                target_avg_model.build_model(y_train)
                feature_avg_model.build_model(X_train[:,0:9])


                ################################################################
                ###################    CLUSTER/SVR PREDICTION   ################
                ################################################################

                ##########################  TRAINING  ##########################

                # Predict the target values for each training sample
                y_train_predict_model1 = target_avg_model.predict(X_train_pca)
                y_train_predict_model2 = feature_avg_model.predict(X_train_pca)

                ###########################  TESTING  ##########################
                
                # Predict the target values for each test sample
                y_test_predict_model1 = target_avg_model.predict(X_test_pca)
                y_test_predict_model2 = feature_avg_model.predict(X_test_pca)
    

                ################################################################
                ##################    TRAINING/TESTING ERROR   #################
                ################################################################

                # Compute the RMS error for the training and test samples
                train_error_model1 = np.power(y_train_predict_model1-y_train, 2)
                test_error_model1 = np.power(y_test_predict_model1-y_test, 2)
                train_error_model1 = np.sqrt(np.mean(train_error_model1))
                test_error_model1 = np.sqrt(np.mean(test_error_model1))

                train_error_model2 = np.power(y_train_predict_model2-y_train, 2)
                test_error_model2 = np.power(y_test_predict_model2 - y_test, 2)
                train_error_model2 = np.sqrt(np.mean(train_error_model2))
                test_error_model2 = np.sqrt(np.mean(test_error_model2))

                # Store the RMS error for this 
                rms_model1[index[0]] = test_error_model1
                rms_model2[index[0]] = test_error_model2
                
                # Print the results for this case to the screen
                print '        Batch %d \t model-1 test err. %.3g \t model-2 test err. %0.3g' \
                        % (index[1] , test_error_model1, test_error_model2)

            # Plot the SVR RMS for this tally, energy
            plt.semilogy(batches, rms_model1, linewidth=2)
            plt.semilogy(batches, rms_model2, linewidth=2)

        # Annotate the plot
        plt.ylabel('Root Mean Squared Error')
        plt.xlabel('Batch #')
        plt.title(assembly + ' ' + tally + ' RMS')
        plt.legend(energies)
        plt.grid(b=True, which='major', color='b', linestyle='-')
        plt.grid(b=True, which='minor', color='r', linestyle='--')
        plt.legend(['Low Energy - Actual', 'Low Energy - Model 1', \
                    'Low Energy - Model 2', 'High Energy - Actual', \
                    'High Energy - Model1', 'High Energy - Model 2'])

        # Save the plot
        filename = tally.replace('.', '').replace(' ', '-').lower()
        filename = 'process/rms-plots/' + assembly + '/' + filename + '.png'
        plt.savefig(filename)
