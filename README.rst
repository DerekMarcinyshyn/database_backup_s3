Database Backup to AWS S3
=========================

Installed in Odoo server instance and sends backup data to S3.

Features:
---------

Uses Odoo built in db.dump_db command.

We recommend setting your AWS S3 Lifecycle to your preferred expiration policy.

Install:
--------

* Install boto (AWS Python Library) ``pip install boto``
* Create AWS id, key, and bucket in your AWS account
* Enter AWS id, key, and bucket in Settings -> Database Backup -> AWS Settings
