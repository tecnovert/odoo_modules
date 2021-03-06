# -*- coding: utf-8 -*-
{
    'name': "activity_history",

    'summary': """
        Activity history.""",

    'description': """
        Activity history.
        Adds a new option to Projects -> Activity History page.
        Prevents tasks from being deleted.
    """,

    'author': "tecnovert",
    'website': "https://github.com/tecnovert",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
