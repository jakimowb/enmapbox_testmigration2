from __future__ import print_function
from enmapbox.processing.types import Classifier
import sklearn.neural_network

class MLPClassifier(Classifier):

    def __init__(self, activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
                       beta_2=0.999, early_stopping=False, epsilon=1e-08,
                       hidden_layer_sizes=(100,), learning_rate='constant',
                       learning_rate_init=0.001, max_iter=200, momentum=0.9,
                       nesterovs_momentum=True, power_t=0.5, random_state=None,
                       shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
                       verbose=False, warm_start=False,
                       copy=True, with_mean=True, with_std=True):

        scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
        mlp = sklearn.neural_network.MLPClassifier(activation=activation, alpha=alpha, batch_size=batch_size, beta_1=beta_1,
                       beta_2=beta_2, early_stopping=early_stopping, epsilon=epsilon,
                       hidden_layer_sizes=hidden_layer_sizes, learning_rate=learning_rate,
                       learning_rate_init=learning_rate_init, max_iter=max_iter, momentum=momentum,
                       nesterovs_momentum=nesterovs_momentum, power_t=power_t, random_state=random_state,
                       shuffle=shuffle, solver=solver, tol=tol, validation_fraction=validation_fraction,
                       verbose=verbose, warm_start=warm_start)

        pipe = sklearn.pipeline.make_pipeline(scaler, mlp)
        Classifier.__init__(self, pipe)

def test_MLPClassifier():
    from enmapbox.processing.types import Image, Classification

    # get test data
    image = Image(r'C:\Work\data\Hymap_Berlin-A_Image')
    train = Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')
    test = Classification(r'C:\Work\data\Hymap_Berlin-A_Classification-Validation-Sample')

    mlp = MLPClassifier()
    mlp.fit(image=image, labels=train)
    classification = mlp.predict(image=image,filename=r'C:\Work\data\_mlpClassification')
    accAss = classification.assessClassificationPerformance(classification=test)
    print('Overall Accuracy:', accAss.OverallAccuracy)

if __name__ == '__main__':
    test_MLPClassifier()
