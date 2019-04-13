# EnMAP-Box 3

![build status](https://img.shields.io/bitbucket/pipelines/hu-geomatics/enmap-box.svg)

![Logo](enmapbox/gui/ui/icons/enmapbox.svg)

The EnMAP-Box is free and open source [QGIS Plugin ](https://www.qgis.org) to visualize and process remote sensing raster data. It is particularly developed to handle imaging spectroscopy data, as from the upcoming EnMAP sensor.

![Screenshot](doc/source/img/screenshot_main2.png)

# Highlights:

* an easy-to-use graphical user interface for the visualization of vector and raster data sources in parallel and in spatially linked maps

* collection and visualisation of spectral profiles spectral libraries. Spectral profiles can come from different sources, e.g. raster images, field spectrometer or table-sheets.

* enhances the QGIS Processing Framework with many algorithms commonly used in
  remote sensing and imaging spectroscopy, e.g. support vector machines or random forest based raster classification, regession, cluster approaches from the [scikit-learn](https://scikit-learn.org/stable/index.html) library.

* applications specific to imaging spectroscopy and the EnMAP program, e.g. a simulation of spectral profiles (IIVM), atmospheric correction of EnMAP data, mapping of geological classes from EnMAP data and more...


Documentation: http://enmap-box.readthedocs.io

Git Repository: https://bitbucket.org/hu-geomatics/enmap-box


## License

The EnMAP-Box is released under the GNU Public License (GPL) Version 3 or above. A copy of this licence can be found in the LICENSE.txt file that is part of the EnMAP-Box plugin folder and the EnMAP-Box repository, and also at
<http://www.gnu.org/licenses/>

Developing the EnMAP-Box under this license means that you can (if you want to) inspect and modify the source code and guarantees that you will always have access to an EnMAP-Box software that is free of cost and can be freely
modified.


## Support
You can get support in the following ways:

 -  Read the EnMAP-Box documentation [http://enmap-box.readthedocs.io](http://enmap-box.readthedocs.io)

 -  Open an issue with your question, bug report, feature request or other enhancement https://bitbucket.org/hu-geomatics/enmap-box/issues/new
 
 -  Write us an email: [andreas.rabe@geo.hu-berlin.de](mail://andreas.rabe@geo.hu-berlin.de) or [andreas.rabe@geo.hu-berlin.de](mail://benjamin.jakimow@geo.hu-berlin.de)


## Contribute own source code


If you like to contribute algorithms and applications to the EnMAP-Box,
please describe your ideas in an [enhancement issue](), or contact us via [mail:enmap-box@enmap.org](mail:enmap-box@enmap.org).

If you you wish to contribute source code directly, you preferably:

1. Create a fork of the EnMAP-Box development branch (
[Bitbucket](https://confluence.atlassian.com/bitbucket/forking-a-repository-221449527.html),
[GitHub](https://help.github.com/en/articles/fork-a-repo), 
[GitLab](https://docs.gitlab.com/ee/gitlab-basics/fork-project.html))
2. Make your changes
3. Commit your canges to the forked repository. Please
    - add ``[FEATURE]`` to your commit message AND give a clear description of the new feature.
    - sign your contribution (``git commit -s -S``)
4. Create a pull request to add your changes to the EnMAP-Box repository 
([Bitbucket](https://confluence.atlassian.com/bitbucket/work-with-pull-requests-223220593.html), 
[GitHub](https://help.github.com/articles/creating-a-pull-request-from-a-fork/), 
[GitLab](https://docs.gitlab.com/ee/gitlab-basics/add-merge-request.html))

The EnMAP-Box core developers will review your contribution and commit it upstream as appropriate.


