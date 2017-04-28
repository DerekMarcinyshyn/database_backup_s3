# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime

from odoo import models, fields, api, tools
from odoo.service import db

import logging
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.s3.key import Key
    from boto.s3.connection import S3Connection
except:
    _logger.debug('Database Backup S3 requires python library Boto to be installed.')

try:
    parallel_upload = False
    from filechunkio import FileChunkIO
    parallel_upload = True
except:
    _logger.debug('Database Backup S3 performs better with FileChunkIO installed.')


PARAMS = [
    ("database_backup_s3_id", "database_backup_s3.id"),
    ("database_backup_s3_key", "database_backup_s3.key"),
    ("database_backup_s3_bucket", "database_backup_s3.bucket"),
]


class DatabaseBackupS3Settings(models.TransientModel):

    _name = 'database_backup_s3.settings'
    _inherit = 'res.config.settings'

    database_backup_s3_id = fields.Char('AWS Access Id')
    database_backup_s3_key = fields.Char('AWS Secret Key')
    database_backup_s3_bucket = fields.Char('AWS Bucket')

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
        _logger.critical('*** Clicked ***')
        # _logger.critical('id,key: ' + self.database_backup_s3_id + ',' + self.database_backup_s3_key)
        # conn = S3Connection(self.database_backup_s3_id, self.database_backup_s3_key)
        # bucket = conn.get_bucket(self.database_backup_s3_bucket)
        self.create_backup()

    @api.model
    def create_backup(self):
            """Run backups"""
            backup = None
            filename = self.filename(datetime.now())
            successful = self.browse()

            for rec in self:
                with rec.backup_log():
                    # Directory must exist
                    try:
                        os.makedirs(self.folder())
                    except OSError:
                        pass

                    with open(os.path.join(self.folder(), filename), 'wb') as destiny:
                        # Copy the cached backup
                        if backup:
                            with open(backup) as cached:
                                shutil.copyfileobj(cached, destiny)
                        # Generate new backup
                        else:
                            db.dump_db(self.env.cr.dbname, destiny)
                            backup = backup or destiny.name
                    successful |= rec
            _logger.info('Done database backup')

    @api.model
    def backup_log(self):
        """Log a backup result."""
        try:
            _logger.info("Starting database backup: %s", self.env.cr.dbname)
            yield
        except:
            _logger.exception("Database backup failed: %s", self.env.cr.dbname)
        else:
            _logger.info("Database backup succeeded: %s", self.env.cr.dbname)

    @api.model
    def folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(tools.config["data_dir"], "backups", self.env.cr.dbname)

    @api.model
    def filename(self, when):
        """Generate a filename for backup"""
        return "{:%Y_%m_%d_%H_%M_%S}.dump.zip".format(when)
