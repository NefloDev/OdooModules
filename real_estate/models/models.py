# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class real_estate(models.Model):
    _name = 'real_estate.real_estate'
    _description = 'Real Estate'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        "Available From", default=date.today()+relativedelta(months=3), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[('1', 'North'), ('2', 'South'), ('3', 'East'), ('4', 'West')], default='1')
    state = fields.Selection(
        selection=[('1', 'New'), ('2', 'Offer Received'), ('3', 'Offer Accepted'),
                   ('4', 'Sold'), ('5', 'Canceled')], default='1')
    active = fields.Boolean()
    salesman = fields.Char()
    buyer = fields.Char()
    total_area = fields.Float(compute='_compute_total_area')

    estate_type = fields.Many2one(
        'real_estate.real_estate_type', 'name')
    estate_tag = fields.Many2many(
        'real_estate.real_estate_tag', 'name')
    estate_offer_ids = fields.One2many(
        'real_estate.real_estate_offer', 'offer_id')
    prices = fields.Many2one(
        'real_estate.real_estate_offer', 'price')

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.onchange('garden')
    def _set_default_garden(self):
        if self.garden:
            self.garden_area = 10.0
            self.garden_orientation = '1'
        else:
            self.garden_area = 0.0
            self.garden_orientation = False


class real_estate_type(models.Model):
    _name = 'real_estate.real_estate_type'
    _description = "Real Estate Type"

    name = fields.Char(required=True)


class real_estate_tag(models.Model):
    _name = 'real_estate.real_estate_tag'
    _description = "Real Estate Tag"

    name = fields.Char(required=True)


class real_estate_offer(models.Model):
    _name = 'real_estate.real_estate_offer'
    _description = "Real Estate Offer"
    price = fields.Float()
    offer_id = fields.Many2one(
        'real_estate.real_estate', 'Offer Id', ondelete='cascade', required=True)
    partner = fields.Many2one(
        'real_estate.real_estate_partner', 'name')
    status = fields.Selection(selection=[('1', 'Accepted'), ('2', 'Refused')])
    validity_days = fields.Integer(
        default=0, compute='_compute_validity_days', inverse='_compute_deadline')
    deadline = fields.Date()

    @api.depends("deadline")
    def _compute_validity_days(self):
        for record in self:
            temp = record.deadline - date.today()
            record.validity_days = temp.days

    @api.depends("validity_days")
    def _compute_deadline(self):
        for record in self:
            temp = date.today() + relativedelta(days=record.validity_days)
            record.deadline = temp

    @api.constrains('deadline')
    def _deadline_constraint(self):
        for record in self:
            temp = record.deadline - date.today()
            if temp.days < 7:
                raise ValidationError(
                    "Deadline must be at least one week after the creation of the offer")


class real_estate_partner(models.Model):
    _name = 'real_estate.real_estate_partner'
    _description = "Real Estate Partner"

    name = fields.Char()
