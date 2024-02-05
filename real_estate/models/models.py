# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class real_estate(models.Model):
    _name = 'real_estate.real_estate'
    _description = 'Real Estate'
    _order = 'id desc'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        "Available From", default=date.today()+relativedelta(months=3), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(
        compute='_compute_selling_price', copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean(default=False)
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[('1', 'North'), ('2', 'South'), ('3', 'East'), ('4', 'West')], default='1')
    state = fields.Selection(
        selection=[('1', 'New'), ('2', 'Offer Received'), ('3', 'Offer Accepted'),
                   ('4', 'Sold'), ('5', 'Canceled')], default='1', compute='_compute_state', store=True)
    active = fields.Boolean()
    salesman = fields.Char(
        default=lambda self: self.env.user.name, readonly=True)
    buyer = fields.Char(compute='_compute_buyer')
    total_area = fields.Float(compute='_compute_total_area')
    estate_type = fields.Many2one(
        'real_estate.real_estate_type', 'name')
    estate_tag = fields.Many2many(
        'real_estate.real_estate_tag', 'name')
    estate_offer_ids = fields.One2many(
        'real_estate.real_estate_offer', 'offer_id')
    best_price = fields.Float(default=0.0, compute='_compute_best_price')
    property_id = fields.Many2one('real_estate.real_estate_type')

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends('estate_offer_ids')
    def _compute_best_price(self):
        for record in self:
            if record.estate_offer_ids != False:
                max_val = 0.0
                for offer in record.estate_offer_ids:
                    if offer.price > max_val:
                        max_val = offer.price
                record.best_price = max_val
            else:
                record.best_price = False

    @api.depends('estate_offer_ids')
    def _compute_selling_price(self):
        for record in self:
            if record.estate_offer_ids != False:
                max_val = 0.0
                for offer in record.estate_offer_ids:
                    if offer.status == '1' and offer.price > max_val:
                        max_val = offer.price
                record.selling_price = max_val
            else:
                record.selling_price = False

    @api.depends('estate_offer_ids')
    def _compute_buyer(self):
        for record in self:
            if record.estate_offer_ids != False:
                max_val = 0.0
                buyer = ""
                for offer in record.estate_offer_ids:
                    if offer.status == '1' and offer.price > max_val:
                        max_val = offer.price
                        buyer = offer.partner[0].name
                record.buyer = buyer
            else:
                record.selling_price = False

    @api.depends('estate_offer_ids')
    def _compute_state(self):
        for record in self:
            if not (record.state == '4' and '5') and record.estate_offer_ids != False and len(record.estate_offer_ids) > 0:
                finish = False
                i = 0
                while i < len(record.estate_offer_ids) and not finish:
                    temp = record.estate_offer_ids[i]
                    if temp.status == '1':
                        record.state = '3'
                        finish = True
                    i += 1
                if not finish:
                    record.state = '2'
            else:
                record.state = '1'

    @api.onchange('garden')
    def _set_default_garden(self):
        if self.garden:
            self.garden_area = 10.0
            self.garden_orientation = '1'
        else:
            self.garden_area = 0.0
            self.garden_orientation = False

    def sell_property(self):
        for record in self:
            if record.state != '5':
                record.state = '4'
            else:
                raise ValidationError("Canceled properties cannot be sold.")
        return True

    def cancel_property(self):
        for record in self:
            record.state = '5'
        return True


class real_estate_type(models.Model):
    _name = 'real_estate.real_estate_type'
    _description = "Real Estate Type"
    _order = 'sequence, name'

    name = fields.Char(required=True)

    properties = fields.One2many('real_estate.real_estate', 'property_id')
    sequence = fields.Integer()


class real_estate_tag(models.Model):
    _name = 'real_estate.real_estate_tag'
    _description = "Real Estate Tag"
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer()


class real_estate_offer(models.Model):
    _name = 'real_estate.real_estate_offer'
    _description = "Real Estate Offer"
    _order = 'price desc'
    price = fields.Float()
    best_price = fields.Float(default=0.0, compute='_compute_best_price')
    offer_id = fields.Many2one(
        'real_estate.real_estate', 'Offer Id', ondelete='cascade', required=True)
    partner = fields.Many2one(
        'real_estate.real_estate_partner', 'name')
    properties = fields.One2many(
        'real_estate.real_estate', "property_id")
    status = fields.Selection(
        selection=[('1', 'Accepted'), ('2', 'Refused')], default=False)
    validity_days = fields.Integer(
        default=0, compute='_compute_validity_days', inverse='_compute_deadline')
    deadline = fields.Date()

    @api.depends("deadline")
    def _compute_validity_days(self):
        for record in self:
            if record.deadline != False:
                temp = record.deadline - date.today()
                record.validity_days = temp.days

    @api.depends("validity_days")
    def _compute_deadline(self):
        for record in self:
            if record.validity_days != False:
                record.deadline = date.today() + relativedelta(days=record.validity_days)

    @api.constrains('deadline')
    def _deadline_constraint(self):
        for record in self:
            if record.deadline != False:
                temp = record.deadline - date.today()
                if temp.days < 7:
                    raise ValidationError(
                        "Deadline must be at least one week after the creation of the offer")

    @api.depends('price')
    def _compute_best_price(self):
        max_val = 0.0
        for record in self:
            if max_val < record.price:
                max_val = record.price
        self.best_price = max_val

    def accept_offer(self):
        for record in self:
            record.status = '1'
        return True

    def refuse_offer(self):
        for record in self:
            record.status = '2'
        return True


class real_estate_partner(models.Model):
    _name = 'real_estate.real_estate_partner'
    _description = "Real Estate Partner"

    name = fields.Char()
