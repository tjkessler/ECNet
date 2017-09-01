## Lower-level usage of model, data_utils, error_utils, and limit_parameters

### model.py
#### Class: multilayer_perceptron
Attributes:
- **layers**: list of layers; layers contain information about the number of neurons and the activation function in form [num, func]
- **weights**: list of TensorFlow weight variables
- **biases**: list of TensorFlow bias variables

Methods:
- **addLayer(num_neurons, activ_function)**: adds a layer to layers in form [num_neurons, activ_function]
  - supported activation functions: 'relu', 'sigmoid', 'linear'
- **connectLayers()**: initializes TensorFlow variables for weights and biases between each layer; fully connected
- **feed_forward(x)**: used by TensorFlow graph to feed data through weights and add biases
- **fit(x_l, y_l, learning_rate, train_epochs)**: fits the model to the inputs (x_l) and outputs (y_l) for train_epochs iterations
- **fit_validation(x_l, x_v, y_l, y_v, learning_rate, mdrmse_stop, mdrmse_memory, max_epochs)**: fits the model while using a validation set in order to test the learning performance over time
  - mdrmse: mean-delta-root-mean-squared error, or the change in the difference between RMSE values over time
  - mdrmse_stop is the cutoff point, where the function ceases learning (mdrmse approaches zero as epochs increases)
  - mdrmse_memory is used to determine how far back (number of epochs) the function looks in determining mdrmse
  - max_epochs is the cutoff point if mdrmse has not fallen below mdrmse_stop
- **test_new(x)**: used to pass data through the model to get a prediction, without training it
- **save_net(output_filepath)**: saves the TensorFlow session (.sess) and model architecture information (.struct) to specified filename
- **load_net(model_load_filename)**: opens a TensorFlow session (.sess) and model architecture information (.struct) to work with
- **export_weights()**: returns numerical versions of the model's TensorFlow weight variables
- **export_biases()**: returns numerical versions of the model's TensorFlow bias variables

Misc. Functions:
- **calc_valid_rmse(x, y)**: calculates the root-mean-squared error during 'fit_validation()'

### data_utils.py
#### Class: initialize_data(data_filename)
Methods:
- **build()**: imports a formatted database, parses controls, sets up groupings and data I/O locations
- **normalize(param_filepath)**: will normalize the input and output data to [0,1] using min-max normalization; saves a file containing normalization parameters
- **apply_normal(param_filepath)**: will apply the normalization paramters found in the specified file to un-normalized data
- **buildTVL(sort_type, data_split)**: builds the test, validation and learn sets using 'random' or 'explicit' sort types
  - supported sort types: 'random', 'explicit'
  - data_split format: [0.L, 0.V, 0.T] - sum of 0.L, 0.V and 0.T = 1
- **randomizeData(randIndex, data_split)**: used by 'buildTVL' to randomly assign test, validation and learn indices, which will be applied to each data input
- **applyTVL()**: applies the test, validation and learn indices to each data input
- **package()**: packages the data, so it can be handed to a machine learning model

Misc. Functions:
- **create_static_test_set(data)**: taking an initialize_data object, this function will create separate files for the test and learning/validation data; useful for when you need a static test set for completely blind model testing
- **output_results(results, data, which_data, filename)**: outputs your prediction results from your model to a specified filename
  - which_data: 'all' or 'test', corresponding to which data set(s) are contained in your results
- **denormalize_result(results, param_filepath)**: denormalizes a result, using min-max normalization paramters found in the param_filepath

### error_utils.py
- **Notation:**
  - y_hat - predicted values
  - y - known/experimental/training values
  
Error Functions:
- **calc_rmse(y_hat, y)**: calculates the root-mean-squared error
- **calc_mean_abs_error(y_hat, y)**: calculates the mean absolute error
- **calc_med_abs_error(y_hat, y)**: calculates the median absolute error
- **calc_r2(y_hat, y)**: calculates the correlation of determination, or r-squared value

### limit_parameters.py
Functions:
- **limit(server)**: limits the number of input parameters to an integer value specified in the server config.yml file, using a "retain the best" process, where the best performing input parameter (based on RMSE) is retained, paired with every other input parameter until a best pair is found, repeated until the limit number has been reached
  - returns a list of parameters
- **output(data, param_list, filename)**: saves a new .csv formatted database, using a generated parameter list and an output filename