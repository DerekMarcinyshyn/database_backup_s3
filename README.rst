Database Backup to AWS S3
=========================

Installed in Odoo server instance and sends backup data to S3.

Uses Odoo built in db.dump_db command.

Install:
--------

* Install boto (AWS Python Library) ``pip install boto``
* Create aws.json file from aws.json.example from models folder
* Test in Settings -> Database Backup -> AWS
