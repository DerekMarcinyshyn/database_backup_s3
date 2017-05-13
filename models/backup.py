# -*- coding: utf-8 -*-

import tempfile
import base64
from datetime import datetime

from odoo import models, fields, api
from odoo.service import db

import logging
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.s3.key import Key
    from boto.s3.connection import S3Connection
except:
    _logger.debug('Database Backup S3 requires python library Boto to be installed.')

PARAMS = [
    ("database_backup_s3_id", "database_backup_s3.id"),
    ("database_backup_s3_key", "database_backup_s3.key"),
    ("database_backup_s3_bucket", "database_backup_s3.bucket"),
]


class DatabaseBackupS3Backup(models.TransientModel):

    _name = 'database_backup_s3.backup'
    _inherit = 'res.config.settings'

    database_backup_s3_id = fields.Char(string='AWS Access Id', required=True)
    database_backup_s3_key = fields.Char(string='AWS Secret Key', required=True)
    database_backup_s3_bucket = fields.Char(string='AWS Bucket', required=True)

    @api.one
    def set_params(self):
        self.ensure_one()

        for field_name, key_name in PARAMS:
            value = getattr(self, field_name, '').strip()
            self.env['ir.config_parameter'].set_param(key_name, value)

    @api.model
    def get_default_params(self, fields):
        res = {}
        for field_name, key_name in PARAMS:
            res[field_name] = self.env['ir.config_parameter'].get_param(key_name, '').strip()
        return res

    @api.one
    def action_database_backup_s3_test(self):
        self.create_backup()

    @api.model
    def create_backup(self):
        """Run backups"""
        filename = self.filename(datetime.now())
        try:
            _logger.info('Creating backup...')

            def dump_db(stream):
                return db.dump_db(self.env.cr.dbname, stream)

            with tempfile.TemporaryFile() as t:
                dump_db(t)
                t.seek(0)
                data = base64.b64decode(t.read().encode('base64'))

                _logger.info('Sending S3 simple agent')
                conn = boto.s3.connect_to_region('us-west-2', aws_access_key_id=self.database_backup_s3_id, aws_secret_access_key=self.database_backup_s3_key)
                bucket = conn.get_bucket(self.database_backup_s3_bucket)
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
