from eb.types import Classifier, Regressor, Transformer, Clusterer, ClassificationSample
import sklearn.pipeline
import sklearn.preprocessing
import sklearn.grid_search
import sklearn.svm
import sklearn.ensemble
import sklearn.cluster
from eb.report import *
from HTML import Table, TableRow, TableCell
from eb.env import PrintProgress, SilentProgress
import numpy
import matplotlib.pyplot as plt

def all(estimators):

#    for k, v in estimators.__dict__.items():
#        if not k.startswith('_'):
#            print k
#            print v()
    return [v() for k, v in estimators.__dict__.items() if not k.startswith('_')]


class Classifiers():

    class LinearSVC(Classifier):

        def __init__(self, C=1., class_weight=None, dual=True, fit_intercept=True,
                  intercept_scaling=1, loss='squared_hinge', max_iter=1000,
                  multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
                  verbose=0,
                  copy=True, with_mean=True, with_std=True):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svc = sklearn.svm.LinearSVC(C=C, class_weight=class_weight, dual=dual, fit_intercept=fit_intercept,
                                        intercept_scaling=intercept_scaling, loss=loss, max_iter=max_iter,
                                        multi_class=multi_class, penalty=penalty, random_state=random_state,
                                        tol=tol, verbose=verbose)

            pipe = sklearn.pipeline.make_pipeline(scaler, svc)
            Classifier.__init__(self, pipe)


        def reportDetails(self):

            svc = self.finalEstimator()
            report = Report('')
            return report


    class LinearSVCTuned(LinearSVC):

        def __init__(self, C=[0.001, 0.01, 0.1, 1, 10, 1000],
                       class_weight=None, dual=True, fit_intercept=True,
                       intercept_scaling=1, loss='squared_hinge', max_iter=1000,
                       multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
                       verbose=0,
                       copy=True, with_mean=True, with_std=True,
                       scoring='f1_weighted', fit_params=None,
                       n_jobs=1, iid=True, refit=True, cv=3,
                       pre_dispatch='2*n_jobs', error_score='raise'):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svc = sklearn.svm.LinearSVC(class_weight=class_weight, dual=dual, fit_intercept=fit_intercept,
                                        intercept_scaling=intercept_scaling, loss=loss, max_iter=max_iter,
                                        multi_class=multi_class, penalty=penalty, random_state=random_state,
                                        tol=tol, verbose=verbose)
            svcTuned = sklearn.grid_search.GridSearchCV(svc, param_grid=[{'C': C}],
                                                        scoring=scoring, fit_params=fit_params,
                                                        n_jobs=n_jobs, iid=iid, refit=refit, cv=cv,
                                                        pre_dispatch=pre_dispatch, error_score=error_score)

            pipe = sklearn.pipeline.make_pipeline(scaler, svcTuned)
            Classifier.__init__(self, pipe)


    class SVC(Classifier):

        def __init__(self, C=1.0, cache_size=200, class_weight=None, coef0=0.0,
            decision_function_shape=None, degree=3, gamma='auto', kernel='rbf',
            max_iter=-1, probability=False, random_state=None, shrinking=True,
            tol=0.001, verbose=False,
            copy=True, with_mean=True, with_std=True):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svc = sklearn.svm.SVC(C=C, cache_size=cache_size, class_weight=class_weight, coef0=coef0,
                                  decision_function_shape=decision_function_shape, degree=degree, gamma=gamma,
                                  kernel=kernel, max_iter=max_iter, probability=probability, random_state=random_state,
                                  shrinking=shrinking, tol=tol, verbose=verbose)

            pipe = sklearn.pipeline.make_pipeline(scaler, svc)
            Classifier.__init__(self, pipe)



        def reportDetails(self):

            svc = self.finalEstimator()

            report = Report('')
            report.append(ReportHeading('Information'))
            classNames = [''] + self.sample.mask.meta.getMetadataItem('class_names')[1:]
            nsv = ['<b>Number of Support Vectors</b>'] + list(svc.n_support_)
            table = Table([nsv], header_row=classNames)
            report.append(ReportTable(table))
            return report


    class SVCTuned(SVC):

        def __init__(self, C=[0.001, 0.01, 0.1, 1, 10, 1000], gamma=[0.001, 0.01, 0.1, 1, 10, 1000],
                 cache_size=200, class_weight=None, coef0=0.0,
                 decision_function_shape=None, degree=3,
                 max_iter=-1, probability=False, random_state=None, shrinking=True,
                 tol=0.001, verbose=False,
                 copy=True, with_mean=True, with_std=True,
                 scoring='f1_macro', fit_params=None,
                 n_jobs=1, iid=True, refit=True, cv=3,
                 pre_dispatch='2*n_jobs', error_score='raise'):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svc = sklearn.svm.SVC(cache_size=cache_size, class_weight=class_weight, coef0=coef0,
                                  decision_function_shape=decision_function_shape, degree=degree,
                                  kernel='rbf', max_iter=max_iter, probability=probability, random_state=random_state,
                                  shrinking=shrinking, tol=tol, verbose=verbose)
            svcTuned = sklearn.grid_search.GridSearchCV(svc, param_grid=[{'gamma': gamma, 'C': C}],
                                                        scoring=scoring, fit_params=fit_params,
                                                        n_jobs=n_jobs, iid=iid, refit=refit, cv=cv,
                                                        pre_dispatch=pre_dispatch, error_score=error_score)

            pipe = sklearn.pipeline.make_pipeline(scaler, svcTuned)
            Classifier.__init__(self, pipe)


    class RandomForestClassifier(Classifier):

        def __init__(self, bootstrap=True, class_weight=None, criterion='gini',
            max_depth=None, max_features='auto', max_leaf_nodes=None,
            min_samples_leaf=1, min_samples_split=2,
            min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
            oob_score=True, random_state=None, verbose=0,
            warm_start=False):

            rfc = sklearn.ensemble.RandomForestClassifier(bootstrap=bootstrap, class_weight=class_weight,
                    criterion=criterion, max_depth=max_depth, max_features=max_features, max_leaf_nodes=max_leaf_nodes,
                    min_samples_leaf=min_samples_leaf, min_samples_split=min_samples_split,
                    min_weight_fraction_leaf=min_weight_fraction_leaf, n_estimators=n_estimators, n_jobs=n_jobs,
                    oob_score=oob_score, random_state=random_state, verbose=verbose, warm_start=warm_start)

            pipe = sklearn.pipeline.make_pipeline(rfc)
            Classifier.__init__(self, pipe)


        def reportDetails(self):



            rfc = self.finalEstimator()



            report = Report('')
            report.append(ReportHeading('Information'))

            bandNames = [''] + self.sample.image.meta.getBandNames()
            data = numpy.round(rfc.feature_importances_, 4)*100
            rowHeaders = [['Feature Importance [%]']]
            report.append(ReportTable(data, rowHeaders=rowHeaders))

            if rfc.oob_score:
                report.append(ReportParagraph('### ToDo - insert out-of-bag accuracies ###', font_color='red'))
                fig = MH.RandomForestClassifier(rfc, self)
                report.append(ReportPlot(fig, 'Hello World'))

            return report





