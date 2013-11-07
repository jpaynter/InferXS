from statepoint import StatePoint
import numpy as np
import matplotlib.pyplot as plt
import time

# User parameters
sleep_interval = 0    # seconds
batch_start = 260
batch_stop = 1250
batch_interval = 10

directory = '../openmc-input/Fuel-1.6wo-CRD/pinwise/'
#directory = '../openmc-input/Fuel-2.4wo-16BA-grid-56/pinwise/'
#directory = '../openmc-input/Fuel-3.1wo-instr-16BA-grid-17/pinwise/'

#directory = '../openmc-input/Fuel-1.6wo-CRD/three-by-three/500_per_batch/'
#directory = '../openmc-input/Fuel-2.4wo-16BA-grid-56/three-by-three/500_per_batch/'
#directory = '../openmc-input/Fuel-3.1wo-instr-16BA-grid-17/three-by-three/500_per_batch/'

# score options are 'fission' 'nu-fission' 'absorption' 'flux' 'total'
score1 = 'fission'
score2 = 'total'

# energy options are 1 or 2
energy = 2         
num_groups = 2

# Mesh is 17x17 or 51x51
mesh_x_dim = 17
mesh_y_dim = 17


################################################################################
# Create plot of initial data to start animation
################################################################################

# Instantiate statepoint for the first batch of tally data
print directory + 'statepoint.' + str(batch_start) + '.h5'
sp = StatePoint(directory + 'statepoint.' + str(batch_start) + '.h5')
sp.read_results()
tallyid = 1
tally1_data = sp.extract_results(tallyid, score1)
tally2_data = sp.extract_results(tallyid, score2)

tally1_means = tally1_data['mean']
tally1_std_dev = np.nan_to_num(tally1_data['CI95'])
tally2_means = tally2_data['mean']
tally2_std_dev = np.nan_to_num(tally2_data['CI95'])

# Reshape to grid with energy as third index
tally1_means = np.reshape(tally1_means,(mesh_x_dim, mesh_y_dim, num_groups))
tally1_std_dev = np.reshape(tally1_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
tally2_means = np.reshape(tally2_means,(mesh_x_dim, mesh_y_dim, num_groups))
tally2_std_dev = np.reshape(tally2_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))

# Instantiate a PyPlot figure and turn on Matplotlib's interactive mode
fig = plt.figure(num=1,dpi=160)
fig.set_size_inches(18,10)
plt.ion()

# Plot tally1 in top left corner
plt.subplot(121)
img = plt.imshow(tally1_means[:,:,energy-1], interpolation='nearest', animated=True)
plt.colorbar()
plt.title(str.capitalize(score1))

# Plot tally2 in top right corner
plt.subplot(122)
img = plt.imshow(tally2_means[:,:,energy-1], interpolation='nearest', animated=True)
plt.colorbar()
plt.title(str.capitalize(score2))

# Plot tally1 std dev in lower left corner
plt.subplot(223)
batches = [batch_start]
std_dev_tally1 = [np.max(tally1_std_dev[:,:,energy-1])]
std_dev_tally1_ideal = [std_dev_tally1[0]]
plt.plot(batches, std_dev_tally1, animated=True, color='blue')
plt.plot(batches, std_dev_tally1_ideal, animated=True, color='green')
plt.xlabel('Batch #')
plt.ylabel('Std. Dev')
plt.legend(['Sample', 'Ideal'])
plt.title(str.capitalize(score1 + 'Std. Dev.'))

# Plot tally2 std dev in lower right corner
plt.subplot(224)
std_dev_tally2 = [np.max(tally2_std_dev[:,:,energy-1])]
std_dev_tally2_ideal = [std_dev_tally2[0]]
plt.plot(batches, std_dev_tally2, animated=True, color='blue')
plt.plot(batches, std_dev_tally2_ideal, animated=True, color='green')
plt.xlabel('Batch #')
plt.ylabel('Std. Dev.')
plt.legend(['Sample', 'Ideal'])
plt.title(str.capitalize(score1 + 'Std. Dev.'))

# Draw all of the subplots and sleep
plt.draw()
time.sleep(sleep_interval)

# Iterate over all batches
for batch in range(batch_start+batch_interval, batch_stop+batch_interval, batch_interval):
    
    # Instantiate statepoint for the this batch of tally data
    sp = StatePoint(directory+'statepoint.' + str(batch) + '.h5')
    sp.read_results()
    tallyid = 1
    tally1_data = sp.extract_results(tallyid, score1)
    tally2_data = sp.extract_results(tallyid, score2)

    tally1_means = tally1_data['mean']
    tally1_std_dev = np.nan_to_num(tally1_data['CI95'])
    tally2_means = tally2_data['mean']
    tally2_std_dev = np.nan_to_num(tally2_data['CI95'])

    # Reshape to grid with energy as third index
    tally1_means = np.reshape(tally1_means,(mesh_x_dim, mesh_y_dim, num_groups))
    tally1_std_dev = np.reshape(tally1_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
    tally2_means = np.reshape(tally2_means,(mesh_x_dim, mesh_y_dim, num_groups))
    tally2_std_dev = np.reshape(tally2_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
    
    # Plot tally1 in top left corner
    plt.subplot(221)
    plt.imshow(tally1_means[:,:,energy-1], interpolation='nearest')
    plt.title(str.capitalize(score1))

    # Plot tally2 in top right corner
    plt.subplot(222)
    plt.imshow(tally2_means[:,:,energy-1], interpolation='nearest')
    plt.title(str.capitalize(score2))

    # Plot tally1 std dev in lower left corner
    plt.subplot(223)
    batches.append(batch)
    std_dev_tally1.append(np.max(tally1_std_dev[:,:,energy-1]))
    std_dev_tally1_ideal.append(std_dev_tally1[0] / np.sqrt(batch-batch_start))
    plt.plot(batches, std_dev_tally1, color='blue')
    plt.plot(batches, std_dev_tally1_ideal, color='green')
    plt.title(str.capitalize(score1 + 'Std. Dev.'))

    # Plot tally2 std dev in lower right corner
    plt.subplot(224)
    std_dev_tally2.append(np.max(tally2_std_dev[:,:,energy-1]))
    std_dev_tally2_ideal.append(std_dev_tally2[0] / np.sqrt(batch-batch_start))
    plt.plot(batches, std_dev_tally2, color='blue')
    plt.plot(batches, std_dev_tally2_ideal, color='green')
    plt.title(str.capitalize(score2 + ' Std. Dev.'))

    # Update all of the subplots and sleep
    plt.draw()
    time.sleep(sleep_interval)
