# -*- coding: utf-8 -*-

import os
import json
import tempfile
import base64
from datetime import datetime

from odoo import models, api
from odoo.service import db

import logging
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.s3.key import Key
    from boto.s3.connection import S3Connection
except:
    _logger.debug('Database Backup S3 requires python library Boto to be installed.')


class DatabaseBackupS3Backup(models.Model):
    _name = 'database_backup_s3.backup'

    @api.one
    def action_database_backup_s3_test(self):
        self.create_backup()

    @api.model
    def create_backup(self):
        """Run backups"""
        filename = self.filename(datetime.now())
        with open(os.path.dirname(os.path.abspath(__file__)) + '/aws.json', 'r') as aws_file:
            aws = json.load(aws_file)
            key = aws["key"]
            secret = aws["secret"]
            bucket = aws["bucket"]

        try:
            _logger.info('Creating backup...')

            def dump_db(stream):
                return db.dump_db(self.env.cr.dbname, stream)

            with tempfile.TemporaryFile() as t:
                dump_db(t)
                t.seek(0)
                data = base64.b64decode(t.read().encode('base64'))

                _logger.info('Sending S3 simple agent')
                conn = boto.s3.connect_to_region('us-west-2', aws_access_key_id=key, aws_secret_access_key=secret)
                bucket = conn.get_bucket(bucket)
                k = Key(bucket)
                k.key = filename
                k.set_contents_from_string(data)
                _logger.info('Backup success')

        except Exception as e:
            _logger.exception('An error occurred uploading to AWS S3. %s' % str(e))

    @api.model
    def filename(self, when):
        """Generate a filename for backup"""
        return "{:%Y_%m_%d_%H_%M_%S}.dump.zip".format(when)
