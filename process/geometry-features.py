'''
'''

import h5py as h5
import numpy as np
import os


os.system('rm ../data/geometry-features.h5')

# Fuel - 0
# Water - 1
# Burnable absorber - 2
# Fission chamber - 3

materials = {}


################################################################################
###############################   Fuel-1.6wo-CRD   #############################
################################################################################

materials['Fuel-1.6wo-CRD'] = np.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,1,0,0,1,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0],
        [0,0,0,0,0,1,0,0,1,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])


################################################################################
###########################   Fuel-2.4wo-16BA-grid-56   ########################
################################################################################

materials['Fuel-2.4wo-16BA-grid-56'] = np.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,2,0,0,2,0,0,2,0,0,0,0,0],
        [0,0,0,2,0,0,0,0,0,0,0,0,0,2,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,0,0,1,0,0,1,0,0,1,0,0,2,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,0,0,1,0,0,3,0,0,1,0,0,2,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,0,0,1,0,0,1,0,0,1,0,0,2,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,2,0,0,0,0,0,0,0,0,0,2,0,0,0],
        [0,0,0,0,0,2,0,0,2,0,0,2,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])


################################################################################
########################   Fuel-3.1wo-instr-16BA-grid-17   #####################
################################################################################

materials['Fuel-3.1wo-instr-16BA-grid-17'] = np.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,2,0,0,2,0,0,2,0,0,0,0,0],
        [0,0,0,2,0,0,0,0,0,0,0,0,0,2,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,0,0,1,0,0,1,0,0,1,0,0,2,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,0,0,1,0,0,3,0,0,1,0,0,2,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,0,0,1,0,0,1,0,0,1,0,0,2,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,2,0,0,0,0,0,0,0,0,0,2,0,0,0],
        [0,0,0,0,0,2,0,0,2,0,0,2,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])


f = h5.File('../data/geometry-features.h5', 'w')


# We have three different types of nuclear fuel assemblies (17 x 17 fuel pins)
assemblies = ['Fuel-1.6wo-CRD', \
              'Fuel-2.4wo-16BA-grid-56', \
              'Fuel-3.1wo-instr-16BA-grid-17']

for assembly in assemblies:
    new_features = np.zeros((17*17,9))

    sample_cnt = 0

    for x in range(17):
        for y in range(17):

            tot_mask = [(x-1,y-1), (x,y-1), (x+1,y-1), \
                        (x-1,y), (x,y), (x+1,y), \
                        (x-1,y+1), (x,y+1), (x+1,y+1)]

            face_mask = [(x,y-1), (x-1,y), (x+1,y), (x,y+1)]

            corner_mask = [(x-1,y-1), (x+1,y-1), (x-1,y+1), (x+1,y+1)]

            # Number of adjacent water cells (corners and faces)
            for i in enumerate(tot_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 1:
                    new_features[sample_cnt, 0] += 1

            # Number of adjacent water cells (faces)
            for i in enumerate(face_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 1:
                    new_features[sample_cnt, 1] += 1

            # Number of adjacent water cells (corners)
            for i in enumerate(corner_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 1:
                    new_features[sample_cnt, 2] += 1


            # Number of adjacent burnable asbosrber cells (corners and faces)
            for i in enumerate(tot_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 2:
                    new_features[sample_cnt, 3] += 1

            # Number of adjacent burnable absorber cells (faces)
            for i in enumerate(face_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 2:
                    new_features[sample_cnt, 4] += 1

            # Number of adjacent burnable absorber cells (corners)
            for i in enumerate(corner_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 2:
                    new_features[sample_cnt, 5] += 1


            # Number of adjacent fission chamber cells (corners and faces)
            for i in enumerate(tot_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 3:
                    new_features[sample_cnt, 6] += 1

            # Number of adjacent fission chamber cells (faces)
            for i in enumerate(face_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 3:
                    new_features[sample_cnt, 7] += 1

            # Number of adjacent fission chamber cells (corners)
            for i in enumerate(corner_mask):
                if i[1][0] < 0 or i[1][0] > 16 or i[1][1] < 0 or i[1][1] > 16:
                    continue
                if materials[assembly][i[1][0], i[1][1]] == 3:
                    new_features[sample_cnt, 8] += 1

            sample_cnt +=1

    f.create_dataset(assembly, data=new_features)
