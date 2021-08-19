# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Task(models.Model):
    _inherit = 'project.task'

    @api.model
    def _get_duplicate_fields(self):
        return ['allowed_user_ids', 'company_id', 'description', 'displayed_image_id', 'email_cc',
                'parent_id', 'partner_email', 'partner_id', 'partner_phone', 'planned_hours',
                'project_id', 'project_privacy_visibility', 'sequence', 'tag_ids', 'recurrence_id',
                'name', 'recurring_task']

    def get_new_task_values(self, task):
        self.ensure_one()
        fields_to_copy = self._get_duplicate_fields()
        task_values = task.read(fields_to_copy).pop()
        create_values = {
            field: value[0] if isinstance(value, tuple) else value for field, value in task_values.items()
        }
        create_values['stage_id'] = task.project_id.type_ids[0].id if task.project_id.type_ids else task.stage_id.id
        create_values['user_id'] = False
        return create_values

    def duplicate_subtasks(self, new_task):
        if not self.child_ids:
            return
        for child in self.child_ids:
            child_values = self.get_new_task_values(child)
            child_values['parent_id'] = new_task.id
            new_task.env['project.task'].create([child_values,])
            child.duplicate_subtasks(new_task.child_ids[-1])
        return

    def copy_all(self, default=None):
        logger.info("copy_all task %d", self.id)
        new_task = super(Task, self).copy(default)
        self.duplicate_subtasks(new_task)

        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": new_task._name,
            "res_id": new_task.id,
        }

    def rename_subtasks(self, new_name=None):
        logger.info("rename_subtasks %d", self.id)

        if new_name is None:
            if self.parent_id:
                logger.warning("Only works from the root task.")
                raise UserError(_('Can only rename from root tasks.'))
            new_name = self.name

        if not self.child_ids:
            logger.warning("No subtasks to rename.")
            return
        renamed = 0
        for child in self.child_ids:
            try:
                new_child_name = new_name + ':' + child.name.split(':', 1)[1]
            except Exception as e:
                 logger.warning("Not updating child %d name: %s.", child.id, str(e))
                 continue
            child.update({
                    'name': new_child_name,
                })
            child.rename_subtasks(new_name)
            renamed += 1

        return
