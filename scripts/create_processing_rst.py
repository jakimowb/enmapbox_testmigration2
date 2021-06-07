from os import makedirs
from os.path import abspath, join, dirname, exists, basename
from shutil import rmtree

from qgis._core import QgsProcessingParameterDefinition, QgsProcessingDestinationParameter

from enmapboxgeoalgorithms.algorithms import ALGORITHMS
from enmapboxgeoalgorithms.provider import EnMAPAlgorithm as EnMAPAlgorithmV1, Help as HelpV1, Cookbook as CookbookV1
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm
from hubdsm.processing.enmapalgorithm import EnMAPAlgorithm as EnMAPAlgorithmV2, Help as HelpV2


def generateRST():
    # create folder
    root = abspath(join(dirname(__file__), '..', 'doc', 'source', 'usr_section', 'usr_manual', 'processing_algorithms'))
    print(root)

    if exists(root):
        print('Delete root folder')
        rmtree(root)
    makedirs(root)

    groups = dict()

    nalg = 0
    for alg in ALGORITHMS:
        # print(alg.displayName())
        if alg.group() not in groups:
            groups[alg.group()] = dict()
        groups[alg.group()][alg.displayName()] = alg
        nalg += 1

    print(f'Found {nalg} algorithms.')

    textProcessingAlgorithmsRst = '''Processing Algorithms
*********************
    
.. toctree::
    :maxdepth: 1
       
'''

    for gkey in sorted(groups.keys()):

        # create group folder
        groupId = gkey.lower()
        for c in ' ,*':
            groupId = groupId.replace(c, '_')
        groupFolder = join(root, groupId)
        makedirs(groupFolder)

        textProcessingAlgorithmsRst += '\n    {}/index.rst'.format(basename(groupFolder))

        # create group index.rst
        text = '''.. _{}:\n\n{}
{}

.. toctree::
   :maxdepth: 0
   :glob:

   *
'''.format(gkey, gkey, '=' * len(gkey))
        filename = join(groupFolder, 'index.rst')
        with open(filename, mode='w') as f:
            f.write(text)

        for akey in groups[gkey]:

            algoId = akey.lower()
            for c in [' ']:
                algoId = algoId.replace(c, '_')

            text = '''.. _{}:

{}
{}
{}

'''.format(akey, '*' * len(akey), akey, '*' * len(akey))

            alg = groups[gkey][akey]
            print(alg)
            if isinstance(alg, EnMAPAlgorithmV1):
                alg.defineCharacteristics()
                text = v1(alg, text)
            elif isinstance(alg, EnMAPAlgorithmV2):
                alg.defineCharacteristics()
                text = v2(alg, text)
            elif isinstance(alg, EnMAPProcessingAlgorithm):
                alg.initAlgorithm()
                text = v3(alg, text)
            else:
                print(f'skip {alg}')
                continue
                # assert 0

            filename = join(groupFolder, '{}.rst'.format(algoId))
            for c in r'/()':
                filename = filename.replace(c, '_')
            with open(filename, mode='w') as f:
                f.write(text)

    filename = join(root, 'processing_algorithms.rst')
    with open(filename, mode='w') as f:
        f.write(textProcessingAlgorithmsRst)
    print('created RST file: ', filename)


def v1(alg, text):
    if isinstance(alg.description(), str):
        text += alg.description() + '\n\n'
    if isinstance(alg.description(), HelpV1):
        text += alg.description().rst() + '\n\n'
    if len(alg.cookbookRecipes()) > 0:
        text += alg.cookbookDescription() + ' \n'
        for i, key in enumerate(alg.cookbookRecipes()):
            url = CookbookV1.url(key)
            text += '`{} <{}>`_\n'.format(key, url)
            if i < len(alg.cookbookRecipes()) - 1:
                text += ', '
        text += '\n'
    text += '**Parameters**\n\n'
    outputsHeadingCreated = False
    for pd in alg.parameterDefinitions():
        assert isinstance(pd, QgsProcessingParameterDefinition)

        if not outputsHeadingCreated and isinstance(pd, QgsProcessingDestinationParameter):
            text += '**Outputs**\n\n'
            outputsHeadingCreated = True

        text += '\n:guilabel:`{}` [{}]\n'.format(pd.description(), pd.type())

        if False:  # todo pd.flags() auswerten
            text += '    Optional\n'

        if isinstance(pd._help, str):
            pdhelp = pd._help
        if isinstance(pd._help, HelpV1):
            pdhelp = pd._help.rst()

        for line in pdhelp.split('\n'):
            text += '    {}\n'.format(line)

        text += '\n'

        # if pd.type() == 'fileDestination':
        #    a=1

        if pd.defaultValue() is not None:
            if isinstance(pd.defaultValue(), str) and '\n' in pd.defaultValue():
                text += '    Default::\n\n'
                for line in pd.defaultValue().split('\n'):
                    text += '        {}\n'.format(line)
            else:
                text += '    Default: *{}*\n\n'.format(pd.defaultValue())
    return text


