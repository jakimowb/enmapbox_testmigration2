.. _contribute:


How to contribute
#################

The EnMAP-Box is developed as part of the EnMAP Core Science Team activities, and everyone is welcome to
contribute.

The project is hosted on https://bitbucket.org/hu-geomatics/enmap-box

There are multiple ways how you can contribute to the EnMAP-Box.

Submitting a bug report or a feature request
============================================

We use the Bitbucket issue tracker to track bugs and feature requests. Feel free to open an new issue if you have found
a bug or wish to see a feature being implemented.

https://bitbucket.org/hu-geomatics/enmap-box/issues

Provide source code
===================

If your are not an  EnMAP-Box core developer, the preferred way to contribute code is to:

1. Create a fork on Bitbucket.
2. Clone the forked repository your local system.
3. Modify the local repository.
4. Commit your changes.
5. Push changes back to the remote fork on Bitbucket.
6. Create a pull request from the forked repository (source) back to the original (destination).



1. Create a fork on Bitbucket
.............................

Creating a fork means to clone the EnMAP-Box repository into your own user space. This allows you to create your own
feature branches, modify etc.

Fork the EnMAP-Box repository https://bitbucket.org/hu-geomatics/enmap-box , e.g. to
https://bitbucket.org/<my_account>/enmap-box_fork

See https://confluence.atlassian.com/bitbucket/forking-a-repository-221449527.html for details

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


3. Modify the local repository
..............................

Now you can start your own feature branch 'my_modifications'::

    $ git checkout -b my_modifications



4. Commit your changes
......................

Save your changes by commiting them to your local repository::

    $ git add modified_files
    $ git commit -a -m 'added x, modified y and fixed z' -s

Please use signed commits to make your individual contribution visible.
Even better, use GnuPG-signed commits (-S)

5. Push changes back to your fork
.................................

The pull request informs us on the changes you like to bring into the EnMAP-Box.


    $ git push



6. Creat a pull request
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
-------------------------

To build and text the documentation on your local system, navigate into the `doc` folder and run the make file::

    $ cd doc
    $ make html

This will start Sphinx and create the HTML documentation into the `doc\build`.
Open `doc/build/html/index.html` to visualize it in your web browser.

