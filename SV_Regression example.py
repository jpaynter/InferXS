import numpy as np
import pylab as pl
from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split

#### Generate sample data
n = 180
split = .33
testing = int(n*split)
training = int(n*(1-split))
np.random.seed(10)
X = np.sort(5 * np.random.rand(n, 1), axis=0)
y = np.sin(X).ravel()

#### Add noise to targets (every 5th)
print 'data'
y[::5] += 3 * (0.5 - np.random.rand(n/5))

#### Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split, random_state=10)

#### Fit regression model
print 'regression'
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
svr_lin = SVR(kernel='linear', C=1e3)
svr_poly = SVR(kernel='poly', C=1e3, degree=2)

y_train_rbf = svr_rbf.fit(X_train, y_train).predict(X_train)
y_train_lin = svr_lin.fit(X_train, y_train).predict(X_train)
y_train_poly = svr_poly.fit(X_train, y_train).predict(X_train)

#### Make predictions based on the models

y_test_rbf = svr_rbf.predict(X_test)
y_test_lin = svr_lin.predict(X_test)
y_test_poly = svr_poly.predict(X_test)

#### Calculate training and testing error
print 'calc'
error_train_rbf=0
error_train_lin=0
error_train_poly=0
for i in range(training):
    diff_train_rbf = y_train_rbf[i] - y_train[i]
    diff_train_lin = y_train_lin[i] - y_train[i]
    diff_train_poly = y_train_poly[i] - y_train[i]
    error_train_rbf = error_train_rbf + diff_train_rbf*diff_train_rbf
    error_train_lin = error_train_lin + diff_train_lin*diff_train_lin
    error_train_poly = error_train_poly + diff_train_poly*diff_train_poly
error_train_rbf = error_train_rbf/training
error_train_lin = error_train_lin/training
error_train_poly = error_train_poly/training

error_test_rbf=0
error_test_lin=0
error_test_poly=0
for i in range(testing):
    diff_test_rbf = y_test_rbf[i] - y_test[i]
    diff_test_lin = y_test_lin[i] - y_test[i]
    diff_test_poly = y_test_poly[i] - y_test[i]
    error_test_rbf = error_test_rbf + diff_test_rbf*diff_test_rbf
    error_test_lin = error_test_lin + diff_test_lin*diff_test_lin
    error_test_poly = error_test_poly + diff_test_poly*diff_test_poly
error_test_rbf = error_test_rbf/testing
error_test_lin = error_test_lin/testing
error_test_poly = error_test_poly/testing

print 'RBF kernel training error is %f' % (error_train_rbf)
print 'Linear kernel training error is %f' % (error_train_lin)
print 'Polynomial, 2nd degree, training error is %f' % (error_train_poly)

print 'RBF kernel testing error is %f' % (error_test_rbf)
print 'Linear kernel testing error is %f' % (error_test_lin)
print 'Polynomial, 2nd degree, testing error is %f' % (error_test_poly)

#### Plot the results for the training data
print 'training plots'
pl.scatter(X_train, y_train, c='k', label='data')
pl.hold('on')
pl.scatter(X_train, y_train_rbf, c='g', label='RBF model')
pl.scatter(X_train, y_train_lin, c='r', label='Linear model')
pl.scatter(X_train, y_train_poly, c='b', label='Polynomial model')
pl.xlabel('data')
pl.ylabel('target')
pl.title('Support Vector Regression - Training Data')
pl.legend()
pl.show()
pl.hold('off')

# Close it to show the next plot!

#### Plot the results for the testing data
print 'testing plots'
pl.scatter(X_test, y_test, c='k', label='data')
pl.hold('on')
pl.scatter(X_test, y_test_rbf, c='g', label='RBF model')
pl.scatter(X_test, y_test_lin, c='r', label='Linear model')
pl.scatter(X_test, y_test_poly, c='b', label='Polynomial model')
pl.xlabel('data')
pl.ylabel('target')
pl.title('Support Vector Regression - Testing Data')
pl.legend()
pl.show()
