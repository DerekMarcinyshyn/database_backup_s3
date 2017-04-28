# -*- coding: utf-8 -*-
{
    'name': 'Database Backup S3',
    'summary': 'Backup up database to AWS S3.',
    'version': '10.0.1.0.0',
    'author': 'Derek Marcinyshyn',
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
        'views/backup.xml',
    ],
    'installable': True,
}
