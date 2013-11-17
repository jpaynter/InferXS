'''A cluster class to encapsulate PCA and clustering algorithms from sklearn.

   Author: William Boyd
   Date: 11/11/2013

   Usage: Prepend to Python script - "from cluster import cluster"

   This script iterates through all of the fuel assemblies, tallies, and
   energies, and performs machine learning on the samples via the following
   three steps:

'''

import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA



class Cluster:
    '''The Cluster class.

       This class encapsulates data that is to be clustered using sklearn.
    '''
    
    def __init__(self, X):
        '''Initialize the Cluster class.
        
           Takes in a matrix of feature vectors X, scales them and stores
           them as a class attribute. All other class attributes are 
           initialized to default values.
        '''

        self._X = scale(X)
        self._num_components = self._X.shape[1]
        self._model = None
        self._num_clusters = 0

        self._num_pca_components = 0
        self._pca_model = None


    ############################################################################
    ##################################  Clustering  ############################
    ############################################################################

    def build_clusters(self, method='kmeans', num_clusters=5):
        '''Builds a clustering model.

           This method searches for the best set of num_clusters clusters 
           within the dataset.

           NOTE: Currently this method only supports kmeans clustering, but
                 other sklearn clustering algorithms could easily be 
                 implemented here.
        '''

        self._num_clusters = num_clusters

        
        if method.lower() == 'kmeans':
            self._model = KMeans(init='k-means++', n_clusters=self._num_clusters, n_init=10)
            self._model.fit(self._X)

        # TODO: Implement other clustering algorithms HERE

        else:
            raise Exception('Clustering method ' + method + ' is not supported')


    def predict_cluster_index(self, x):
        '''Predicts which cluster a sample is within.

           The method returns the cluster ID/index for the sample, ie,
           0 - cluster 0, 1 - cluster 1, ...
        '''

        if self._model is None:
            raise Exception('Cannot make clustering predictions until' + \
                            'the buildClusters method is called')
        else:
            self._model.predict(x)        


    def clusterize(self, X):
        '''Returns an array of cluster IDs corresponding to each sample.

           This method iterates over the feature vectors in X and constructs
           a dictionary of indexed by cluster ID with boolean values 
           (True/False) for each sample corresponding to whether it is in 
           that cluster.
        '''
        
        if self._model is None:
            raise Exception('Cannot clusterize until' + \
                            'the buildClusters method is called')

        # Initialize a dictionary to contain the feature vectors for all 
        # samples in each cluster, indexed by cluster 
        clusters = {}

        # If we are using a PCA model, transform the input data into
        # the space spanned by the singular vectors
        if self._pca_model is not None:

            # If the input data is not in the PCA singular vector space
            if X.shape[1] == self._num_components:
                X = self._pca_model.transform(X)

            # If the input data does not have the same dimensionality as the
            # PCA components, then we cannot cluster within it
            elif X.shape[1] != self._num_pca_components:
                raise Exception('Unable to clusterize input features since ' + \
                                 'it is not in either the space defined by ' + \
                                 'the original or PCA feature vectors')

        # Fill the array with a "mask" index array - an array with the
        # indices for each sample corresponding to cluster i
        for i in range(self._num_clusters):
            clusters[i] = self._model.predict(X) == i

        return clusters

    ############################################################################
    #####################################  PCA  ################################
    ############################################################################

    def build_pca_model(self, num_components=3):
        '''Transforms the feature vectors into singular vector space.

           This method uses's sklearn's Principal Component Analysis
           routine to compute the Singular Value Decomposition of the
           feature vector matrix X. The method then projects the feature
           vectors into the space defined by first num_components principal
           vectors (those vectors that describe most of the variance of the
           features).
        '''

        self._num_pca_components = num_components
        self._pca_model = PCA(n_components=self._num_pca_components)
        self._X = self._pca_model.fit_transform(self._X)

    
    def apply_pca_model(self, X):
        '''Returns the feature vector projections into PCA space.

           Takes in a matrix of feature vectors and transforms them into
           the space defined by the PCA model used by this cluster object.
        '''
        
        
        if self._pca_model is None:
            raise Exception('Unable to apply a PCA model to inputs since ' + \
                                'a PCA model has not yet been built')

        return self._pca_model.transform(scale(X))


    def get_pca_variance_ratios(self):
        '''Returns the variance ratios for each PCA component.

           The variance ratio is the percentage of the total variance
           in the feature vector matrix that can be explained (spanned) by
           the corresponding singular vector.
        '''
        
        if self._pca_model is None:
            raise Exception('Unable to get PCA variance ratios since ' + \
                                'a PCA model has not yet been built')

        return self._pca_model.explained_variance_ratios


    ############################################################################
    ############################  Clustering  Metrics  #########################
    ############################################################################

    def get_inertia(self):
        '''Returns the inertia for the clustering model.

           The inertia is a metric for evaluating the clustering model.
           The inertia is bounded below by zero and lower is "better."

           NOTE: The concept of inertia in the context of clustering is
                 discussed briefly in sklearn's online documentation here:
                 http://tinyurl.com/kzfat44
        '''

        if self._model is None:
            raise Exception('Cannot compute inertia until' + \
                            'the buildClusters method is called')

        return self._model.inertia_


    def get_silhouette(self):
        '''Returns the silhouette coefficient for the clustering model.

           The silhouette coefficient is a metric for evaluating how well
           defined are the cluster's in one's model. The silhouette coefficient
           is bounded between -1 and 1. Scores near zero indicate overlapping
           clusters while higher scores indicated well separated clusters.

           NOTE: The concept of silhouette in the context of clustering is
                 discussed briefly in sklearn's online documentation here:
                 http://tinyurl.com/l3en5mc
        '''

        if self._model is None:
            raise Exception('Cannot compute silhouette score until' + \
                            'the buildClusters method is called')

        return metrics.silhouette_score(self._X, self._model.labels_,
                                        metric='euclidean',
                                        sample_size=self._X.shape[0])


    ############################################################################
    #################################  Plotting  ###############################
    ############################################################################

    def plot_clusters_1D(self, feature=0):
        '''Plots histograms for each cluster of data along one feature axis.

           Creates num_clusters of histograms and colors each one according
           to the cluster ID. The plot of overlaid histograms is displayed
           to the screen.

           The user may input which feature to use for generating the
           histograms (default is 0).
        '''

        if feature < -1 or feature > self._X.shape[1]:
            raise Exception('Unable to plot clusters in 1D since the ' + \
                                'feature selected is not within the ' + \
                                'scope of the data') 

        # Initialize a new Matplotlib figure handle
        fig = plt.figure()

        # Initialize a list for the legend entries
        legend = []

        # Find the cluster IDs for each sample
        indices = self.clusterize(self._X)

        # Iterate over each cluster and generate and plot a histogram for
        # all of its samples
        for i in range(self._num_clusters):
            data = self._X[indices[i], feature]
            n, bins, patches = plt.hist(data, 20, histtype='step')
            legend.append('Cluster-'+str(i))

        # Annotate the plot and display it
        plt.xlabel('Feature-' + str(feature))
        plt.ylabel('Sample Counts')
        plt.title('Histogram of Clusters')
        plt.legend(legend)
        plt.show()


    def plot_clusters_2D(self, features=[0,1]):
        '''Plots clusters of samples in 2D feature space.

           Projects each sample into 2D space defined by two of the features
           and colors each point according to its cluster. The user may 
           select which features to use with the "features" parameter (the
           defaults are 0 and 1).
        '''

        # Initialize a new Matplotlib figure handle
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Initialize a list for the legend entries
        legend = []

        # Find the cluster IDs for each sample
        indices = self.clusterize(self._X)

        # Create a colormap for the clusters
        import matplotlib.cm as cm
        colors = cm.rainbow(np.linspace(0, 1, self._num_clusters))

        # Iterate over each cluster and plot the features for each of
        # its samples
        for i in range(self._num_clusters):
            x = self._X[indices[i], features[0]]
            y = self._X[indices[i], features[1]]
            ax.scatter(x, y, c=colors[i], s=25)
            legend.append('Cluster-'+str(i))

        # Annotate the plot and display it
        ax.set_xlabel('Feature-' + str(features[0]))
        ax.set_ylabel('Feature-' + str(features[1]))
        plt.title('Clusters in 2D')
        plt.legend(legend)
        plt.show()
        

    def plot_clusters_3D(self, features=[0,1,2]):
        '''Plots clusters of samples in 3D feature space.

           Projects each sample into 3D space defined by three of the features
           and colors each point according to its cluster. The user may 
           select which features to use with the "features" parameter (the
           defaults are 0, 1 and 2).
        '''

        # Initialize a new Matplotlib figure handle
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Initialize a list for the legend entries
        legend = []

        # Find the cluster IDs for each sample
        indices = self.clusterize(self._X)

        # Create a colormap for the clusters
        import matplotlib.cm as cm
        colors = cm.rainbow(np.linspace(0, 1, self._num_clusters))

        # Iterate over each cluster and plot the features for each of
        # its samples
        for i in range(self._num_clusters):
            x = self._X[indices[i], features[0]]
            y = self._X[indices[i], features[1]]
            z = self._X[indices[i], features[2]]
            ax.scatter(x, y, z, c=colors[i], s=25)
            legend.append('Cluster-'+str(i))

        # Annotate the plot and display it
        ax.set_xlabel('Feature-' + str(features[0]))
        ax.set_ylabel('Feature-' + str(features[1]))
        ax.set_zlabel('Feature-' + str(features[2]))
        plt.title('Clusters in 3D')
        plt.legend(legend)
        plt.show()
