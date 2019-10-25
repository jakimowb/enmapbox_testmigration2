.. _contribute:

=====================
How to contribute
=====================

The EnMAP-Box is developed as part of the EnMAP Core Science Team activities, and everyone is welcome to
contribute.

The project is hosted on https://bitbucket.org/hu-geomatics/enmap-box

There are multiple ways how you can contribute to the EnMAP-Box.

Submitting a bug report or a feature request
--------------------------------------------

We use the Bitbucket issue tracker to track bugs and feature requests. Feel free to open an new issue if you have found
a bug or wish to see a feature being implemented.

https://bitbucket.org/hu-geomatics/enmap-box/issues

Provide source code
-------------------

The preferred way to contribute code is to fork the main EnMAP-Box repository, add your changes and submit a "pull request" (PR).

1. Create an account on bitbucket.com
2. Fork the EnMAP-Box repository https://bitbucket.org/hu-geomatics/enmap-box , e.g. to
   https://bitbucket.org/<my_account>/enmap-box_fork

3. Clone your EnMAP-Box to your local disk, install the python requirements requirement and run the initial setup rountine::

    $ git clone git@bitbucket.com/enmap-box_fork.git
    $ cd my_enmapbix_fork.git
    $ python3 -m pip install -r requirements_develop.txt

   https://bitbucket.org/hu-geomatics/enmap-box
   For more details about the installation of the EnMAP-Box from a repository, please read [tbd]

4. Add the ``upstream`` remote repository::

    $ git remote add upstream https://bitbucket.org/hu-geomatics/enmap-box

  From now on, you can synchronize the master branch of your forked repository with the EnMAP-Box repository by::

    $ git checkout master
    $ git pull upstream master


5. Now you can start your own feature branch 'my_modifications':

    $ git checkout -b my_modifications

6. Commit your changes::

    $ git add modified_files
    $ git commit -a -m 'added x, modified y and fixed z' -s

   .. note::
        Please use signed commits only. Even better, use GnuPG-signed commits (-S)

7. Push your changes to your forked repository

    $ git push
