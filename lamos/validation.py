# -*- coding: utf-8 -*-
import numpy as np
import itertools

# from pyxelware import validation as v
# import os
#
# root = r'c:\Users\pflugmad\OneDrive\Documents\val_test'
#
# test = 'olofsson2013a'
# cm = v.MapAccuracy(count_matrix=v.examples[test]['confusion_matrix'],
#                    map_marginal_totals=v.examples[test]['map_marginal_totals'],
#                    class_labels=v.examples[test]['class_labels'], total_area=1755124)
# cm.export(os.path.join(root, 'aa_test_%s.csv' % test))
# cm.export(os.path.join(root, 'aa_test_%s_counts.csv' % test), proportions=False)
# cm.export(os.path.join(root, 'aa_test_%s_ci95.csv' % test), digits=3, matrix_digits=3, z_score=1.959963984540054)
#
#
# test = 'olofsson2014'
# cm = v.MapAccuracy(count_matrix=v.examples[test]['confusion_matrix'],
#                    map_marginal_totals=v.examples[test]['map_marginal_totals'],
#                    class_labels=v.examples[test]['class_labels'])
# cm.export(os.path.join(root, 'aa_test_%s_ci.csv' % test), digits=2, matrix_digits=4, z_score=1.959963984540054)
#
#
# aa = pd.read_csv(os.path.join(root, 'reference_samples_dp_map_and_prodes_char.csv'))
# weights = list(zip(['FFF', 'NNN', 'FNN', 'FFN'], [0.8129, 0.0297, 0.0886, 0.0688]))
# mt = list(zip(['FFF', 'NNN', 'FNN', 'FFN'], [24555651, 898436, 2677557, 2077628]))
# cm = v.MapAccuracy(samples=zip(aa.prodes, aa.map_class), map_marginal_totals=mt,
#                    class_labels=zip(['FFF', 'NNN', 'FNN', 'FFN'],
#                                     ['Stable Forest', 'Stable Nonforest', 'Deforestation 2006',
#                                      'Deforestation 2011']))
# cm.export(os.path.join(root, 'aa_test_prodes.csv'))
# cm.export(os.path.join(root, 'aa_test_prodes_ci95.csv'), z_score=1.959963984540054)
# cm = v.MapAccuracy(samples=zip(aa.prodes, aa.map_class))
# cm.export(os.path.join(root, 'aa_test_prodes_no_mt.csv'))
#
#
# test_file = os.path.join(root, 'reference_samples_dp_map_and_prodes.csv')
# aa = pd.read_csv(test_file)
# weights = list(zip([1,2,3,4], [0.8129, 0.0297, 0.0886, 0.0688]))
# mt = list(zip([1,2,3,4], [24555651, 898436, 2677557, 2077628]))
# cm = v.MapAccuracy(samples=zip(aa.prodes, aa.map_class), map_marginal_totals=mt)
# cm.export(os.path.join(root, 'aa_test_prodes_numeric.csv'))
# cm.export(os.path.join(root, 'aa_test_prodes_numeric_ci95.csv'), z_score=1.959963984540054)


examples = {
    'olofsson2014': {
        'confusion_matrix': np.array([[66, 0, 5, 4], [0, 55, 8, 12], [1, 0, 153, 11], [2, 1, 9, 313]]),
        'map_marginal_totals': list(zip([1, 2, 3, 4], np.array([200000, 150000, 3200000, 6450000]))),
        'stratum_weights': list(zip([1, 2, 3, 4], np.array([0.02, 0.015, 0.32, 0.645]))),
        'class_labels': list(zip([1, 2, 3, 4], ['Deforestation', 'Forest gain', 'Stable forest', 'Stable non-forest']))
    },

    'olofsson2013a': {
        'confusion_matrix': np.array([[97, 0, 3], [3, 279, 18], [2, 1, 97]]),
        'total_area': 1755124,
        'map_marginal_totals': list(zip([1, 2, 3], np.array([248367, 12472700, 6780311]))),
        'map_marginal_totals_ha': list(zip([1, 2, 3], np.array([22353, 1122543, 610228]))),
        'stratum_weights': list(zip([1, 2, 3], np.array([0.013, 0.640, 0.348]))),
        'class_labels': list(zip([1, 2, 3], ['Deforestation', 'Stable forest', 'Non-forest']))
    }
}


def unstack_confusion_matrix(cm, csv_file=None):

    long = np.array([(j+1, i+1) for j in range(cm.shape[1])
                    for i in range(cm.shape[0]) for _ in range(cm[i, j])])

    if csv_file is not None:
        np.savetxt(csv_file, np.vstack((['reference_class', 'map_class'], long)),
                   delimiter=',', fmt='%s')

    return long


