#!/usr/bin/env python

"""
Usage example employing Lasagne for digit recognition using the MNIST dataset.

This example is deliberately structured as a long flat file, focusing on how
to use Lasagne, instead of focusing on writing maximally modular and reusable
code. It is used as the foundation for the introductory Lasagne tutorial:
http://lasagne.readthedocs.org/en/latest/user/tutorial.html

More in-depth examples and reproductions of paper results are maintained in
a separate repository: https://github.com/Lasagne/Recipes
"""

from __future__ import print_function

import sys
import os
import time

import numpy as np
import theano
import theano.tensor as T

import lasagne



class NeuralNetwork:

    # Input data must be 2D np.array. Shape = (NUM_SAMPLES, input_layer_size)
    # input_layer_size must match the length of a feature vector in train_data
    # train_labels are shape (NUM_SAMPLES, 1)
    def __init__(self, train_data=None, train_labels=None, test_mnist=True, input_layer_size=784):
        self.test_mnist = test_mnist
        self.training_data = train_data
        self.training_labels = train_labels
        self.input_layer_size = input_layer_size

        # Prepare Theano variables for inputs and targets
        self.input_var = T.matrix('inputs')
        self.target_var = T.matrix('targets')

        # Create neural network model 
        self.network = self.build_mlp(self.input_var, input_layer_size=self.input_layer_size)

        # Create a loss expression for training, i.e., a scalar objective we want
        # to minimize (for our multi-class problem, it is the cross-entropy loss):
        prediction = lasagne.layers.get_output(self.network)
        loss = lasagne.objectives.squared_error(prediction, self.target_var)
        loss = loss.mean()

        # Create update expressions for training, i.e., how to modify the
        # parameters at each training step. Here, we'll use Stochastic Gradient
        # Descent (SGD) with Nesterov momentum, but Lasagne offers plenty more.
        params = lasagne.layers.get_all_params(self.network, trainable=True)
        updates = lasagne.updates.sgd(
                loss, params, learning_rate=0.01)

        # Create a loss expression for validation/testing. The crucial difference
        # here is that we do a deterministic forward pass through the network,
        # disabling dropout layers.
        test_prediction = lasagne.layers.get_output(self.network, deterministic=True)
        test_loss = lasagne.objectives.squared_error(test_prediction, self.target_var)
        test_loss = test_loss.mean()

        # Compile a function performing a training step on a mini-batch (by giving
        # the updates dictionary) and returning the corresponding training loss:
        self.train_fn = theano.function([self.input_var, self.target_var], loss, updates=updates)

        # Compile a second function computing the validation loss and accuracy:
        self.val_fn = theano.function([self.input_var, self.target_var], [test_loss, test_prediction])
        self.predict_fn = theano.function(inputs=[self.input_var], outputs=[test_prediction])

    def updateData(self, train_data=None, train_labels=None, input_layer_size=None):
        self.training_data = train_data
        self.training_labels = train_labels
        self.input_layer_size = input_layer_size

    def load_dataset(self):

        if sys.version_info[0] == 2:
            from urllib import urlretrieve
        else:
            from urllib.request import urlretrieve

        def download(filename, source='http://yann.lecun.com/exdb/mnist/'):
            print("Downloading %s" % filename)
            urlretrieve(source + filename, filename)

        import gzip

        def load_mnist_images(filename):
            if not os.path.exists(filename):
                download(filename)

            with gzip.open(filename, 'rb') as f:
                data = np.frombuffer(f.read(), np.uint8, offset=16)

            # Reshape data as matrix with 784 columns. 
            data = data.reshape(-1, 784)
            return data / np.float32(256)

        def load_mnist_labels(filename):
            if not os.path.exists(filename):
                download(filename)
            with gzip.open(filename, 'rb') as f:
                data = np.frombuffer(f.read(), np.uint8, offset=8)

            # Data must be 2D. 
            data = data.reshape(-1, 1)
            return np.float32(data)

        if self.test_mnist:
            X_train = load_mnist_images('train-images-idx3-ubyte.gz')
            y_train = load_mnist_labels('train-labels-idx1-ubyte.gz')
        else:
            X_train = self.training_data
            y_train = self.training_labels

        # We reserve the last 10000 training examples for validation.
        # Adjust number of training examples as needed depending on size
        # of dataset.
        X_train, X_val = X_train[:-10000], X_train[-10000:]
        y_train, y_val = y_train[:-10000], y_train[-10000:]

        return X_train, y_train, X_val, y_val


    def build_mlp(self, input_var=None, input_layer_size=784):

        # Input layer. Shape None specifies variable batch size. 
        l_in = lasagne.layers.InputLayer(shape=(None, input_layer_size),
                                         input_var=input_var)

        # Drop out with probablity 0.2; Drop out acts as regularization
        l_in_drop = lasagne.layers.DropoutLayer(l_in, p=0.2)

        # First hidden layer of size 800. Uses ReLu activation function. 
        # Weights initialized to glorot normal distribution.
        l_hid1 = lasagne.layers.DenseLayer(
                l_in_drop, num_units=100,
                nonlinearity=lasagne.nonlinearities.rectify)

        l_hid1_drop = lasagne.layers.DropoutLayer(l_hid1, p=0.5)

        l_hid2 = lasagne.layers.DenseLayer(
                l_hid1_drop, num_units=100,
                nonlinearity=lasagne.nonlinearities.rectify)

        l_hid3 = lasagne.layers.DenseLayer(
                l_hid2, num_units=100,
                nonlinearity=lasagne.nonlinearities.rectify)

        l_hid2_drop = lasagne.layers.DropoutLayer(l_hid3, p=0.5)

        # Output layer of 1 node. No non-linearity as this is
        # a regression problem.
        l_out = lasagne.layers.DenseLayer(
                l_hid2_drop, num_units=1,
                nonlinearity=lasagne.nonlinearities.identity)

        # Return the output layer.
        # This layer is the layer that 
        # represents the entire network
        return l_out


    # feature_vector must be a 1 dimension np.array, 
    # i.e. feature_vector.shape() = (, SIZE)
    def predict(self, feature_vector):

        # Since predict_fn takes a 2D matrix, we reshape our 
        # input to conform
        return self.predict_fn(feature_vector.reshape(1, -1))


    # ############################# Batch iterator ###############################
    # This is just a simple helper function iterating over training data in
    # mini-batches of a particular size, optionally in random order. It assumes
    # data is available as numpy arrays. For big datasets, you could load numpy
    # arrays as memory-mapped files (np.load(..., mmap_mode='r')), or write your
    # own custom data iteration function. For small datasets, you can also copy
    # them to GPU at once for slightly improved performance. This would involve
    # several changes in the main program, though, and is not demonstrated here.
    # Notice that this function returns only mini-batches of size `batchsize`.
    # If the size of the data is not a multiple of `batchsize`, it will not
    # return the last (remaining) mini-batch.

    def iterate_minibatches(self, inputs, targets, batchsize, shuffle=False):
        assert len(inputs) == len(targets)
        if shuffle:
            indices = np.arange(len(inputs))
            np.random.shuffle(indices)
        for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
            if shuffle:
                excerpt = indices[start_idx:start_idx + batchsize]
            else:
                excerpt = slice(start_idx, start_idx + batchsize)
            yield inputs[excerpt], targets[excerpt]


    def train(self, num_epochs=500):
        # Load the dataset
        print("Loading data...")
        X_train, y_train, X_val, y_val = self.load_dataset()

        # Finally, launch the training loop.
        print("Starting training...")
        # We iterate over epochs:
        for epoch in range(num_epochs):
            # In each epoch, we do a full pass over the training data:
            train_err = 0
            train_batches = 0
            start_time = time.time()
            for batch in self.iterate_minibatches(X_train, y_train, 50, shuffle=True):
                inputs, targets = batch
                train_err += self.train_fn(inputs, targets)
                train_batches += 1



            # And a full pass over the validation data:
            val_err = 0
            val_acc = 0
            val_batches = 0
            for batch in self.iterate_minibatches(X_val, y_val, 50, shuffle=False):
                inputs, targets = batch
                err, predictions = self.val_fn(inputs, targets)
                print(predictions, targets)
                val_err += err
                val_batches += 1

            # Then we print the results for this epoch:
            print("Epoch {} of {} took {:.3f}s".format(
                epoch + 1, num_epochs, time.time() - start_time))
            print("  training loss:\t\t{:.6f}".format(train_err / train_batches))
            print("  validation loss:\t\t{:.6f}".format(val_err / val_batches))


        # Optionally, you could now dump the network weights to a file like this:
        # np.savez('model.npz', *lasagne.layers.get_all_param_values(network))
        #
        # And load them again later on like this:
        # with np.load('model.npz') as f:
        #     param_values = [f['arr_%d' % i] for i in range(len(f.files))]
        # lasagne.layers.set_all_param_values(network, param_values)


def main():
    network = NeuralNetwork()
    network.train()





if __name__ == '__main__':
    main()