from statepoint import StatePoint
import numpy as np
import matplotlib.pyplot as plt
import time

# User parameters
sleep_interval = 0.5    # seconds
batch_start = 20
batch_stop = 1000
batch_interval = 10

score1 = 'flux'
score2 = 'nu-fission'
mesh_x_dim = 5
mesh_y_dim = 5
num_groups = 2


################################################################################
# Create plot of initial data to start animation
################################################################################

# Instantiate statepoint for the first batch of tally data
sp = StatePoint('pincell/statepoint.' + str(batch_start) + '.h5')
sp.read_results()
tallyid = 1
flux_data = sp.extract_results(tallyid, score1)
nu_fiss_data = sp.extract_results(tallyid, score2)

flux_means = flux_data['mean']
flux_std_dev = flux_data['CI95']
nu_fiss_means = nu_fiss_data['mean']
nu_fiss_std_dev = np.nan_to_num(nu_fiss_data['CI95'])

# Reshape to grid with energy as third index
flux_means = np.reshape(flux_means,(mesh_x_dim, mesh_y_dim, num_groups))
flux_std_dev = np.reshape(flux_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))
nu_fiss_means = np.reshape(nu_fiss_means,(mesh_x_dim, mesh_y_dim, num_groups))
nu_fiss_std_dev = np.reshape(nu_fiss_std_dev,(mesh_x_dim, mesh_y_dim, num_groups))

flux_variance = np.power(flux_std_dev, 2)
nu_fiss_variance = np.power(nu_fiss_std_dev, 2)

means = (nu_fiss_means / flux_means) + (nu_fiss_means / (np.power(flux_means,3))) * flux_variance
variance = (nu_fiss_variance / (np.power(flux_means, 2))) + \
           ((np.power(nu_fiss_means,2) * flux_variance) / (np.power(flux_means, 4)))
variance = np.nan_to_num(variance)
std_dev = np.sqrt(variance)

print 'max std dev = ' + str(np.max(std_dev))
print 'avg std dev = ' + str(np.average(std_dev[np.nonzero(std_dev)]))

# Instantiate a PyPlot figure and turn on Matplotlib's interactive mode
fig = plt.figure(1)
plt.ion()

# Plot fast flux tally mesh in top left corner
plt.subplot(221)
img = plt.imshow(std_dev[:,:,0], interpolation='nearest', animated=True)
plt.title('Fast Flux')
plt.colorbar()

# Plot thermal flux tally mesh in top right corner
plt.subplot(222)
img = plt.imshow(std_dev[:,:,1], interpolation='nearest', animated=True)
plt.title('Thermal Flux')
plt.colorbar()

# Plot fast flux std dev in lower left corner
plt.subplot(223)
batches = [10]
std_dev_fast = [np.max(std_dev[:,:,0])]
std_dev_fast_ideal = [std_dev_fast[0]]
plt.plot(batches, std_dev_fast, animated=True, color='blue')
plt.plot(batches, std_dev_fast_ideal, animated=True, color='green')
plt.xlabel('Batch #')
plt.ylabel('CI95')
plt.legend(['Sample', 'Ideal'])
plt.title('Fast Flux Uncertainty')

# Plot therm flux std dev in lower right corner
plt.subplot(224)
std_dev_therm = [np.max(std_dev[:,:,1])]
std_dev_therm_ideal = [std_dev_therm[0]]
plt.plot(batches, std_dev_therm, animated=True, color='blue')
plt.plot(batches, std_dev_therm_ideal, animated=True, color='green')
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
    flux_data = sp.extract_results(tallyid, score1)
    nu_fiss_data = sp.extract_results(tallyid, score2)

    flux_means = flux_data['mean']
    flux_std_dev = flux_data['CI95']
    nu_fiss_means = nu_fiss_data['mean']
    nu_fiss_std_dev = np.nan_to_num(nu_fiss_data['CI95'])

    flux_variance = np.power(flux_std_dev, 2)
    nu_fiss_variance = np.power(nu_fiss_std_dev, 2)

    means = (nu_fiss_means / flux_means) + (nu_fiss_means / (np.power(flux_means,3))) * flux_variance
    variance = (nu_fiss_variance / (np.power(flux_means, 2))) + \
           ((np.power(nu_fiss_means,2) * flux_variance) / (np.power(flux_means, 4)))
    variance = np.nan_to_num(variance)
    std_dev = np.sqrt(variance)

    print 'max std dev = ' + str(np.max(std_dev))
    print 'avg std dev = ' + str(np.average(std_dev[np.nonzero(std_dev)]))
    print 'max fiss xs = ' + str(np.max(means))
    print 'avg fiss xs = ' + str(np.average(means[np.nonzero(means)]))


    # Reshape to grid with energy as third index
    means = np.reshape(means,(mesh_x_dim,mesh_y_dim,num_groups))
    std_dev = np.reshape(std_dev,(mesh_x_dim,mesh_y_dim,num_groups))
    
    # Plot fast flux tally mesh in top left corner
    plt.subplot(221)
    plt.imshow(std_dev[:,:,0], interpolation='nearest')

    # Plot thermal flux tally mesh in top right corner
    plt.subplot(222)
    plt.imshow(std_dev[:,:,1], interpolation='nearest')

    # Plot fast flux std dev in lower left corner
    plt.subplot(223)
    batches.append(batch)
    std_dev_fast.append(np.max(std_dev[:,:,0]))
    std_dev_fast_ideal.append(std_dev_fast[0] / np.sqrt(batch))
    plt.plot(batches, std_dev_fast, color='blue')
    plt.plot(batches, std_dev_fast_ideal, color='green')

    # Plot therm flux std dev in lower right corner
    plt.subplot(224)
    std_dev_therm.append(np.max(std_dev[:,:,1]))
    std_dev_therm_ideal.append(std_dev_therm[0] / np.sqrt(batch))
    plt.plot(batches, std_dev_therm, color='blue')
    plt.plot(batches, std_dev_therm_ideal, color='green')

    # Update all of the subplots and sleep
    plt.draw()
    time.sleep(sleep_interval)
