import numpy as np


def get_ngrams(n, line):
    line = line.strip().split()
    cur_len = len(line)
    ngrams_list = []
    if cur_len == 0:
        # Token list is empty
        pass
    elif cur_len < n:
        # Token list fits in one ngram
        ngrams_list.append(" ".join(line))
    else:
        # Token list spans multiple ngrams
        loop_num = cur_len - n + 1
        for i in range(loop_num):
            cur_gram = " ".join(line[i: i + n])
            ngrams_list.append(cur_gram)
    return ngrams_list


def build_ngram_vocabulary(n, inputData):
    """
        Divides log into n-gram using get_ngrams method and creates vocabulary.
        Args:
            n: ngram size
            inputData: list of log lines
        Returns:
            Vocabulary to index dict
    """
    vocabulary = {}
    for line in inputData:
        ngrams_list = get_ngrams(n, line)
        for ngram in ngrams_list:
            if ngram not in vocabulary:
                vocabulary[ngram] = len(vocabulary)

    return vocabulary


def log_to_vector(n, inputData, vocabulary, y):
    result = []
    x_result = []
    y_result = []
    for index_data, line in enumerate(inputData):
        temp = []
        ngrams_list = get_ngrams(n, line)
        if ngrams_list:
            for cur_gram in ngrams_list:
                if cur_gram not in vocabulary:
                    continue
                else:
                    temp.append(vocabulary[cur_gram])
        result.append(temp)
        x_result.append(line)
        y_result.append(y[index_data])
    return np.array(result), np.array(y_result), x_result


def setTrainDataForILF(x, y):
    x_res, indices = np.unique(x, return_index=True)
    y_res = y[indices]

    return x_res, y_res


def calculate_inv_freq(total, num):
    return np.log(
            float(total) / float(num + 0.01)
        )


# CHECK IF USING MAX IS BETTER OR SIMILAR SPEED AS IT'S EASIER TO READ
# WHAT ABOUT NUMPY?
def get_max_line(inputVector):
    max_length = 0
    for line in inputVector:
        if len(line) > max_length:
            max_length = len(line)
    return max_length


def get_tf(inputVector):
    gram_index_dict = {}
    # Counting the number of logs the word appears in
    for index, line in enumerate(inputVector):
        for gram in line:
            if gram not in gram_index_dict:
                gram_index_dict[gram] = set()
            gram_index_dict[gram].add(index)
    return gram_index_dict


def get_lf(inputVector):
    gram_index_ilf_dict = {}
    for line in inputVector:
        for location, gram in enumerate(line):
            if gram not in gram_index_ilf_dict:
                gram_index_ilf_dict[gram] = set()
            gram_index_ilf_dict[gram].add(location)
    return gram_index_ilf_dict


def calculate_idf(gram_index_dict, inputVector, vocabulary):
    idf_dict = {}
    total_log_num = len(inputVector)
    for gram in gram_index_dict:
            idf_dict[gram] = calculate_inv_freq(
                                total_log_num,
                                len(gram_index_dict[gram])
                                )
    return idf_dict


def calculate_ilf(gram_index_dict, inputVector, vocabulary):
    ilf_dict = {}
    max_length = get_max_line(inputVector)
    # calculating ilf for each gram
    for gram in gram_index_dict:
        ilf_dict[gram] = calculate_inv_freq(
            max_length,
            len(gram_index_dict[gram])
            )
    return ilf_dict


def create_invf_vector(invf_dict, inputVector, vocabulary):
    tfinvf = []
    # Creating the idf/ilf vector for each log message
    for line in inputVector:
        cur_tfinvf = np.zeros(len(vocabulary))
        for gram_index in line:
                cur_tfinvf[gram_index] = (
                    float(line.count(gram_index)) * invf_dict[gram_index]
                )
        tfinvf.append(cur_tfinvf)

    tfinvf = np.array(tfinvf)
    return tfinvf


def calculate_tf_invf_train(inputVector, vocabulary,
                            get_tf=get_tf, calc_invf=calculate_idf):
    """In this version, tf is not normalized.
    We use frequence value as tf value.

    RETURN: tfidf,tfidf_mean,tfidf_std,idf_dict
    """
    gram_index_dict = get_tf(inputVector)
    invf_dict = calc_invf(gram_index_dict, inputVector, vocabulary)
    tfinvf = create_invf_vector(invf_dict, inputVector, vocabulary)
    return tfinvf, invf_dict