class Regressors():

    class LinearSVR(Regressor):

        def __init__(self, C=1.0, dual=True, epsilon=0.0, fit_intercept=True,
                  intercept_scaling=1.0, loss='epsilon_insensitive', max_iter=1000,
                  random_state=None, tol=0.0001, verbose=0,
                  copy=True, with_mean=True, with_std=True):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svr = sklearn.svm.LinearSVR(C=C, dual=dual, epsilon=epsilon, fit_intercept=fit_intercept,
                    intercept_scaling=intercept_scaling, loss=loss, max_iter=max_iter, random_state=random_state,
                    tol=tol, verbose=verbose)

            pipe = sklearn.pipeline.make_pipeline(scaler, svr)
            Regressor.__init__(self, pipe)


    class LinearSVRTuned(Regressor):

        def __init__(self, C=[0.001, 0.01, 0.1, 1, 10, 1000], epsilon=[0.0],
                       dual=True, fit_intercept=True,
                       intercept_scaling=1.0, loss='epsilon_insensitive', max_iter=1000,
                       random_state=None, tol=0.0001, verbose=0,
                       copy=True, with_mean=True, with_std=True,
                       scoring='mean_absolute_error', fit_params=None,
                       n_jobs=1, iid=True, refit=True, cv=3,
                       pre_dispatch='2*n_jobs', error_score='raise'):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svr = sklearn.svm.LinearSVR(dual=dual, fit_intercept=fit_intercept,
                    intercept_scaling=intercept_scaling, loss=loss, max_iter=max_iter, random_state=random_state,
                    tol=tol, verbose=verbose)
            svrTuned = sklearn.grid_search.GridSearchCV(svr, param_grid=[{'C': C, 'epsilon':epsilon}],
                                                        scoring=scoring, fit_params=fit_params,
                                                        n_jobs=n_jobs, iid=iid, refit=refit, cv=cv,
                                                        pre_dispatch=pre_dispatch, error_score=error_score)

            pipe = sklearn.pipeline.make_pipeline(scaler, svrTuned)
            Regressor.__init__(self, pipe)


    class SVR(Regressor):

        def __init__(self, C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma='auto',
            kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False,
            copy=True, with_mean=True, with_std=True):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svr = sklearn.svm.SVR(C=C, cache_size=cache_size, coef0=coef0, degree=degree, epsilon=epsilon, gamma=gamma,
                                  kernel=kernel, max_iter=max_iter, shrinking=shrinking, tol=tol, verbose=verbose)

            pipe = sklearn.pipeline.make_pipeline(scaler, svr)
            Regressor.__init__(self, pipe)


    class SVRTuned(Regressor):

        def __init__(self, C=[0.001, 0.01, 0.1, 1, 10, 1000], gamma=[0.001, 0.01, 0.1, 1, 10, 1000], epsilon=[0.1],
                 cache_size=200, coef0=0.0, degree=3,
                 max_iter=-1, shrinking=True, tol=0.001, verbose=False,
                 copy=True, with_mean=True, with_std=True,
                 scoring='mean_absolute_error', fit_params=None,
                 n_jobs=1, iid=True, refit=True, cv=3,
                 pre_dispatch='2*n_jobs', error_score='raise'):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            svr = sklearn.svm.SVR(cache_size=cache_size, coef0=coef0, degree=degree,
                                  max_iter=max_iter, shrinking=shrinking, tol=tol, verbose=verbose)
            svrTuned = sklearn.grid_search.GridSearchCV(svr, param_grid=[{'gamma': gamma, 'C': C, 'epsilon': epsilon}],
                                                        scoring=scoring, fit_params=fit_params,
                                                        n_jobs=n_jobs, iid=iid, refit=refit, cv=cv,
                                                        pre_dispatch=pre_dispatch, error_score=error_score)

            pipe = sklearn.pipeline.make_pipeline(scaler, svrTuned)
            Regressor.__init__(self, pipe)


    class RandomForestRegressor(Regressor):

        def __init__(self, bootstrap=True, criterion='mse', max_depth=None,
                              max_features='auto', max_leaf_nodes=None, min_samples_leaf=1,
                              min_samples_split=2, min_weight_fraction_leaf=0.0,
                              n_estimators=10, n_jobs=1, oob_score=False, random_state=None,
                              verbose=0, warm_start=False):

            rfr = sklearn.ensemble.RandomForestRegressor(bootstrap=bootstrap, criterion=criterion, max_depth=max_depth,
                    max_features=max_features, max_leaf_nodes=max_leaf_nodes, min_samples_leaf=min_samples_leaf,
                    min_samples_split=min_samples_split, min_weight_fraction_leaf=min_weight_fraction_leaf,
                    n_estimators=n_estimators, n_jobs=n_jobs, oob_score=oob_score, random_state=random_state,
                    verbose=verbose, warm_start=warm_start)

            pipe = sklearn.pipeline.make_pipeline(rfr)
            Regressor.__init__(self, pipe)


    class LinearRegression(Regressor):

        def __init__(self, copy_X=True, fit_intercept=True, n_jobs=1, normalize=True):

            linearRegression = sklearn.linear_model.LinearRegression(copy_X=copy_X, fit_intercept=fit_intercept, n_jobs=n_jobs,
                                                    normalize=normalize)

            pipe = sklearn.pipeline.make_pipeline(linearRegression)
            Regressor.__init__(self, pipe)


