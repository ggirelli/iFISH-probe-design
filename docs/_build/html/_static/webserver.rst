Web Server
==========

BiCro Commons is a web space hosted on a Python-based basic server powered by the ``bottle`` library. It can easily run locally, though some of its hosted tools might require further setup.

Requirements
------------

To run, BiCro Commons requires the following Python3 libraries: ``bottle``, ``paste``.

How to run
----------

To run the web server just use the ``./web.py`` script. By default, the web space will be hosted at ``0.0.0.0:8080``, but you can easily specify both url and port with the ``--url`` and ``--port`` optional parameters.

usage: ``web.py [-h] [--url url] [--port port]``

+-------------+------------------+
|optional arguments:             |
+=============+==================+
| --url url   | Web Server URL.  |
+-------------+------------------+
| --port port | Web Server port. |
+-------------+------------------+
