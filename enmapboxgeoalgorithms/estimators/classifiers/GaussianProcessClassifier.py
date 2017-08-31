from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

gpc = GaussianProcessClassifier(RBF(), max_iter_predict=1)
scaledGPC = make_pipeline(StandardScaler(), gpc)
estimator = scaledGPC
