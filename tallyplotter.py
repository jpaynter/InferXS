from statepoint import StatePoint
import numpy as np
import matplotlib.pyplot as plt
import time

# User parameters
sleep_interval = 0.5    # seconds
batch_start = 260
batch_stop = 1000
batch_interval = 10

directory = 'Fuel-1.6wo-CRD/'

score1 = 'nu-fission'
score2 = 'absorption'
energy = 1
mesh_x_dim = 17
mesh_y_dim = 17
num_groups = 2


################################################################################
# Create plot of initial data to start animation
################################################################################

# Instantiate statepoint for the first batch of tally data
sp = StatePoint(directory + 'statepoint.' + str(batch_start) + '.h5')
sp.read_results()
tallyid = 1
tally1_data = sp.extract_results(tallyid, score1)
tally2_data = sp.extract_results(tallyid, score2)

tally1_means = flux_data['mean']
tally1_std_dev = np.nan_to_num(flux_data['CI95'])
tally2_means = nu_fiss_data['mean']
tally2_std_dev = np.nan_to_num(nu_fiss_data['CI95'])

# Reshape to grid with energy as third index
tally1_means = np.reshape(flux_means,(mesh_x_dim, mesh_y_dim, num_groups))
tally1_std_dev = np.reshape(flux_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
tally2_means = np.reshape(nu_fiss_means,(mesh_x_dim, mesh_y_dim, num_groups))
tally2_std_dev = np.reshape(nu_fiss_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))

# Instantiate a PyPlot figure and turn on Matplotlib's interactive mode
fig = plt.figure(1)
plt.ion()

# Plot tally1 in top left corner
plt.subplot(121)
img = plt.imshow(tally1_means[:,:,energy-1], interpolation='nearest', animated=True)
plt.colorbar()

# Plot tally2 in top right corner
plt.subplot(122)
img = plt.imshow(tally2_means[:,:,energy-1], interpolation='nearest', animated=True)
plt.colorbar()

# Plot tally1 std dev in lower left corner
plt.subplot(223)
batches = [10]
std_dev_tally1 = [np.max(tally1_std_dev[:,:,group-1])]
std_dev_tally1_ideal = [std_dev_tally1[0]]
plt.plot(batches, std_dev_tally1, animated=True, color='blue')
plt.plot(batches, std_dev_tally1_ideal, animated=True, color='green')
plt.xlabel('Batch #')
plt.ylabel('CI95')
plt.legend(['Sample', 'Ideal'])

# Plot tally2 std dev in lower right corner
plt.subplot(224)
std_dev_tally2 = [np.max(std_dev[:,:,groups-1])]
std_dev_tally2_ideal = [std_dev_therm[0]]
plt.plot(batches, std_dev_tally2, animated=True, color='blue')
plt.plot(batches, std_dev_tally2_ideal, animated=True, color='green')
plt.xlabel('Batch #')
plt.ylabel('Std. Dev.')
plt.legend(['Sample', 'Ideal'])

# Draw all of the subplots and sleep
plt.draw()
time.sleep(sleep_interval)

# Iterate over all batches
for batch in range(batch_start, batch_stop+batch_interval, batch_interval):
    
    # Instantiate statepoint for the this batch of tally data
    sp = StatePoint(directory+'statepoint.' + str(batch) + '.h5')
    sp.read_results()
    tallyid = 1
    tally1_data = sp.extract_results(tallyid, score1)
    tally2_data = sp.extract_results(tallyid, score2)

    tally1_means = flux_data['mean']
    tally2_std_dev = np.nan_to_num(flux_data['CI95'])
    tally1_means = nu_fiss_data['mean']
    tally2_std_dev = np.nan_to_num(nu_fiss_data['CI95'])

    # Reshape to grid with energy as third index
    tally1_means = np.reshape(tally1_means,(mesh_x_dim, mesh_y_dim, num_groups))
    tally1_std_dev = np.reshape(tally1_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
    tally2_means = np.reshape(tally2_means,(mesh_x_dim, mesh_y_dim, num_groups))
    tally2_std_dev = np.reshape(tally2_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
    
    # Plot tally1 in top left corner
    plt.subplot(221)
    plt.imshow(std_dev[:,:,group-1], interpolation='nearest')

    # Plot tally2 in top right corner
    plt.subplot(222)
    plt.imshow(std_dev[:,:,group-1], interpolation='nearest')

    # Plot tally1 std dev in lower left corner
    plt.subplot(223)
    batches.append(batch)
    std_dev_tally1.append(np.max(std_dev_tally1[:,:,group-1]))
    std_dev_tally1_ideal.append(std_dev_tally1[0] / np.sqrt(batch))
    plt.plot(batches, std_dev_tally1, color='blue')
    plt.plot(batches, std_dev_fast_tally1, color='green')

    # Plot tally2 std dev in lower right corner
    plt.subplot(224)
    std_dev_tally2.append(np.max(tally2_std_dev[:,:,group-1]))
    std_dev_tally2_ideal.append(std_dev_tally2[0] / np.sqrt(batch))
    plt.plot(batches, std_dev_tally2, color='blue')
    plt.plot(batches, std_dev_tally2_ideal, color='green')

    # Update all of the subplots and sleep
    plt.draw()
    time.sleep(sleep_interval)
