.. include:: external_links.rst

2. Graphical User Interfaces
############################

Overview
========

This tutorial gives an introduction on how to create graphical user interfaces with Qt, QGIS and the EnMAP-Box. It covers the
following aspects:

#. Basics of GUI programming.

   Here you learn the very fundamentals of how to create your own GUI applications with Qt and QGIS.
   It addresses users that never created a GUI programmatically before.


#. EnMAP-Box and EnMAP-Box Applications.
   Here you learn how to bring your widget application into the EnMAP-Box and to interact with an active EnMAP-Box GUI, e.g.
   to receive spectral profiles selected from a map.


#. Advanced GUI programming.

   Here you find more examples, templates and recommendation to solve specific GUI-related aspects.


Prerequisites
-------------

#. If not already done, clone the workshop repository and include it to your PyCharm project as described :ref:`here <setup_workshop_repository>`

#. The folder `programming_tutorial2/references` contains some scrips with reference code for the following exercises.
   To be able to start them from PyCharm, mark the folder as sources root ([Alt+1], *Mark Directory as > Sources Root*)

   .. image:: img/pycharm_setup_sourcesroots.png


.. include:: part1_basics.rst
.. include:: part2_enmapbox.rst
.. include:: part3_advanced.rst
