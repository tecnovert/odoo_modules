# -*- coding: utf-8 -*-
# from odoo import http


# class DuplicateWithSubtasks(http.Controller):
#     @http.route('/duplicate_with_subtasks/duplicate_with_subtasks/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/duplicate_with_subtasks/duplicate_with_subtasks/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('duplicate_with_subtasks.listing', {
#             'root': '/duplicate_with_subtasks/duplicate_with_subtasks',
#             'objects': http.request.env['duplicate_with_subtasks.duplicate_with_subtasks'].search([]),
#         })

#     @http.route('/duplicate_with_subtasks/duplicate_with_subtasks/objects/<model("duplicate_with_subtasks.duplicate_with_subtasks"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('duplicate_with_subtasks.object', {
#             'object': obj
#         })
