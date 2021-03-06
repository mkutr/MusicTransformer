import utils
import random
import pickle
import tensorflow as tf
from tensorflow.python import keras
import numpy as np
import params as par


class Data:
    def __init__(self, dir_path):
        self.files = list(utils.find_files_by_extensions(dir_path, ['.pickle']))
        self.file_dict = {
            'train': self.files[:int(len(self.files) * 0.8)],
            'eval': self.files[int(len(self.files) * 0.8): int(len(self.files) * 0.9)],
            'test': self.files[int(len(self.files) * 0.9):],
        }
        self._seq_file_name_idx = 0
        self._seq_idx = 0
        self.batch_it_dict = {
            'train': 0,
            'eval': 0,
            'test': 0,
        }

    def __repr__(self):
        return '<class Data has "' + str(len(self.files)) + '" files>'

    # def generator

    def batch(self, batch_size, length, mode='train', random_select=True):
        if random_select:
            batch_files = random.sample(self.file_dict[mode], k=batch_size)
        else:
            curr_it = self.batch_it_dict[mode]
            batch_files = self.file_dict[mode][curr_it:curr_it + batch_size]
            self.batch_it_dict[mode] = (curr_it + batch_size) % len(self.file_dict[mode])

        batch_data = [self._get_seq(file, length) for file in batch_files]
        return np.array(batch_data)  # batch_size, seq_len

    def seq2seq_batch(self, batch_size, length, mode='train'):
        data = self.batch(batch_size, length * 2, mode)
        x = data[:, :length]
        y = data[:, length:]
        return x, y

    def smallest_encoder_batch(self, batch_size, length, mode='train'):
        data = self.batch(batch_size, length * 2, mode)
        x = data[:, :length // 100]
        y = data[:, length // 100:length // 100 + length]
        return x, y

    def slide_seq2seq_batch(self, batch_size, length, mode='train'):
        data = self.batch(batch_size, length + 1, mode)
        x = data[:, :-1]
        y = data[:, 1:]
        return x, y

    def random_sequential_batch(self, batch_size, length):
        batch_files = random.sample(self.files, k=batch_size)
        batch_data = []
        for i in range(batch_size):
            data = self._get_seq(batch_files[i])
            for j in range(len(data) - length):
                batch_data.append(data[j:j + length])
                if len(batch_data) == batch_size:
                    return batch_data

    def sequential_batch(self, batch_size, length):
        batch_data = []
        data = self._get_seq(self.files[self._seq_file_name_idx])

        while len(batch_data) < batch_size:
            while self._seq_idx < len(data) - length:
                batch_data.append(data[self._seq_idx: self._seq_idx + length])
                self._seq_idx += 1
                if len(batch_data) == batch_size:
                    return batch_data

            self._seq_idx = 0
            self._seq_file_name_idx = self._seq_file_name_idx + 1
            if self._seq_file_name_idx == len(self.files):
                self._seq_file_name_idx = 0
                print('iter intialized')

    def _get_seq(self, fname, max_length=None):
        with open(fname, 'rb') as f:
            data = pickle.load(f)
        if max_length is not None:
            if max_length <= len(data):
                start = random.randrange(0, len(data) - max_length)
                data = data[start:start + max_length]
            else:
                data = np.append(data, par.token_eos)
                while len(data) < max_length:
                    data = np.append(data, par.pad_token)
        return data


class PositionalY:
    def __init__(self, data, idx):
        self.data = data
        self.idx = idx

    def position(self):
        return self.idx

    def data(self):
        return self.data

    def __repr__(self):
        return '<Label located in {} position.>'.format(self.idx)


def add_noise(inputs: np.array, rate: float = 0.01):  # input's dim is 2
    seq_length = np.shape(inputs)[-1]

    num_mask = int(rate * seq_length)
    for inp in inputs:
        rand_idx = random.sample(range(seq_length), num_mask)
        inp[rand_idx] = random.randrange(0, par.pad_token)

    return inputs

class DataNew:
    def __init__(self, dir_path, seq_length, batch_size=1):
        self.files = list(utils.find_files_by_extensions(dir_path, ['.pickle']))
        # self.file_list =
        self.file_dict = {
            'train': self.files[:int(len(self.files) * 0.8)],
            'eval': self.files[int(len(self.files) * 0.8): int(len(self.files) * 0.9)],
            'test': self.files[int(len(self.files) * 0.9):],
        }

        generator_train = DataGenerator(self.file_dict['train'], seq_length=seq_length, batch_size=batch_size)
        generator_eval = DataGenerator(self.file_dict['eval'], seq_length=seq_length, batch_size=batch_size)
        generator_test = DataGenerator(self.file_dict['test'], seq_length=seq_length, batch_size=batch_size)

        # self.generators_dict = {
        #     'train': (generator_train.generate_batches_x(), generator_train.generate_batches_y()),
        #     'eval': (generator_eval.generate_batches_x(), generator_eval.generate_batches_y()),
        #     'test': (generator_test.generate_batches_x(), generator_test.generate_batches_y())
        # }

        # self.generators_dict = {
        #     'train': generator_train,
        #     'eval': generator_eval,
        #     'test': generator_test
        # }
        self.generators_dict = {
            'train': generator_train.generate_batches(),
            'eval': generator_eval.generate_batches(),
            'test': generator_test.generate_batches()
        }

        self._seq_file_name_idx = 0
        self._seq_idx = 0
        self.batch_it_dict = {
            'train': 0,
            'eval': 0,
            'test': 0,
        }

    def __repr__(self):
        return '<class Data has "' + str(len(self.files)) + '" files>'

    # def generator

    def batch(self, batch_size, length, mode='train', random_select=True):
        if random_select:
            batch_files = random.sample(self.file_dict[mode], k=batch_size)
        else:
            curr_it = self.batch_it_dict[mode]
            batch_files = self.file_dict[mode][curr_it:curr_it + batch_size]
            self.batch_it_dict[mode] = (curr_it + batch_size) % len(self.file_dict[mode])

        batch_data = [self._get_seq(file, length) for file in batch_files]
        return tf.convert_to_tensor(np.array(batch_data))
 # batch_size, seq_len

    def seq2seq_batch(self, batch_size, length, mode='train'):
        data = self.batch(batch_size, length * 2, mode)
        x = data[:, :length]
        y = data[:, length:]
        return x, y

    def smallest_encoder_batch(self, batch_size, length, mode='train'):
        data = self.batch(batch_size, length * 2, mode)
        x = data[:, :length // 100]
        y = data[:, length // 100:length // 100 + length]
        return x, y

    def slide_seq2seq_batch(self, batch_size, length, mode='train'):
        data = self.batch(batch_size, length + 1, mode)
        x = data[:, :-1]
        y = data[:, 1:]
        return x, y

    def random_sequential_batch(self, batch_size, length):
        batch_files = random.sample(self.files, k=batch_size)
        batch_data = []
        for i in range(batch_size):
            data = self._get_seq(batch_files[i])
            for j in range(len(data) - length):
                batch_data.append(data[j:j + length])
                if len(batch_data) == batch_size:
                    return batch_data

    def sequential_batch(self, batch_size, length):
        batch_data = []
        data = self._get_seq(self.files[self._seq_file_name_idx])

        while len(batch_data) < batch_size:
            while self._seq_idx < len(data) - length:
                batch_data.append(data[self._seq_idx: self._seq_idx + length])
                self._seq_idx += 1
                if len(batch_data) == batch_size:
                    return batch_data

            self._seq_idx = 0
            self._seq_file_name_idx = self._seq_file_name_idx + 1
            if self._seq_file_name_idx == len(self.files):
                self._seq_file_name_idx = 0
                print('iter intialized')

    def _get_seq(self, fname, max_length=None):
        with open(fname, 'rb') as f:
            data = pickle.load(f)
        if max_length is not None:
            if max_length <= len(data):
                start = random.randrange(0, len(data) - max_length)
                data = data[start:start + max_length]
            else:
                data = np.append(data, par.token_eos)
                while len(data) < max_length:
                    data = np.append(data, par.pad_token)
        return data

class DataGenerator(tf.keras.utils.Sequence):
    def __init__(self, files_list, seq_length, batch_size):
        'Initialization'
        self.batch_size = batch_size
        self.files_list = files_list
        self.seq_length = seq_length
        # self.files_data_dict = {}
        # self.populate_files_data_list()
        # self._seq_file_name_idx = 0
        # self._seq_idx = 0
        # self.batch_it = 0
        # self.batch_it_dict = {
        #     'train': 0,
        #     'eval': 0,
        #     'test': 0,
        # }

    # def populate_files_data_list(self):
    #     for el in self.files_list:
    #         data = self._get_seq(el)
    #         self.files_data_dict[el] = data


    # @staticmethod
    # def concat_parallel(a, b):
    #     l = np.array(
    #         [np.concatenate((np.array([x], dtype=np.int32), np.array([y], dtype=np.int32))) for x in a for y in b])
    #     return tf.convert_to_tensor(l, dtype=tf.int32)

    @staticmethod
    def concat_parallel(a, b):
        a = list(a)
        b = list(b)
        z = list(zip(a, b))
        l = [(tf.convert_to_tensor(np.array([x], dtype=np.int32)),
              tf.convert_to_tensor(np.array([y], dtype=np.int32))) for x, y in z]
        return l

    def generate_batches(self):
        batches_x = np.empty((0, self.seq_length))
        batches_y = np.empty((0, self.seq_length))
        # all
        for file in self.files_list:
            if batches_x.shape[0] < self.batch_size:
                file_content = self._get_all_seq(file)
                batches_x = np.concatenate((batches_x, file_content[:-1]))
                batches_y = np.concatenate((batches_y, file_content[1:]))
            #

            # file_content_as_np = DataGenerator.reshape_trimmed(file_content, -1, self.batch_size)
            # print(f"${batches.shape}")
            # print(f"{batches.shape[0] / self.batch_size}")
            if batches_x.shape[0] / self.batch_size >= 1:
                concat = DataGenerator.concat_parallel(batches_x[0:self.batch_size], batches_y[0:self.batch_size])
                yield concat
                batches_x = batches_x[self.batch_size:]
                batches_y = batches_y[self.batch_size:]

    def generate_batches_x(self):
        batches_x = np.empty((0, self.seq_length))
        # batches_y = np.empty((0, self.seq_length))
        # all
        for file in self.files_list:
            if batches_x.shape[0] < self.batch_size:
                file_content = self._get_all_seq(file)
                batches_x = np.concatenate((batches_x, file_content[:-1]))
                # batches_y = np.concatenate((batches_y, file_content[1:]))


            # file_content_as_np = DataGenerator.reshape_trimmed(file_content, -1, self.batch_size)
            # print(f"${batches.shape}")
            # print(f"{batches.shape[0] / self.batch_size}")
            if batches_x.shape[0] / self.batch_size >= 1:
                yield batches_x[0:self.batch_size]
                batches_x = batches_x[self.batch_size:-1]
                # batches_y = batches_y[self.batch_size:-1]

    def generate_batches_y(self):
        # batches_x = np.empty((0, self.seq_length))
        batches_y = np.empty((0, self.seq_length))
        # all
        for file in self.files_list:
            if batches_y.shape[0] < self.batch_size:
                file_content = self._get_all_seq(file)
                # batches_x = np.concatenate((batches_x, file_content[:-1]))
                batches_y = np.concatenate((batches_y, file_content[1:]))

            # file_content_as_np = DataGenerator.reshape_trimmed(file_content, -1, self.batch_size)
            # print(f"${batches.shape}")
            # print(f"{batches.shape[0] / self.batch_size}")
            if batches_y.shape[0] / self.batch_size >= 1:
                yield batches_y[0:self.batch_size]
                # batches_x = batches_x[self.batch_size:-1]
                batches_y = batches_y[self.batch_size:-1]
            # for batch in batches:

        # while
        #     file_it = 0
    #
    # def get_next_seq(self):
    #     for file in self.files_list:
    #         file_content = self._get_all_seq(file)
    #         for seq in file_content:
    #
    #     while
    #     file_it = 0

    # def __getitem__(self, index):
    #
    #     if index <
    #     return self.get_next_batch[index]
    def __getitem__(self, index):
        filenames = self.files_list[index*self.batch_size:(index+1)*self.batch_size]
        batchXY = self.seq2seq_batch(filenames, self.batch_size, self.seq_length)
        # print(f"batchXY: {batchXY.shape}")

        # Find list of IDs
        # list_IDs_temp = [self.list_IDs[k] for k in indexes]
        # batch_data = [self._get_seq(file, self.seq_length) for file in filenames]
        # Generate data
        # X, y = self.__data_generation(list_IDs_temp)
        x = batchXY[0] #[index]
        y = batchXY[1] #[index]
        # print(f"x: ${x}")
        return x, y

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.files_list) / self.batch_size))

    def batch(self, filenames, length):
        # curr_it = self.batch_it_dict[mode]
        # batch_files = self.file_dict[mode][curr_it:curr_it + batch_size]
        # self.batch_it_dict[mode] = (curr_it + batch_size) % len(self.file_dict[mode])

        batch_data = [self._get_seq(file, length) for file in filenames]
        return np.array(batch_data)  # batch_size, seq_len

    def seq2seq_batch(self, filenames, batch_size, length, mode='train'):
        data = self.batch(filenames, length * 2)
        x = data[:, :length]
        y = data[:, length:]
        return x, y

    def slide_seq2seq_batch(self, filenames, length, mode='train'):
        data = self.batch(filenames, length + 1)
        x = data[:, :-1]
        y = data[:, 1:]

        return x, y

    @staticmethod
    def reshape_trimmed(l, x, y):
        to_trim = len(l) % y
        l = l[0:-to_trim]
        return l.reshape(x, y)

    def _get_all_seq(self, fname):
        with open(fname, 'rb') as f:
            data = np.array(pickle.load(f))

        return DataGenerator.reshape_trimmed(data, -1, self.seq_length)

        # if max_length is not None:
        #     if max_length <= len(data):
        #         start = random.randrange(0, len(data) - max_length)
        #         data = data[start:start + max_length]
        #     else:
        #         data = np.append(data, par.token_eos)
        #         while len(data) < max_length:
        #             data = np.append(data, par.pad_token)
        # return data

    def _get_seq(self, fname, max_length=None):
        with open(fname, 'rb') as f:
            data = pickle.load(f)
        if max_length is not None:
            if max_length <= len(data):
                start = random.randrange(0, len(data) - max_length)
                data = data[start:start + max_length]
            else:
                data = np.append(data, par.token_eos)
                while len(data) < max_length:
                    data = np.append(data, par.pad_token)
        return data

if __name__ == '__main__':
    import pprint

    d = DataNew("midi_processed", 2048, 2)
    for el in d.generators_dict["train"][0]:
        print(el)

    # def count_dict(max_length, data):
    #     cnt_arr = [0] * max_length
    #     cnt_dict = {}
    #     # print(cnt_arr)
    #     for batch in data:
    #         for index in batch:
    #             try:
    #                 cnt_arr[int(index)] += 1
    #
    #             except:
    #                 print(index)
    #             try:
    #                 cnt_dict['index-' + str(index)] += 1
    #             except KeyError:
    #                 cnt_dict['index-' + str(index)] = 1
    #     return cnt_arr

    # print(add_noise(np.array([[1,2,3,3,4,5,6]]), rate=0.2))

    # print(par.vocab_size)
    # data = Data('dataset/processed')
    # # ds = DataSequence('dataset/processed', 10, 2048)
    # sample = data.seq2seq_batch(1000, 100)[0]
    # pprint.pprint(list(sample))
    # arr = count_dict(par.vocab_size+3,sample)
    # pprint.pprint(
    #     arr)
    #
    # from sequence import EventSeq, Event
    #
    # event_cnt = {
    #     'note_on': 0,
    #     'note_off': 0,
    #     'velocity': 0,
    #     'time_shift': 0
    # }
    # for event_index in range(len(arr)):
    #     for event_type, feat_range in EventSeq.feat_ranges().items():
    #
    #         if feat_range.start <= event_index < feat_range.stop:
    #             print(event_type+':'+str(arr[event_index])+' event cnt: '+str(event_cnt))
    #             event_cnt[event_type] += arr[event_index]
    #
    # print(event_cnt)

    # print(np.max(sample), np.min(sample))
    # print([data._get_seq(file).shape for file in data.files])
    # while True:
    # print(ds.__getitem__(10)[1].argmax(-1))
