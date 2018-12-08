#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ecnet/fitness_functions.py
# v.1.7.0
# Developed in 2018 by Travis Kessler <travis.j.kessler@gmail.com>
#
# Contains fitness functions used for input dimensionality reduction,
# hyperparameter tuning
#

# Stdlib imports
from multiprocessing import current_process

# ECNet imports
import ecnet.model
import ecnet.error_utils


def limit_inputs(parameters, args):
    '''Genetic algorithm cost function, supplied to the genetic algorithm

    Args:
        parameters (dictionary): dictionary of parameter names and values
        args (dictionary): dictionary of arguments to pass

    Returns:
        float: RMSE of model used with supplied parameters
    '''

    learn_input = []
    valid_input = []
    test_input = []

    if args['shuffle']:
        args['DataFrame'].shuffle(
            'l', 'v', 't',
            split=args['data_split']
        )
        packaged_data_cf = args['DataFrame'].package_sets()
    else:
        packaged_data_cf = args['packaged_data']

    for param in parameters:
        learn_input_add = [
            [sublist[
                parameters[param]
            ]] for sublist in packaged_data_cf.learn_x
        ]
        valid_input_add = [
            [sublist[
                parameters[param]
            ]] for sublist in packaged_data_cf.valid_x
        ]
        test_input_add = [
            [sublist[
                parameters[param]
            ]] for sublist in packaged_data_cf.test_x
        ]

        if len(learn_input) == 0:
            learn_input = learn_input_add
            valid_input = valid_input_add
            test_input = test_input_add
        else:
            for idx_add, param_add in enumerate(learn_input_add):
                learn_input[idx_add].append(param_add[0])
            for idx_add, param_add in enumerate(valid_input_add):
                valid_input[idx_add].append(param_add[0])
            for idx_add, param_add in enumerate(test_input_add):
                test_input[idx_add].append(param_add[0])

    if args['num_processes'] > 1:
        model = ecnet.model.MultilayerPerceptron(
            id=current_process()._identity[0] % args[
                'num_processes'
            ]
        )
    else:
        model = ecnet.model.MultilayerPerceptron()
    model.add_layer(len(learn_input[0]), args['input_activation'])
    for layer in args['hidden_layers']:
        model.add_layer(layer[0], layer[1])
    model.add_layer(
        len(packaged_data_cf.learn_y[0]),
        args['output_activation']
    )
    model.connect_layers()

    model.fit_validation(
        learn_input,
        packaged_data_cf.learn_y,
        valid_input,
        packaged_data_cf.valid_y,
        learning_rate=args['learning_rate'],
        keep_prob=args['keep_prob'],
        max_epochs=args['validation_max_epochs']
    )

    return ecnet.error_utils.calc_rmse(
        model.use(test_input),
        packaged_data_cf.test_y
    )


# Can I pass data to this? I don't want to have to re-import if I've already
#   sorted/split
def tune_hyperparameters(values):
    '''Fitness function used by artificial bee colony

    Args:
        values (tuple): (learning_rate, validation_max_epochs, keep_prob,
            hidden_layers)

    Returns:
        float: mean absolute error
    '''

    return sum(values)

    # Old method is depricated, new neural network creation method is required