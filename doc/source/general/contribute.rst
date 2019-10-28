.. _contribute:

How to contribute
#################

The EnMAP-Box is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
and particularly developed to handle data from the EnMAP sensor.

It is provided as a plug-in for QGIS (https://www.qgis.org/en/site/).

The development of the EnMAP-Box is funded within the EnMAP scientific preparation program under the
DLR Space Administration (mission lead) and GFZ Potsdam (scientific lead) with resources from the
German Federal Ministry for Economic Affairs and Energy.

The EnMAP-Box source code is hosted in a public git repository at https://bitbucket.org/hu-geomatics/enmap-box.
Approved QGIS plugin versions (“production releases”) are available at https://plugins.qgis.org/plugins/enmap-box

Everyone is welcome to contribute to the EnMAP-Box. In follow we describe how you can do so.

Submit a bug report or feature request
======================================

In case you experience issues with the EnMAP-Box, do not hesitate to submit a
ticket to our `Issue Tracker <https://bitbucket.org/hu-geomatics/enmap-box/issues>`_.

You are also welcome to post feature requests or pull requests.

It is recommended to check that your issue complies with the
following rules before submitting:

*  Verify that your issue is not being currently addressed by other
   `issues <https://bitbucket.org/hu-geomatics/enmap-box/issues?q=>`_
   or `pull requests <https://bitbucket.org/hu-geomatics/enmap-box/pull-requests?>`_.

*  If you are submitting a bug report, please:

    * Report a short description how to reproduce it

    * If an exception is raised, please **provide the full traceback**.

    * If necessary, provide a link to the data that causes the bug

    * If not feasible to include a reproducible snippet, please be specific about
      what part of the EnMAP-Box (functions, widget) are involved and the shape of the data

    * Include your operating system type and version number of QGIS, Qt and the EnMAP-Box

    *  Please ensure that **code snippets and error messages are formatted in
        appropriate code blocks**.

    .. note::
        You can use this `Markdown syntax <https://confluence.atlassian.com/bitbucketserver/markdown-syntax-guide-776639995.html>`_
        to style your issues.





Provide source code
===================

If your are not an EnMAP-Box core developer, the preferred way to contribute code is to use pull requests:

1. Create a fork on Bitbucket.
2. Clone the forked repository your local system.
3. Modify the local repository.
4. Commit your changes.
5. Push changes back to the remote fork on Bitbucket.
6. Create a pull request from the forked repository (source) back to the original (destination).

.. _contribute_fork

1. Create a fork on Bitbucket
.............................

Creating a fork means to clone the EnMAP-Box repository into your own user space. This allows you to create your own
feature branches, modify etc.

Fork the EnMAP-Box repository https://bitbucket.org/hu-geomatics/enmap-box , e.g. to
https://bitbucket.org/<my_account>/enmap-box_fork

See https://confluence.atlassian.com/bitbucket/forking-a-repository-221449527.html for details

.. _contribute_clone

2. Clone the forked EnMAP-Box repository
........................................

Now clone your fork to the your local disk, install the python requirements requirement and run the initial setup::

    $ git clone git@bitbucket.com/enmapbox.git
    $ cd enmapbox
    $ python3 -m pip install -r requirements_develop.txt

For details on the EnMAP-Box repository setup please read [tbd]

Add the ``upstream`` remote repository

    $ git remote add upstream https://bitbucket.org/hu-geomatics/enmap-box

.. note::
    From now on, you can synchronize the master branch of your forked repository with the EnMAP-Box repository by::

    $ git checkout master
    $ git pull upstream master


.. _contribute_modify

3. Modify the local repository
..............................

Now you can start your own feature branch 'my_modifications'::

    $ git checkout -b my_modifications


.. _contribute_commit

4. Commit your changes
......................

Save your changes by commiting them to your local repository::

    $ git add modified_files
    $ git commit -a -m 'added x, modified y and fixed z' -s

Please use signed commits to make your individual contribution visible.
Even better, use GnuPG-signed commits (-S)

.. _contribute_push

5. Push changes back to your fork
.................................

The pull request informs us on the changes you like to bring into the EnMAP-Box.


    $ git push



.. _contribute_pull_request

6. Create a pull request
.......................

Open the Bitbucket webpage of your fork and create a pull request.
The pull request will inform us on the changed you made.



Tests and Continuous Integration
================================

Please support unit tests that test if your source code contribution works right.


Documentation
=============

The EnMAP-Box documentation is based on Sphinx and and hosted at https://enmap-box.readthedocs.io
The reStructured text source files of the documentation are located in `doc\source` folder.

Building the documentation
--------------------------

To build and text the documentation on your local system, navigate into the `doc` folder and run the make file::

    $ cd doc
    $ make html

This will start Sphinx and create the HTML documentation into the `doc\build`.
Open `doc/build/html/index.html` to visualize it in your web browser.

Licensing
=========

The software produced for the EnMAP-Box is licensed according to the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License (SPDX short identifier: GPL-3.0), or (if desired) any later version.
See either https://www.gnu.org/licenses/gpl-3.0.en.html or https://opensource.org/licenses/GPL-3.0 for further details of the license.

A copy of this license is part of the EnMAP-Box repository https://bitbucket.org/hu-geomatics/enmap-box/src/master/LICENSE.md?fileviewer=file-view-default and delivered with each release of an EnMAP-Box plugin.

Applying License Terms
----------------------
Each source code file of a contribution to the central repository should include the following notice to the license terms::

    """
    ***************************************************************************
        <file name> - <short description>
        -----------------------------------------------------------------------
        begin                : <month and year of creation>
        copyright            : (C) <year> <creator>
        email                : <main address>

    ***************************************************************************
        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 3 of the License, or
        (at your option) any later version.
                                                                                                                                                     *
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this software. If not, see <http://www.gnu.org/licenses/>.
    ***************************************************************************
    """



