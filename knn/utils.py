import numpy as np
import time

class DataSystem:


    def __init__(self, dim=2, num_points=1000, distribution = 'normal'):
        """
        Parameters
            dim (int)               : Dimension of the data required
            num_points (int)        : Number of the data points required
            distribution (string)   : The distribution from which the generated data will be sampled from
                options:
                    'normal'        : Normal Distribution
                    'uniform'       : Uniform Distribution
                    'beta'          : Beta Distribution
                    'exponential'   : Exponential Distribution
                    'gamma'         : Gamma Distribution
                    'geometric'     : Geometric Distribution
                    'poisson'       : Poisson Distribution
        """
        self.dim = dim
        self.num_points = num_points
        self.distribution = distribution
        np.random.seed(42)
    

    def generate(self, memory=True, path=None, **kwargs):
        """
        Generates numbers from a specified distribution

            Parameters:
                memory (bool)       : denoted whether the data has to be stored in memory or not
                path (string)       : Path where the data will be stored, if memory = True (Please specify path as .txt)
                **kwargs            : Parameters of the required distribution.

            Returns:
            data                    : Numpy array of size (num_points x dim)

        """
        # Get the correspoding numpy function for the distribution
        func = self.get_dist_func()
        # Get the arguments for the function as a dictionary
        func_args = self.get_func_args()
        # Update the arguments from the **kwargs passed
        func_args.update(pair for pair in kwargs.items() if pair[0] in func_args.keys())

        if memory is not True:
            assert path is not None, "Specify path, if you don't want things in memory"
        
            # TODO: Disk arrays
            # Save the array to the given path
            np.savetxt(path, func(**func_args))

        else:
            # Memory arrays
            data = func(**func_args)
            print(data.shape)
            return data
    

    def get_dist_func(self):
        func_dict = {
            'normal': np.random.normal,
            'uniform': np.random.uniform,
            'beta': np.random.beta,
            'exponential': np.random.exponential,
            'gamma': np.random.gamma,
            'geometric': np.random.geometric,
            'poisson': np.random.poisson,
        }
        # Get the function from function dictionary
        func = func_dict.get(self.distribution, lambda: "Invalid distribution")
        # Return the function
        return func
    

    def get_func_args(self):
        arg_dict = {
            'normal': {'loc' : 0.0, 'scale' : 1.0, 'size' : (self.num_points, self.dim)},
            'uniform': {'low' : 0.0, 'high' : 1.0, 'size' : (self.num_points, self.dim)},
            'beta': {'a': 1, 'b' : 2, 'size' : (self.num_points, self.dim)},
            'exponential': {'scale' : 1.0, 'size' : (self.num_points, self.dim)},
            'gamma': {'shape' : 2.0, 'scale' : 1.0, 'size' : (self.num_points, self.dim)},
            'geometric': {'p': 0.5, 'size' : (self.num_points, self.dim)},
            'poisson': {'lam' : 1.0, 'size' : (self.num_points, self.dim)},
        }
        # Get the arguments from argument dictionary
        args = arg_dict.get(self.distribution, lambda: "Invalid distribution")
        # Return the arguments
        return args


class Data_Generator(DataSystem):

    def __init__(self, chunk_dist, high=100, low=10):

        """
        Parameters
            chunk_dist (string)              : The distribution of the online chunks to be sent to each processor
                options:
                    'constant_low'           : Constant low values throughout
                    'constant_high'          : Constant high values throughout
                    'random'                 : Completely random set of values between 1 and 100
                    'crest_trough'           : Alternating values of high and low
                    'low_high'               : A stretch of low values followed by high values
                    'high_low'               : A stretch of high values followed by low values
        """

        self.chunk_dist = chunk_dist
        self.high = high
        self.low = low
        # self.sleep_dist = sleep_dist


    def generate_chunk_list(self):

        if (self.chunk_dist == 'consant_low'):
            no_chunks = int(self.num_points / self.low)
            chunk_list = [self.low]
            return chunk_list*no_chunks
        
        elif (self.chunk_dist == 'constant_high'):
            no_chunks = int(self.num_points / self.high)
            chunk_list = [self.high]
            return chunk_list*no_chunks

        elif (self.chunk_dist == 'random'):
            no_chunks = int(self.num_points / self.high)
            chunk_list = []
            total = no_chunks
            for i in range(no_chunks-1):
                val = np.random.randint(0, total)
                chunk_list.append(val)
                total -= val
            chunk_list.append(total)
            return chunk_list
        
        elif (self.chunk_dist == 'crest_trough'):
            each_count = int(self.num_points / (self.low + self.high))
            chunk_list = [self.low, self.high]
            return chunk_list*each_count
        
        elif (self.chunk_dist == 'low_high'):
            each_count = int(self.num_points / (self.low + self.high))
            low_list = [self.low]*each_count
            high_list = [self.high]*each_count
            return low_list+high_list

        elif (self.chunk_dist == 'high_low'):
            each_count = int(self.num_points / (self.low + self.high))
            low_list = [self.low]*each_count
            high_list = [self.high]*each_count
            return high_list+low_list


    def data_generator(self, chunk_size, **kwargs):
        
        chunk_list = self.generate_chunk_list()
        for chunk_size in chunk_list:
            data = self.generate(memory=True, path=None, size = (chunk_size, self.dim))
            yield data

# data_class = DataSystem()