'''This is an example of how to build a dataset.

   Author: William Boyd
   Date: 11/5/2013

   Usage: python example.py

   This script provides an example of how to index into 'samples.h5' and 
   retrieve one of many possible datasets of targets and feature vectors.
'''

import h5py as h5
import numpy as np

################################################################################
################################    Data Parameters   ##########################
################################################################################

# Create a file handle for the samples file
# 3 Assembly types are available:
#    Fuel-1.6wo-CRD
#    Fuel-2.4wo-16BA-grid-56
#    Fuel-3.1wo-instr-16BA-grid-17
sample_file = h5.File('data/Fuel-1.6wo-CRD-samples.h5', 'r')

# Different batch means are available:
#     10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
batch = 'Batch-200'

# Two energies are available:
#     Low Energy, High Energy
energy = 'Low Energy'

# Different tally types are available:
#    Flux
#    Tot. RXN Rate, Abs. RXN Rate, Fiss. RXN Rate, NuFiss RXN Rate
#    Tot. XS, Abs. XS, Fiss. XS, NuFiss. XS
tally = 'Tot. XS'



################################################################################
################################    Data Extraction   ##########################
################################################################################

# Get target regression values for each sample
targets = sample_file[batch][energy][tally]['Targets'][...]

# Get the feature vectors for each sample
features = sample_file[batch][energy][tally]['Features'][...]



################################################################################
##################################    Data Report   ############################
################################################################################

num_samples = len(targets)
num_features = features.shape[1]
print 'There are %d samples with %d features each' % (num_samples, num_features)
