========
Examples
========

The foldlers here contain examples of how to run the
StackInAWSGI functionality in some common WSGI servers.

gunicorn
--------

Shows how to run StackInAWSGI using Gunicorn.

uwsgi
-----

Shows how to run StackInAWSGI using uWSGI.

python-wsgiref
--------------

Shows how to run StackInAWSGI using the built-in wsgiref.


Known Issues
============

- Only 1 worker can be used for any given WSGI server platform.
  This is due to the fact that the session information is not
  shared between workers. In theory all the workers should be able
  to see the data; however, they may be running as separate processes
  which would limit their value of what they can see. More research
  is needed to overcome this limitation.
