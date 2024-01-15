# -*- coding: utf-8 -*-

from odoo import models, fields, api


class lista_tareas(models.Model):
    _name = 'lista_tareas.lista_tareas'
    _description = 'lista_tareas.lista_tareas'

    tarea = fields.Char()
    prioridad = fields.Integer()
    urgente = fields.Boolean(compute="_value_urgente", store=True)
    realizada = fields.Boolean()
    descripcion = fields.Text()
    asignatura = fields.Char()
    tipo = fields.Selection(
        selection=[('1', 'Ejercicio'), ('2', 'Examen'), ('3', 'Trabajo')])

    @api.depends('prioridad')
    def _value_urgente(self):
        for record in self:
            if record.prioridad > 10:
                record.urgente = True
            else:
                record.urgente = False