class Clusterers():

    class KMeans(Clusterer):

        def __init__(self, copy_x=True, init='k-means++', max_iter=300, n_clusters=8, n_init=10,
               n_jobs=1, precompute_distances='auto', random_state=None, tol=0.0001, verbose=0,
               copy=True, with_mean=True, with_std=True):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            kMeans = sklearn.cluster.KMeans(copy_x=copy_x, init=init, max_iter=max_iter, n_clusters=n_clusters,
                                            n_init=n_init, n_jobs=n_jobs, precompute_distances=precompute_distances,
                                            random_state=random_state, tol=tol, verbose=verbose)

            pipe = sklearn.pipeline.make_pipeline(scaler, kMeans)
            Clusterer.__init__(self, pipe)


        def reportDetails(self):

            kMeans = self.finalEstimator()

            import numpy as np
            import matplotlib.pyplot as plt

            for spectra in kMeans.cluster_centers_:
                x = self.sample.image.meta.getMetadataItem('wavelength')
                y = spectra
                plt.plot(x, y)
                plt.show()

            report = Report('')
            report.append(ReportHeading('Information'))
#            bandNames = [''] + [str(i) + '. PC' for i in range(1, pca.n_components_ + 1)]

         #   explainedVariance = ['<b>Explained Variance [%]</b>'] + list(
         #       numpy.round(pca.explained_variance_ratio_ * 100, 2))
        #    cumulatedExplainedVariance = ['<b>Cumulated Explained Variance [%]</b>'] + list(
         #       numpy.round(numpy.cumsum(pca.explained_variance_ratio_) * 100, 2))

        #    table = Table([explainedVariance, cumulatedExplainedVariance], header_row=bandNames)
        #    report.append(ReportTable(table))
            return report


