from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

svc = LinearSVC()
param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
tunedSVC = GridSearchCV(cv=3, estimator=svc, scoring='f1_macro', param_grid=param_grid)
scaledAndTunedSVC = make_pipeline(StandardScaler(), tunedSVC)
estimator = MultiOutputClassifier(scaledAndTunedSVC)
