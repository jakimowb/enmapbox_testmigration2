
from enmapbox.testing import TestCase



class Scripts(TestCase):

    def test_createProfiles(self):

        from enmapbox.gui import SpectralLibrary, SpectralProfile
        from enmapbox.gui.utils import file_search
        from enmapbox.externals.qps.speclib.io.asd import ASDSpectralLibraryIO, ASDBinaryFile
        import pathlib
        import os
        import numpy as np

        # Ordner mit den '*.asd.ref' Dateien
        dirRefl = pathlib.Path(r'F:\Temp\SPJ_Greifswald\Feldspektren') / 'Reflexion'
        # CSV mit den Angaben der Mischungen
        pathMixRecipe = pathlib.Path(__file__).parent / 'mischungen.csv'

        assert dirRefl.is_dir()
        assert pathMixRecipe.is_file()
        pathMixResultGPKG = pathMixRecipe.parent / 'mischungsergebnisse.gpkg'
        pathMixResultCSV  = pathMixRecipe.parent / 'mischungsergebnisse.csv'

        asd_files_ref = list(file_search(dirRefl, '*.asd.ref', recursive=True))

        rezept = np.recfromcsv(pathMixRecipe, encoding='utf-8')
        gruppen = np.unique(rezept.gruppe)

        speclib = SpectralLibrary()
        speclib.startEditing()

        for gruppe in gruppen:
            print(f'Mische Gruppe {gruppe}')
            i_grp = np.where(rezept.gruppe == gruppe)[0]
            basenames = [f'{n}.asd.ref' for n in rezept.basename[i_grp]]
            weights = rezept.gewicht[i_grp]
            nweights = weights / weights.sum()
            description = rezept.beschreibung[i_grp]
            asd_files = [p for p in asd_files_ref if os.path.basename(p) in basenames]
            profiles = ASDSpectralLibraryIO.readFrom(asd_files)
            assert len(profiles) == len(asd_files)
            for p, d in zip(profiles, description):
                if d != '':
                    p.setName(f'{p.name()} {d}')

            #speclib.addProfiles(profiles)

            mixed_profile = sum([p*w for p, w in zip(profiles, nweights)])
            assert isinstance(mixed_profile, SpectralProfile)
            mixed_profile.setName(f'Mischung Gruppe {gruppe}')
            speclib.addProfiles(mixed_profile)

        speclib.commitChanges()
        speclib.write(pathMixResultGPKG)
        speclib.write(pathMixResultCSV)


