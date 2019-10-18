===========
Scrapy Docs
===========


.. image:: https://img.shields.io/pypi/v/scrapy_docs.svg
        :target: https://pypi.python.org/pypi/scrapy_docs

.. image:: https://img.shields.io/travis/b-rade/scrapy_docs.svg
        :target: https://travis-ci.org/b-rade/scrapy_docs

.. image:: https://readthedocs.org/projects/scrapy-docs/badge/?version=latest
        :target: https://scrapy-docs.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Scrapes documentation sites for images that contain code snippets.

Run by executing this code to generate all the urls for each docs page that will need scraping.
Make sure to delete the file this generates after scraping. As it gets appended to for every
crawl. // TODO make it overwrite.

.. code-block:: bash

    scrapy crawl docs-root

Then each page can be scraped with the following command.

.. code-block:: bash

    scrapy crawl whats-up-docs

This will give a file with the url of the docs page and the img source url 
(no reason to download the images if we don't need to).

The next stage of the problem to classify images as code snippets I'd probably resort to mechanical turk. It's
the type of activity that could be easily offloaded to hundreds of people instead of trying to build
an ML model. Could also try OCR and give an estimate of whether the text constitutes code.


* Free software: MIT license
* Documentation: https://scrapy-docs.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
