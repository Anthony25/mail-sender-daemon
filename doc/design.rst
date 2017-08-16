.. _design:

======
Design
======

This part will present the different design choices made for this project.

.. contents:: Table of Contents
   :depth: 3

.. _design_application:

Application
-----------

A separation between a frontend and a backend application has been adopted:
the last one provide a REST API, used by the first one to interact with it.

Python has been chosen for its simplicity. Compute time is not important here,
as the application relies mainly on its providers. The REST API is done by
`flask-restplus <https://github.com/noirbizarre/flask-restplus>`_, using
Swagger to provide data verification and documentation. ``requests`` is
used to implement a client for the 2 providers' web API.


.. _design_infrastructure:

Infrastructure
--------------

Different redundancy techniques have been used to host the daemon:

.. _infrastructure_img:
.. figure:: img/infrastructure.svg
    :alt: Infrastructure
    :align: center
    :scale: 90%

    Mail Sender infrastructure

The infrastructure is split as 2 main parts: my home infrastructure, and 2 vm
hosted on Digital Ocean. Round Robin DNS is used between each entry point.

On Digital Ocean, each host runs a HAProxy and Mail Sender Daemon (in a
docker). ``keepalived`` is used to setup VRRP, detecting if HAProxy is still
up, otherwise the other host will take up the relay. Digital Ocean only
provides IPv4 floating addresses, that is why the IPv6 is not included into
VRRP.

On my home infrastructure, a public IP is dynamically routed through OSPF
from a Online server. HAProxy is used, and load balances to 3 nodes, running
on LXC. VRRP cannot be used here, as Online does not provide a floating API,
and I do not have the control on the IP external announcement.


.. _design_tradeoffs:

Tradeoffs
---------

Synchronous vs asynchronous
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When sending an email, a synchronous design has been chosen: the web API will
try to send the email when requested, and the client will wait for an answer
indicating if it failed or not.

However, an asynchronous design has been thought: a client could send a request
to the API, which then transmits it to a message broker, and returns a token to
the client as a response. The message broker then load balances the mail
sending to different nodes, which store the sending status in a database.  The
client could check the sending status by calling a method in the API with the
same token they previously received.

This design has the advantage to handle much more capacity, as all messages
could be stacked into the message broker queue, and be sent when a node is
free. Clients will not timeout if their mail take longer than usual to be sent,
and a retry could be implemented if no provider is available.

However, it is way more complex: users should be able to request the sending
status, a database and a message broker have to be added. On the infrastructure
side, it also means that, in order to avoid any SPOF, the database and the
message broker should both be in a cluster. Also, as the current infrastructure
is divided into 2 sites (home infrastructure and Digital Ocean), a split brain
could occur.

Regarding the delay of this project, an asynchronous design would have brought
too much complexity to be implemented. For this reason, the synchronous design
has followed.