def make_confusion_matrix(samples, ignore=None, class_labels=None):

    samples_list = list(samples)

    if class_labels is None:
        class_id = np.unique(samples_list)
        if ignore is not None:
            class_id = [z for z in class_id if z not in tuplefy(ignore)]
        class_name = [str(z) for z in class_id]
    else:
        class_list = list(class_labels)
        class_id = [str(z[0]) for z in class_list]
        class_name = [str(z[1]) for z in class_list]

    count_matrix = np.array([samples_list.count(i)
                            for i in itertools.product(class_id, repeat=2)],
                            dtype=np.float64)

    return {'matrix': count_matrix.reshape(len(class_id), len(class_id), order='F'), 'class_id': class_id, 'class_name': class_name}


def tuplefy(data):

    if type(data) is int or type(data) is str:
        return tuple([data, ])
    elif type(data) is tuple:
        return data
    else:
        return tuple(data)


class MapAccuracy(object):

    def __init__(self, samples=None, count_matrix=None, class_labels=None,
                 card=False, ignore=None, map_marginal_totals=None, total_area=None):

        self.samples = samples
        self.count_matrix = count_matrix
        self.overall_accuracy = None
        self.users_accuracy = None
        self.producers_accuracy = None
        self.reference_proportions = None
        self.proportional_matrix = None
        self.stratum_weights = None
        self.total_area = total_area

        if samples is None:
            classes = (np.arange(count_matrix.shape[0]) + 1).astype(str)
            if class_labels is None:
                self.class_labels = list(zip(classes, [str(z) for z in classes]))
            else:
                self.class_labels = class_labels
        else:
            result = make_confusion_matrix(samples, ignore=ignore, class_labels=class_labels)
            self.count_matrix = result['matrix']
            self.class_labels = list(zip(result['class_id'], result['class_name']))

        if map_marginal_totals is None:
            self.map_marginal_totals = np.nansum(self.count_matrix, 1)  # / 0.01
        else:
            self.map_marginal_totals = list(map_marginal_totals)
            map_total_ids = np.array([x[0] for x in self.map_marginal_totals])
            map_total_val = np.array([x[1] for x in self.map_marginal_totals])

            self.map_marginal_totals = np.array([map_total_val[np.where(map_total_ids == x[0])][0]
                                                 for x in self.class_labels
                                                 if np.where(map_total_ids == x[0])[0].shape[0] > 0])

        if len(self.map_marginal_totals) != len(self.class_labels):
            print('Map marginal totals not of the same length or classes as class labels.')
            return
        else:
            self.estimate_accuracy(card=card)

    def estimate_accuracy(self, card=False):

        # data   : confusion matrix with rows = map; columns = reference
        #       where the elements represent sampling counts
        # w   : stratum weights
        # i   : subscript i refers to reference class
        # j   : subscript j refers to map class

        n = self.count_matrix.copy().astype(np.float64)
        d = len(self.class_labels)

        # map totals
        n_j = np.nansum(n, 1)

        # reference totals
        # n_i = np.nansum(n, 0)

        # stratum weights
        if self.map_marginal_totals is None:
            w_j = n_j/np.nansum(n).astype(np.float64)
            w_j = np.nan_to_num(w_j)
            N_j = n_j
        else:
            w_j = np.array(self.map_marginal_totals)/np.sum(self.map_marginal_totals).astype(np.float64)
            N_j = self.map_marginal_totals.astype(np.float64)

        self.stratum_weights = w_j
        # Proportional error matrix
        p = n * (w_j/n_j).reshape(d, 1)
        p = np.nan_to_num(p)

        # User's Accuracy
        ua = np.diagonal(p)/np.nansum(p, 1)
        # Producer's Accuracy
        pa = np.diagonal(p)/np.nansum(p, 0)

        # Overall Accuracy
        oa = sum(np.diagonal(p))

        # Reference area proportions
        p_i = np.nansum(p, 0)

        if card:

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # standard errors after Card for stratified sampling
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # standard error of reference class proportions
            temp = p * (w_j.reshape(d, 1) - p) / n_j.reshape(d, 1)
            #  temp = np.nan_to_num(temp, 0)
            p_i_se = np.sqrt(np.nansum(temp, 0))
            # p_i_se = np.nan_to_num(p_i_se, 0)

            # standard error of producer's accurarcy
            term1 = np.diagonal(p) * np.power(p_i, -4)
            term2 = p * (w_j.reshape(d, 1) - p) / n_j.reshape(d, 1)
            term2[np.diag_indices(d)] = 0
            term2 = np.diagonal(p) * np.nansum(term2, 0)
            term3 = (w_j - np.diagonal(p)) * np.power((p_i - np.diagonal(p)), 2) / n_j
            pa_se = np.sqrt(term1 * (term2+term3))

            # standard error of user's accuracy
            # todo: check seems to result in lower estimates than the Olofsson formula
            ua_se = np.sqrt(np.diagonal(p) * (w_j - np.diagonal(p)) / (n_j * np.power(w_j, 2)))

            # standard error of overall accuracy
            oa_se = np.sqrt(sum(np.diagonal(p) * (w_j - np.diagonal(p)) / n_j))

        else:
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # standard errors after Olofsson et al (2014) stratified sampling
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Olofsson uses -1 degrees of freedom in comparison to Card 1982

            # standard error of producer's accuracy
            N_i = np.nansum(n * (N_j / n_j).reshape(d, 1), 0)

            term1 = np.power(N_j, 2) * np.power(1 - pa, 2) * ua * (1 - ua) / (n_j - 1)

            term2 = (np.power(N_j, 2)/n_j).reshape(d, 1) * n * (1 - n/n_j.reshape(d, 1))
            term2 /= (n_j.reshape(d, 1) - 1)
            term2[np.diag_indices(d)] = 0
            term2 = np.nansum(term2, 0)

            pa_se = np.sqrt((term1 + np.power(pa, 2) * term2)/np.power(N_i, 2))  # todo

            # standard error of user's accuracy
            ua_se = np.sqrt(ua * (1 - ua) / (n_j - 1))

            # standard error of overall accuracy
            oa_se = np.sqrt(np.nansum(np.power(w_j, 2) * ua * (1 - ua) / (n_j).reshape(d, 1)))

            # standard error of reference class proportions
            p_i_se = (w_j.reshape(d, 1) * p - np.power(p, 2)) / (n_j.reshape(d, 1) - 1)
            p_i_se = np.sqrt(np.nansum(p_i_se, 0))

        self.proportional_matrix = p
        self.overall_accuracy = (oa, oa_se)
        self.users_accuracy = list(zip(ua, ua_se))
        self.producers_accuracy = list(zip(pa, pa_se))
        self.reference_proportions = list(zip(p_i, p_i_se))

    def export(self, file_name, delimiter=',', digits=3, matrix_digits=None,
               z_score=1, proportions=True):

        if proportions is True:

            if self.proportional_matrix is None:
                print('Error in proportional error matrix. Abort export.')
                return
            confusion_matrix = self.proportional_matrix

        else:

            if self.count_matrix is None:
                print('Error in count error matrix. Abort export.')
                return
            confusion_matrix = self.count_matrix

        if matrix_digits is None:
            matrix_digits = digits

        tmp2s = '{:.%sf} \xb1 {:.%sf}' % (digits, digits)
        tmp1m = '{:.%sf}' % matrix_digits

        z = z_score
        class_names = [x[1] for x in self.class_labels]

        reference_proportions = [tmp2s.format(*(x[0], x[1]*z)) for x in self.reference_proportions]
        stratum_weights = np.array(['Area proportions'] + [tmp1m.format(x) for x in self.stratum_weights] +
                                   ['1'])[:, None]

        users_accuracy = np.array(["User's"] + [tmp2s.format(*(x[0], x[1]*z))
                                                for x in self.users_accuracy] + [''])[:, None]

        producers_accuracy = np.array(["Producer's"] +
                                      [tmp2s.format(*(x[0], x[1]*z)) for x in self.producers_accuracy] + [''])[:, None]

        overall_accuracy = np.array(["Overall"] +
                                    [tmp2s.format(*(self.overall_accuracy[0], self.overall_accuracy[1] * z))] +
                                    [''] * len(class_names))[:, None]

        confusion_matrix_str = np.array([tmp1m.format(x) for x in confusion_matrix.reshape(confusion_matrix.size)])
        confusion_matrix_str = confusion_matrix_str.reshape(confusion_matrix.shape)

        charcopy = np.vstack((class_names, confusion_matrix_str, reference_proportions))

        row_labels = np.array(['Class'] + class_names + ["Area proportions"])[:, None]

        if self.total_area is not None:
            total_area = np.array(["Area"] + [tmp2s.format(*(x[0] * self.total_area, x[1] * self.total_area * z))
                                              for x in self.reference_proportions] + [''])[:, None]
            charcopy = np.hstack((row_labels, charcopy, stratum_weights, users_accuracy,
                                 producers_accuracy, total_area, overall_accuracy))
        else:
            charcopy = np.hstack((row_labels, charcopy, stratum_weights, users_accuracy,
                                 producers_accuracy, overall_accuracy))

        np.savetxt(file_name, charcopy, delimiter=delimiter, fmt='%s')