def v2(alg, text):
    if isinstance(alg.description(), str):
        text += alg.description() + '\n\n'
    if isinstance(alg.description(), HelpV2):
        text += alg.description().rst() + '\n\n'
    if len(alg.cookbookRecipes()) > 0:
        text += alg.cookbookDescription() + ' \n'
        for i, key in enumerate(alg.cookbookRecipes()):
            url = CookbookV1.url(key)
            text += '`{} <{}>`_\n'.format(key, url)
            if i < len(alg.cookbookRecipes()) - 1:
                text += ', '
        text += '\n'
    text += '**Parameters**\n\n'
    outputsHeadingCreated = False
    for pd in alg.parameterDefinitions():
        assert isinstance(pd, QgsProcessingParameterDefinition)

        if not outputsHeadingCreated and isinstance(pd, QgsProcessingDestinationParameter):
            text += '**Outputs**\n\n'
            outputsHeadingCreated = True

        text += '\n:guilabel:`{}` [{}]\n'.format(pd.description(), pd.type())

        if False:  # todo pd.flags() auswerten
            text += '    Optional\n'

        if isinstance(pd.help, str):
            pdhelp = pd.help
        if isinstance(pd.help, HelpV2):
            pdhelp = pd.help.rst()

        for line in pdhelp.split('\n'):
            text += '    {}\n'.format(line)

        text += '\n'

        # if pd.type() == 'fileDestination':
        #    a=1

        if pd.defaultValue() is not None:
            if isinstance(pd.defaultValue(), str) and '\n' in pd.defaultValue():
                text += '    Default::\n\n'
                for line in pd.defaultValue().split('\n'):
                    text += '        {}\n'.format(line)
            else:
                text += '    Default: *{}*\n\n'.format(pd.defaultValue())
    return text


def v3(alg: EnMAPProcessingAlgorithm, text):
    try:
        helpParameters = {k: v for k, v in alg.helpParameters()}
    except:
        assert 0

    text += alg.shortDescription() + '\n\n'

    text += '**Parameters**\n\n'
    outputsHeadingCreated = False
    for pd in alg.parameterDefinitions():
        assert isinstance(pd, QgsProcessingParameterDefinition)

        if not outputsHeadingCreated and isinstance(pd, QgsProcessingDestinationParameter):
            text += '**Outputs**\n\n'
            outputsHeadingCreated = True

        text += '\n:guilabel:`{}` [{}]\n'.format(pd.description(), pd.type())

        if False:  # todo pd.flags() auswerten
            text += '    Optional\n'

        pdhelp = helpParameters.get(pd.description(), 'undocumented')

        if pdhelp == 'undocumented':
            assert 0, pd.description()

        for line in pdhelp.split('\n'):
            text += '    {}\n'.format(line)

        text += '\n'

        # if pd.type() == 'fileDestination':
        #    a=1

        if pd.defaultValue() is not None:
            if isinstance(pd.defaultValue(), str) and '\n' in pd.defaultValue():
                text += '    Default::\n\n'
                for line in pd.defaultValue().split('\n'):
                    text += '        {}\n'.format(line)
            else:
                text += '    Default: *{}*\n\n'.format(pd.defaultValue())
    return text


if __name__ == '__main__':
    generateRST()