class Transformers():

    class PCA(Transformer):

        def __init__(self, copy=True, n_components=0.999, whiten=False):

            pca = sklearn.decomposition.PCA(copy=copy, n_components=n_components, whiten=whiten)
            pipe = sklearn.pipeline.make_pipeline(pca)
            Transformer.__init__(self, pipe)


        def transformMeta(self, meta, iimeta, immeta):

            Transformer.transformMeta(self, meta, iimeta, immeta)
            meta.setBandNames([str(i) + '. PC' for i in range(1, meta.RasterCount+1)])


        def reportDetails(self):

            pca = self.finalEstimator()

            report = Report('')
            report.append(ReportHeading('Information'))
            bandNames = [''] + [str(i) + '. PC' for i in range(1, pca.n_components_+1)]

            explainedVariance = ['<b>Explained Variance [%]</b>'] + list(numpy.round(pca.explained_variance_ratio_ * 100, 2))
            cumulatedExplainedVariance = ['<b>Cumulated Explained Variance [%]</b>'] + list(numpy.round(numpy.cumsum(pca.explained_variance_ratio_) * 100, 2))

            table = Table([explainedVariance, cumulatedExplainedVariance], header_row=bandNames)
            report.append(ReportTable(table))
            return report


    class KernelPCA(Transformer):

        def __init__(self, alpha=1.0, coef0=1, degree=3, eigen_solver='auto',
                     fit_inverse_transform=False, gamma=None, kernel='linear',
                     kernel_params=None, max_iter=None, n_components=None,
                     remove_zero_eig=False, tol=0,
                     copy=True, with_mean=False, with_std=False):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
            kpca = sklearn.decomposition.KernelPCA(alpha=alpha, coef0=coef0, degree=degree, eigen_solver=eigen_solver,
                     fit_inverse_transform=fit_inverse_transform, gamma=gamma, kernel=kernel,
                     kernel_params=kernel_params, max_iter=max_iter, n_components=n_components,
                     remove_zero_eig=remove_zero_eig, tol=tol)
            pipe = sklearn.pipeline.make_pipeline(scaler, kpca)
            Transformer.__init__(self, pipe)


        def transformMeta(self, meta, iimeta, immeta):

            Transformer.transformMeta(self, meta, iimeta, immeta)
            meta.setBandNames([str(i) + '. kernelPC' for i in range(1, meta.RasterCount+1)])


        def reportDetails(self):

            kpca = self.finalEstimator()

            report = Report('')
            report.append(ReportHeading('Information'))
            n_components = kpca.lambdas_.size
            bandNames = [''] + [str(i) + '. KernelPC' for i in range(1, n_components+1)]
            explainedVariance = ['<b>Explained Variance [%]</b>'] + list(numpy.round(kpca.lambdas_/kpca.lambdas_.sum() * 100, 2))
            cumulatedExplainedVariance = ['<b>Cumulated Explained Variance [%]</b>'] + list(numpy.round(numpy.cumsum(kpca.lambdas_/kpca.lambdas_.sum()) * 100, 2))

            table = Table([explainedVariance, cumulatedExplainedVariance], header_row=bandNames)
            report.append(ReportTable(table))
            return report


    class FastICA(Transformer):

        def __init__(self, algorithm='parallel', fun='logcosh', fun_args=None, max_iter=200,
                n_components=None, random_state=None, tol=0.0001, w_init=None,
                whiten=True):

            ica = sklearn.decomposition.FastICA(algorithm=algorithm, fun=fun, fun_args=fun_args, max_iter=max_iter,
                                                n_components=n_components, random_state=random_state, tol=tol,
                                                w_init=w_init, whiten=whiten)

            pipe = sklearn.pipeline.make_pipeline(ica)
            Transformer.__init__(self, pipe)


        def transformMeta(self, meta, iimeta, immeta):

            Transformer.transformMeta(self, meta, iimeta, immeta)
            meta.setBandNames([str(i) + '. Independent Component' for i in range(1, meta.RasterCount+1)])


        def reportDetails(self):

            # anything to report?
            ica = self.finalEstimator()
            report = Report('')
            #report.append(ReportHeading('Information'))
            return report


    class StandardScaler(Transformer):

        def __init__(self, copy=True, with_mean=True, with_std=True):

            scaler = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)

            pipe = sklearn.pipeline.make_pipeline(scaler)
            Transformer.__init__(self, pipe)

        def transformMeta(self, meta, iimeta, immeta):

            Transformer.transformMeta(self, meta, iimeta, immeta)
            meta.setBandNames(iimeta.getMetadataItem('band names'))


    class RobustScaler(Transformer):

        def __init__(self, copy=True, with_centering=True, with_scaling=True):

            scaler = sklearn.preprocessing.RobustScaler(copy=copy, with_centering=with_centering, with_scaling=with_scaling)
            pipe = sklearn.pipeline.make_pipeline(scaler)
            Transformer.__init__(self, pipe)


        def reportDetails(self):

            scaler = self.finalEstimator()

            report = Report('')
            report.append(ReportHeading('Information'))
            bandNames = self.sample.image.meta.getBandNames()
            table = Table([['<b>Median</b>']+list(scaler.center_),
                           ['<b>Interquartile Range</b>']+list(scaler.scale_)], header_row=['']+bandNames)
            report.append(ReportTable(table))
            return report


