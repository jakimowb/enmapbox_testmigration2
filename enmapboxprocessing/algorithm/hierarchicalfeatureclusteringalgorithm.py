from collections import defaultdict, OrderedDict
from os.path import basename
from typing import Dict, Any, List, Tuple

#import matplotlib.pyplot as plt
import matplotlib.pyplot as plt, mpld3
import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback)
from scipy.cluster import hierarchy
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.reportwriter import MultiReportWriter, HtmlReportWriter, CsvReportWriter
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class HierarchicalFeatureClusteringAlgorithm(EnMAPProcessingAlgorithm):
    P_SAMPLE, _SAMPLE = 'sample', 'Sample'
    P_N, _N = 'n', 'Number of clusters'
    P_NO_PLOT, _NO_PLOT = 'noPlot', 'Skip plotting'
    P_OUTPUT_SAMPLE, _OUTPUT_SAMPLE = 'outputSample', 'Output sample'
    P_OUTPUT_REPORT, _OUTPUT_REPORT = 'outputReport', 'Output report'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._SAMPLE, 'Sample (*.pkl) file.'),
            (self._N, 'Number of clusters used '),
            (self.P_NO_PLOT, 'Skip the creation of plots, which can take a lot of time for very big features sets.'),
            (self._OUTPUT_SAMPLE, 'Output sample destination *.pkl file.'),
            (self._OUTPUT_REPORT, 'Output report *.html file.')
        ]

    def displayName(self) -> str:
        return 'Hierarchical feature clustering'

    def shortDescription(self) -> str:
        return 'Evaluate feature multicollinearity by performing hierarchical/agglomerative clustering with Ward linkage using Spearman rank-order correlation as distance between features. ' \
               'After a first dry-run the can user manually pick a suitable threshold by visual inspection of the output report to group the features into clusters. ' \
               'In a second run, the user specifies the number of clusters. For each cluster the most representative feature is selected for subsetting the input sample.\n' \
               'Note that a JSON sidecar file is placed next to the output report, including additional results for further analysis.'


    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_SAMPLE, self._SAMPLE, extension='pkl')
        self.addParameterInt(self.P_N, self._N, None, True, 1)
        self.addParameterBoolean(self.P_NO_PLOT, self._NO_PLOT, False, False, True)
        self.addParameterFileDestination(self.P_OUTPUT_SAMPLE, self._OUTPUT_SAMPLE, 'Pickle (*.pkl)', None, True, False)
        self.addParameterFileDestination(self.P_OUTPUT_REPORT, self._OUTPUT_REPORT, 'Report file (*.html)')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameSample = self.parameterAsFile(parameters, self.P_SAMPLE, context)
        n = self.parameterAsInt(parameters, self.P_N, context)
        noPlot = self.parameterAsBoolean(parameters, self.P_NO_PLOT, context)
        filenameOutputSample = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_REPORT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            dumpJson = OrderedDict()
            dump = Utils.pickleLoad(filenameSample)
            X = dump['X']
            features = dump['features']
            feedback.pushInfo(f'Load sample data: X{list(X.shape)}')
            feedback.pushInfo('Performing hierarchical clustering')
            corr = spearmanr(X).correlation**2
            corr_linkage = hierarchy.ward(corr)
            #corr_linkage = hierarchy.linkage(corr, method='single', metric='euclidean')
            dumpJson['feature_names'] = features
            dumpJson['squared_spearmanr'] = corr.copy()
            dumpJson['ward_linkage'] = corr_linkage

            # prepare results
            clusterTable = list()
            fig3_values = list()
            fig4_values = list()
            flat_clusters = list()
            feature_subsets = list()
            for i, t in enumerate(reversed(corr_linkage[:, 2])):
                fcluster = hierarchy.fcluster(corr_linkage, t, criterion='distance')

                flat_clusters.append(fcluster)
                clusterTable.append(list(fcluster))
                cluster_id_to_feature_ids = defaultdict(list)
                for idx, cluster_id in enumerate(fcluster):
                    cluster_id_to_feature_ids[cluster_id].append(idx)

                selected_features = [v for v in cluster_id_to_feature_ids.values()]
                selected_features_mean_intra_cluster_corr = [list(np.nanmean(corr[v][:, v], axis=0)) for v in selected_features]
                featureSubset = [f[np.argmax(c)] for f, c in zip(selected_features, selected_features_mean_intra_cluster_corr)]
                feature_subsets.append(featureSubset)

                # inter-cluster corr
                values = list()
                for i1, f1 in enumerate(featureSubset):
                    for i2, f2 in enumerate(featureSubset):
                        if i1 != i2:
                            values.append(corr[f1, f2])
                fig3_values.append(values)

                # intra-cluster corr
                values = list()
                for fs in selected_features:
                    for i1, f1 in enumerate(fs):
                        for i2, f2 in enumerate(fs):
                            if i1 != i2:
                                values.append(corr[f1, f2])
                fig4_values.append(values)

            # supervised performance
            y = dump['y'].ravel()
            feature_subset_score = list()
            if 0:#'targets' in dump:  # regression sample
                feedback.pushInfo('Calculate supervised performance')
                #estimator = RandomForestRegressor(n_estimators=100, oob_score=True, n_jobs=8, random_state=42)
                estimator = LinearRegression(normalize=True)
                score_name = 'root mean squared error'
                estimator_name = 'LinearRegression'
                def score():
                    return np.sqrt(mean_squared_error(y_test, y_predicted))
            if 0:#'categories' in dump:  # classification sample
                feedback.pushInfo('Calculate supervised RandomForestClassifier out-of-bag score')
                estimator = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
                score_name = 'f1 macro score'
                estimator_name = 'LogisticRegression'
                def score():
                    return f1_score(y_test, y_predicted, average='macro')

            if 0:
                test_size = train_size = min(1000, len(X) // 2)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, train_size=train_size)
                for i, feature_subset in enumerate(feature_subsets):
                    feedback.setProgress(i / len(feature_subsets))
                    X_train_i = X_train[:, feature_subset]
                    X_test_i = X_test[:, feature_subset]
                    estimator.fit(X_train_i, y_train)
                    y_predicted = estimator.predict(X_test_i)
                    feature_subset_score.append(score())
                    print(len(feature_subset), feature_subset_score[-1])

            dumpJson['feature_subset_oob'] = flat_clusters
            dumpJson['flat_clusters'] = flat_clusters
            dumpJson['feature_subsets'] = feature_subsets

            Utils.jsonDump(dumpJson, filename + '.json')

            if not noPlot:
                feedback.pushInfo('Plot dendrogamm')
                figsizeX = len(features) * 0.15 + 5
                figsizeY = 10
                fig, ax = plt.subplots(figsize=(figsizeX, figsizeY))
                plt.title('Feature clustering dendrogram')
                dendro = hierarchy.dendrogram(
                    corr_linkage, orientation='bottom', labels=features, ax=ax, leaf_rotation=90,leaf_font_size=10
                )
                plt.ylabel('Ward inter-cluster distance')
                fig.tight_layout()
                filenameFig1 = filename + '.fig1.svg'
                #fig.savefig(filenameFig1, format='svg')
                #mpld3.show(fig)
                #exit()

                feedback.pushInfo('Plot correlation matrix')
                figsizeX = len(features) * 0.15 + 5
                figsizeY = len(features) * 0.15 + 5
                fig, ax = plt.subplots(figsize=(figsizeX, figsizeY))
                plt.title('squared Spearman rank-order correlation matrix')
                dendro_idx = np.arange(0, len(dendro['ivl']))
                im = ax.imshow(corr[dendro['leaves'], :][:, dendro['leaves']], cmap='jet')
                ax.set_xticks(dendro_idx)
                ax.set_yticks(dendro_idx)
                ax.set_xticklabels(dendro['ivl'], rotation='vertical')
                ax.set_yticklabels(dendro['ivl'])
                plt.xticks(fontsize=10)
                plt.yticks(fontsize=10)
                plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)  # the numbers here are quite magic, but do work :-)
                fig.tight_layout()
                filenameFig2 = filename + '.fig2.svg'
                fig.savefig(filenameFig2, format='svg')
                #mpld3.show(fig)
                plt.show()
                exit()

                feedback.pushInfo('Plot inter-cluster similarity')
                figsizeX = 10
                figsizeY = len(features) * 0.15 + 1
                fig, ax = plt.subplots(figsize=(figsizeX, figsizeY))
                plt.title('Inter-cluster correlation distribution')
                plt.xlabel(f'squared Spearman rank-order correlation')
                plt.ylabel(f'number of clusters')
                ax.boxplot(fig3_values,
                    vert=False, sym='',
                    labels=[f'n={i + 1}' for i in range(len(features) - 1)],
                )
                fig.tight_layout()
                filenameFig3 = filename + '.fig3.svg'
                #fig.savefig(filenameFig3, format='svg')

                #plt.plot([3,1,4,1,5], 'ks-', mec='w', mew=5, ms=20)
                mpld3.show(fig)
                exit()

                feedback.pushInfo('Plot intra-cluster similarity')
                figsizeX = 10
                figsizeY = len(features) * 0.15 + 1
                fig, ax = plt.subplots(figsize=(figsizeX, figsizeY))
                plt.title('Intra-cluster correlation distribution')
                plt.xlabel(f'squared Spearman rank-order correlation')
                plt.ylabel(f'number of clusters')
                ax.boxplot(fig4_values,
                    vert=False, sym='',
                    labels=[f'n={i + 1}' for i in range(len(features) - 1)],
                )
                fig.tight_layout()
                filenameFig4 = filename + '.fig4.svg'
                fig.savefig(filenameFig4, format='svg')

                feedback.pushInfo('Plot supervised performance')
                figsizeX = 10
                figsizeY = len(features) * 0.15 + 1
                fig, ax = plt.subplots(figsize=(figsizeX, figsizeY))
                plt.title(f'Supervised {estimator_name} performance')
                plt.xlabel(score_name)
                plt.ylabel(f'number of clusters')
                ax.plot(feature_subset_score, range(1, len(feature_subset_score)+1))
                plt.yticks(
                    ticks=range(1, len(feature_subset_score)+1),
                    labels=[f'n={i + 1}' for i in range(len(features) - 1)]
                )
                fig.tight_layout()
                filenameFig5 = filename + '.fig5.svg'
                mpld3.show(fig)
                exit()
                fig.savefig(filenameFig5, format='svg')


            with \
                    open(filename, 'w') as fileHtml, \
                    open(filename + '.csv', 'w') as fileCsv:
                report = MultiReportWriter([HtmlReportWriter(fileHtml), CsvReportWriter(fileCsv)])
                report.writeHeader('Hierarchical feature clustering')
                linkWard = self.htmlLink(
                    'https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.ward.html',
                    'scipy.cluster.hierarchy.ward',
                )
                linkSpearmanr = self.htmlLink(
                    'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html',
                    'scipy.stats.spearmanr'
                )
                report.writeParagraph(f'Linkage methode: Ward (see {linkWard})')
                report.writeParagraph(f'Distance metric: squared Spearman rank-order correlation (see {linkSpearmanr})')
                if not noPlot:
                    report.writeImage(basename(filenameFig2))
                    report.writeImage(basename(filenameFig1))
                    report.writeImage(basename(filenameFig3))
                    report.writeImage(basename(filenameFig4))
                    report.writeImage(basename(filenameFig5))



                #values = np.transpose(clusterTable).tolist()
                #report.writeTable(
                #    values,
                #    'Cluster assignment by number of clusters n',
                #    [f'n={i+1}' for i in range(len(features) - 1)],
                #    features)

                values = feature_subsets
                rowHeaders = [f'n={i+1}' for i, v in enumerate(feature_subsets)]
                rowHeaders[0] = 'n=1'
                report.writeTable(
                    values,
                    f'Selected features (zero-based index)',
                    None,
                    rowHeaders,
                )

                report.writeParagraph(
                    f'Report design was inspired by {self.htmlLink("https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance_multicollinear.html#sphx-glr-auto-examples-inspection-plot-permutation-importance-multicollinear-py", "Permutation Importance with Multicollinear or Correlated Features")}.'
                )

            result = {self.P_OUTPUT_REPORT: filename}

            if n is not None and filenameOutputSample is not None:
                subset = feature_subsets[n]
                feedback.pushInfo()
                dump['X'] = dump['X'][:, subset]
                dump['features'] = dump['features'][subset]
                Utils.pickleDump(dump, filenameOutputSample)
                result[self.P_OUTPUT_SAMPLE] = filenameOutputSample

            self.toc(feedback, result)

        return result
