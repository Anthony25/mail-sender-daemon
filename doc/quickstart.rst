.. _quickstart:

==========
Quickstart
==========

Mail Sender is a Python application allowing to send emails through 2
providers, AmazonSES and Mailgun, with an automatic failover. It provides a
REST API, documented with Swagger, and a python client to use it.

An demo is hosted on https://mail-sender.uber.aruhier.fr.

A client can be found
`here <https://github.com/Anthony25/mail-sender-client>`_.

.. contents:: Table of Contents
   :depth: 3

.. _quickstart_installation:

Installation
------------

First clone the project::

    $ git clone https://github.com/Anthony25/mail-sender-daemon.git
    $ cd mail-sender-daemon

Install it via pip3 (requires ``python3-pip`` or ``python-pip``, depending
whether python 2 or 3 is the default)::

    $ pip3 install -e

Then use a WSGI container, like Gunicorn, `by refering to the Flask
documentation <http://flask.pocoo.org/docs/0.12/deploying/wsgi-standalone/>`_.
The application can be imported with ``mail_sender_daemon:app``.


Configuration
-------------

A configuration file is needed for the daemon to run. Copy and tweak the self
documented ``config.yml.default`` file (available at the repository root) in
one of the following paths:

  * ``~/.config/mail-sender-daemon/config.yml``: user separated configuration
  * ``/etc/mail-sender-daemon/config.yml``: systemd-wide configuration