class SklearnClassifiers:

    class UncertaintyClassifier(sklearn.ensemble.RandomForestClassifier):

        def __init__(self, sklClassifier, mode, n_estimators=100, n_jobs=1):

            assert mode in ['fp', 'fn']
            self.mode = mode
            self.sklClassifier = sklClassifier
            sklearn.ensemble.RandomForestClassifier.__init__(self, oob_score=True, n_estimators=n_estimators, n_jobs=n_jobs)


        def fit(self, X, y, fit_params=None):

            # get cross validation predictions
            yCV = sklearn.cross_validation.cross_val_predict(self.sklClassifier, X, y, fit_params=fit_params, cv = 10)

            # create confusion class training set and fit random forest that models the confusion
            confused = y != yCV
            yFalse = numpy.zeros_like(y)
            if self.mode == 'fn':
                yFalse[confused] = y[confused]
            elif self.mode == 'fp':
                yFalse[confused] = yCV[confused]

            sklearn.ensemble.RandomForestClassifier.fit(self, X, yFalse)


class SklearnRegressors:

    class UncertaintyRegressor(sklearn.ensemble.RandomForestRegressor):

        def __init__(self, sklRegressor, n_estimators=100, n_jobs=1):

            self.sklRegressor = sklRegressor
            sklearn.ensemble.RandomForestRegressor.__init__(self, oob_score=True, n_estimators=n_estimators, n_jobs=n_jobs)


        def fit(self, X, y, fit_params=None):

            # get cross validation predictions
            yCV = sklearn.cross_validation.cross_val_predict(self.sklRegressor, X, y, fit_params=fit_params, cv = 10)

            # create confusion class training set and fit random forest that models the confusion
            yError = numpy.abs(y-yCV)
            sklearn.ensemble.RandomForestRegressor.fit(self, X, yError)


class MH:

    @staticmethod
    def RandomForestClassifier(rfc, self):

        wl = self.sample.image.meta.getMetadataItem('wavelength')
        fig, ax = plt.subplots(facecolor='white')

        #plt.vlines(numpy.arange(rfc.n_features_)+1,0,rfc.feature_importances_*100)
        plt.vlines(wl,0,rfc.feature_importances_*100)

        plt.ylabel('Variable Importance')
        plt.xlabel('Variable Index')
        return fig
       # ax1 = fig.add_subplot(211)
        #ax1.xcorr(rfc.feature_importances_*100, rfc.feature_importances_*100, usevlines=True, maxlags=50, normed=True, lw=2)
  #self.sample.image.meta.getMetadataItem('wavelength', default=range(1, rfc.n_features_+1))

if __name__ == '__main__':



    for est in all(Classifiers)+all(Regressors):
        print est.name()
