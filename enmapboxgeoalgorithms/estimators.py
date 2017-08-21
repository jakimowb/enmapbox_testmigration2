from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler, Normalizer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVR, SVC, LinearSVR, LinearSVC, NuSVR, NuSVC

REGRESSORS = dict()
REGRESSORS['RandomForestRegressor'] = \
'''RandomForestRegressor(criterion='mse', max_depth=None, max_features='auto', max_leaf_nodes=None,
  min_impurity_split=1e-07, min_samples_leaf=1, min_samples_split=2, min_weight_fraction_leaf=0.0,
  n_estimators=10, oob_score=False)'''

#REGRESSORS['SVR'] = \
#"""make_pipeline(
#  StandardScaler(),
#  GridSearchCV(cv=3, estimator=MultiOutputRegressor(estimator=SVR(epsilon=0.001)),
#     param_grid={
#        'svr__gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
#        'svr__C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}))"""

CLASSIFIERS = dict()
CLASSIFIERS['RandomForestClassifier'] = \
'''RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini', max_depth=None,
   max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None,
   min_samples_leaf=1, min_samples_split=2, min_weight_fraction_leaf=0.0, n_estimators=10, oob_score=False)'''

#CLASSIFIERS['SVC'] = \
#"""make_pipeline(
#  StandardScaler(),
#  GridSearchCV(cv=3, estimator=SVC(class_weight=None, probability=False),
#     param_grid={
#        'svr__gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
#        'svr__C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}))"""


if __name__ == '__main__':

    print(SVC())

    for name, estimator in REGRESSORS.items():
        try:
            eval(estimator)
        except:
            print('can not evaluate '+name)


    print(eval(CLASSIFIERS['SVC']))
