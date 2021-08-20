# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ActivityHistory(models.Model):
    _name = "project.activity_history"
    _description = "Activity History"

    changed_by = fields.Many2one(
        'res.users', 'Changed by',
        default=lambda self: self.env.user,
        index=True, required=True)
    changed_at = fields.Datetime(string="Changed At", help='Instance record state changed', readonly=True, required=True)
    changed_data = fields.Char('Changed')  # for future use

    entry_type = fields.Selection([
        ('create', 'Created'),
        ('edit', 'Edited'),
        ('view', 'Viewed'),
        ('note', 'Added Note'),
        ('assign', 'Assigned'),
        ('unlink', 'Deleted'),
        ('done', 'Done')], 'Type')

    activity_id = fields.Integer(string="Activity ID")

    # owner
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model',
        index=True, ondelete='cascade', required=True)
    res_model = fields.Char(
        'Related Document Model',
        index=True, related='res_model_id.model', compute_sudo=True, store=True, readonly=True)
    res_id = fields.Many2oneReference(string='Related Document ID', index=True, required=True, model_field='res_model')
    res_name = fields.Char(
        'Document Name', compute='_compute_res_name', compute_sudo=True, store=True,
        help="Display name of the related document.", readonly=True)
    # activity
    activity_type_id = fields.Many2one(
        'mail.activity.type', string='Activity Type',
        domain="['|', ('res_model_id', '=', False), ('res_model_id', '=', res_model_id)]", ondelete='restrict')
    activity_category = fields.Selection(related='activity_type_id.category', readonly=True)
    activity_decoration = fields.Selection(related='activity_type_id.decoration_type', readonly=True)
    icon = fields.Char('Icon', related='activity_type_id.icon', readonly=True)
    summary = fields.Char('Summary')
    note = fields.Html('Note', sanitize_style=True)
    date_deadline = fields.Date('Due Date', index=True, required=True, default=fields.Date.context_today)
    automated = fields.Boolean(
        'Automated activity', readonly=True,
        help='Indicates this activity has been created automatically and not by any user.')
    # description
    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        index=True, required=True)
    request_partner_id = fields.Many2one('res.partner', string='Requesting Partner')
    state = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned')], 'State')

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for activity in self:
            activity.name_rel = activity.res_model and \
                self.env[activity.res_model].browse(activity.res_id).display_name

    name_rel = fields.Char('Name', compute='_compute_res_name', store=False)

    def link_to_task(self):
        return {
            'view_mode': 'form',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def unlink(self):
        self.ensure_one()
        fields_to_copy = [
            'res_model_id',
            'res_model',
            'res_id',
            'res_name',
            'note',
            'summary',
            'activity_type_id',
            'date_deadline',
        ]
        activity_values = self.read(fields_to_copy).pop()
        create_values = {
            field: value[0] if isinstance(value, tuple) else value for field, value in activity_values.items()
        }
        create_values['changed_at'] = fields.Datetime.now()
        create_values['changed_by'] = self.env.user.id
        create_values['activity_id'] = self.id
        create_values['entry_type'] = 'done'

        id_created = self.env['project.activity_history'].create([create_values])

        return super().unlink()


class Task(models.Model):
    _inherit = 'project.task'

    def have_near_record(self, res_model_id, self_id):
        seconds_ago = fields.Datetime.now() - timedelta(seconds=5)
        num_records = self.env['project.activity_history'].search_count([
            ('res_model_id', '=', res_model_id),
            ('res_id', '=', self_id),
            ('changed_by', '=', self.env.user.id),
            ('changed_at', '>', seconds_ago)])

        return True if num_records > 0 else False

    @api.model_create_multi
    def create(self, vals):
        rv = super().create(vals)
        res_model_id = self.env.ref('project.model_project_task').id

        for task in rv:
            if self.have_near_record(res_model_id, task.id):
                continue
            create_values = {
                'changed_at': fields.Datetime.now(),
                'changed_by': self.env.user.id,
                'entry_type': 'create',
                'res_model_id': res_model_id,
                'res_id': task.id,
            }
            id_created = self.env['project.activity_history'].create([create_values])

        return rv

    def write(self, vals):
        res_model_id = self.env.ref('project.model_project_task').id
        if not self.have_near_record(res_model_id, self.id):
            create_values = {
                'changed_at': fields.Datetime.now(),
                'changed_by': self.env.user.id,
                'entry_type': 'edit',
                'res_model_id': res_model_id,
                'res_id': self.id,
            }
            id_created = self.env['project.activity_history'].create([create_values])

        return super().write(vals)

    def unlink(self):
        logger.warning("unlink task %d", self.id)
        raise UserError(_('Delete disabled, archive instead.'))
        '''
        create_values = {
            'changed_at': fields.Datetime.now(),
            'changed_by': self.env.user.id,
            'entry_type': 'unlink',
            'res_model_id': self.env.ref('project.model_project_task').id,
            'res_id': self.id,
        }
        id_created = self.env['project.activity_history'].create([create_values])

        logger.info("[rm]unlink task 2 %d", self.id)
        '''
        return super().unlink()

    def _message_create(self, values_list):
        res_model_id = self.env.ref('project.model_project_task').id
        if not self.have_near_record(res_model_id, self.id):
            create_values = {
                'changed_at': fields.Datetime.now(),
                'changed_by': self.env.user.id,
                'entry_type': 'note',
                'res_model_id': res_model_id,
                'res_id': self.id,
            }
            id_created = self.env['project.activity_history'].create([create_values])

        return super()._message_create(values_list)
