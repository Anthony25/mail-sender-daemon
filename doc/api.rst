.. _api:

===
API
===

A Swagger documentation is already available `here
<https://mail-sender.uber.aruhier.fr/>`_, so this part only contains quick
description of each method.

.. contents:: Table of Contents
   :depth: 3

.. _design_send:

Send: ``/send``
---------------

Allows to send an email. Depending on the provider, the destination address
has to be validated, or the email will be unauthorized.


.. _design_validation:

Validation: ``/validation``
---------------------------

Some providers does not allow email sending to addresses that have not been
validated before (AmazonSES for example). To check the validation status of an
address, use ``GET /validation/{address}``. To validate an address, use ``POST
/validation/{address}``. An email will be send to the specified address, asking
if wanted to be white-listed.
