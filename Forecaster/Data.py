import numpy as np
import tensorflow as tf

class Data:
    def __init__(self, data, target, train_split,
                 history_size, target_size, uni_data, step, single_step=False,
                 standardization=True):
        assert isinstance(data, np.ndarray)
        assert data.shape[0] > train_split
        self.data = self.standardize(data, train_split) if standardization else data
#         self.data = data
    
        if uni_data == True:
            self.x_train, self.x_train_target, self.y_train = self.__univariate_data(
                target, 0, train_split, history_size, target_size, step, single_step
            )
            self.x_val, self.x_val_target, self.y_val = self.__univariate_data(
                target, train_split, None, history_size, target_size, step, single_step
            )
        else:
            self.x_train, self.x_train_target, self.y_train = self.__multivariate_data(
                target, 0, train_split, history_size, target_size, step, single_step
            )
            self.x_val, self.x_val_target, self.y_val = self.__multivariate_data(
                target, train_split, None, history_size, target_size, step, single_step
            )

    @staticmethod
    def standardize(data, train_split):
        mean = data[:train_split].mean(axis=0)
        std = data[:train_split].std(axis=0)
        print('Data Std', std)
        print('Data Mean', mean)
        return (data - mean) / std

    def __univariate_data(self, target, start_index, end_index,
                          history_size, target_size, step, single_step=False):
        x, x_target, y = [], [], []
        data_target = self.data[:, target]

        start_index = start_index + history_size
        if end_index is None:
            end_index = len(self.data) - target_size

        for i in range(start_index, end_index):
            indices = range(i - history_size, i, step)
            x.append(np.reshape(data_target[indices], (-1, 1)))
            x_target.append(np.reshape(data_target[indices], (-1, 1)))
            if single_step:
                y.append([data_target[i + target_size]])
            else:
                y.append(data_target[i:i + target_size])
        return np.array(x), np.array(x_target), np.array(y)
    
    def __multivariate_data(self, target, start_index, end_index,
                          history_size, target_size, step, single_step=False):
        x, x_target, y = [], [], []
        data_target = self.data[:, target]

        start_index = start_index + history_size
        if end_index is None:
            end_index = len(self.data) - target_size

        for i in range(start_index, end_index):
            indices = range(i - history_size, i, step)
            x.append(self.data[indices])
            x_target.append(np.reshape(data_target[indices], (-1, 1)))
            if single_step:
                y.append([data_target[i + target_size]])
            else:
                y.append(data_target[i:i + target_size])
        return np.array(x), np.array(x_target), np.array(y)

    def dataset(self, buffer_size, batch_size):
        data_train = tf.data.Dataset.from_tensor_slices((self.x_train, self.x_train_target, self.y_train))
        data_train = data_train.cache().shuffle(buffer_size).batch(batch_size)
#         data_train = data_train.cache().batch(batch_size)
        data_val = tf.data.Dataset.from_tensor_slices((self.x_val, self.x_val_target, self.y_val))
        data_val = data_val.batch(batch_size)
        return data_train, data_val