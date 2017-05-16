# -*- coding: utf-8 -*-
{
    'name': 'Database Backup S3',
    'summary': 'Backup up database to AWS S3.',
    'version': '10.0.1.0.0',
    'author': 'Derek Marcinyshyn',
    'license': 'AGPL-3',
    'category': 'Extra Tools',
    'website': 'https://www.monasheemountainmultimedia.com',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': [
        'website'
    ],
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/backup.xml',
    ],
    'installable': True,
    'auto_install': False
}
