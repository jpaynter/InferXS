from statepoint import StatePoint
import numpy as np
import matplotlib.pyplot as plt
import time

# User parameters
sleep_interval = 0    # seconds
batch_start = 20
batch_stop = 500
batch_interval = 10

score = 'flux'
mesh_x_dim = 100
mesh_y_dim = 100
num_groups = 2

# Plot the convergence of each tally variance (overlaid with 1/sqrt(n))

# Fission / nu-fission rates will have zeroes in the water - hence NaNs for std. dev. 


################################################################################
# Create plot of initial data to start animation
################################################################################

# Instantiate statepoint for the first batch of tally data
sp = StatePoint('pincell/statepoint.' + str(batch_start) + '.h5')
sp.read_results()
tallyid = 1
data = sp.extract_results(tallyid, score)
means = data['mean']
ci95 = data['CI95']

# Reshape to grid with energy as third index
means = np.reshape(means,(100,100,2))
ci95 = np.reshape(ci95,(100,100,2))

# Instantiate a PyPlot figure and turn on Matplotlib's interactive mode
fig = plt.figure(1)
plt.ion()

# Plot fast flux tally mesh in top left corner
plt.subplot(221)
img = plt.imshow(means[:,:,0], interpolation='nearest', animated=True)
plt.title('Fast Flux')

# Plot thermal flux tally mesh in top right corner
plt.subplot(222)
img = plt.imshow(means[:,:,1], interpolation='nearest', animated=True)
plt.title('Thermal Flux')

# Plot fast flux std dev in lower left corner
plt.subplot(223)
batches = [10]
std_dev_fast = [np.max(ci95[:,:,0])]
std_dev_fast_ideal = [std_dev_fast[0]]
std_dev_fast_line, = plt.plot(batches, std_dev_fast, animated=True, color='Blue')
std_dev_fast_ideal_line, = plt.plot(batches, std_dev_fast_ideal, animated=True, color='Green')
plt.xlabel('Batch #')
plt.ylabel('CI95')
plt.legend(['Sample', 'Ideal'])
plt.title('Fast Flux Uncertainty')

# Plot therm flux std dev in lower right corner
plt.subplot(224)
std_dev_therm = [np.max(ci95[:,:,1])]
std_dev_therm_ideal = [std_dev_therm[0]]
std_dev_therm_line, = plt.plot(batches, std_dev_therm, animated=True, color='blue')
std_dev_therm_ideal_line, = plt.plot(batches, std_dev_therm_ideal, animated=True, color='green')
plt.xlabel('Batch #')
plt.ylabel('Std. Dev.')
plt.legend(['Sample', 'Ideal'])
plt.title('Thermal Flux Uncertainty')

# Draw all of the subplots and sleep
plt.draw()
time.sleep(sleep_interval)

# Iterate over all batches
for batch in range(batch_start, batch_stop+batch_interval, batch_interval):

    
    # Instantiate statepoint for the this batch of tally data
    sp = StatePoint('pincell/statepoint.' + str(batch) + '.h5')
    sp.read_results()
    tallyid = 1
    data = sp.extract_results(tallyid, score)
    means = data['mean']
    ci95 = data['CI95']

    # Reshape to grid with energy as third index
    means = np.reshape(means,(100,100,2))
    ci95 = np.reshape(ci95,(100,100,2))

    
    # Plot fast flux tally mesh in top left corner
    plt.subplot(221)
    plt.imshow(means[:,:,0], interpolation='nearest')

    # Plot thermal flux tally mesh in top right corner
    plt.subplot(222)
    plt.imshow(means[:,:,1], interpolation='nearest')

    # Plot fast flux std dev in lower left corner
    plt.subplot(223)
    batches.append(batch)
    std_dev_fast.append(np.max(ci95[:,:,0]))
    std_dev_fast_ideal.append(std_dev_fast[0] / np.sqrt(batch))
    plt.plot(batches, std_dev_fast, color='blue')
    plt.plot(batches, std_dev_fast_ideal, color='green')

    # Plot therm flux std dev in lower right corner
    plt.subplot(224)
    std_dev_therm.append(np.max(ci95[:,:,1]))
    std_dev_therm_ideal.append(std_dev_therm[0] / np.sqrt(batch))
    plt.plot(batches, std_dev_therm, color='blue')
    plt.plot(batches, std_dev_therm_ideal, color='green')

    # Update all of the subplots and sleep
    plt.draw()
    time.sleep(sleep_interval)
