# -*- coding: utf-8 -*-
{
    'name': "duplicate_with_subtasks",

    'summary': """
        Duplicate tasks and subtasks.""",

    'description': """
        Duplicate tasks and subtasks.

        Adds two new options to Task view -> Actions
         - Duplicate with subtasks: Duplicate the task and all linked subtasks.
         - Rename subtasks: Update the names of subtasks to match the name of the parent task only works from parent task.
    """,

    'author': "tecnovert",
    'website': "https://github.com/tecnovert",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
