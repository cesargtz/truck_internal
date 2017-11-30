# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json

class truck_internal(models.Model):
    _inherit = ['truck','truck.transfer','mail.thread']
    _name = 'truck.internal'

  #  _defaults = {'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'reg_code_ti'), }
    name = fields.Char('Truck Internal reference', required=True, select=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('reg_code_ti'), help="Unique number of the Truck Internal")
    humidity_rate_dest = fields.Float('Humedad destino')
    damage_rate_dest = fields.Float('Daño destino')
    break_rate_dest = fields.Float('Quebrado destino')
    impurity_rate_dest = fields.Float('Impureza destino')
    
    input_kilos_dest = fields.Float('Kilos de Entrada Destino')
    output_kilos_dest = fields.Float('Kilos de Salida Destino')

    density_dest = fields.Float('Densidad Destino')
    temperature_dest = fields.Float('Temperatura Destino')
    transgenic_dest = fields.Float('Transgénico Destino')

    raw_kilos_dest = fields.Float('Kilos neto Destino',compute="_compute_raw_kilos_dest", store=False)

    humid_kilos_dest = fields.Float('Kilos Humedos destino', compute="_compute_humid_kilos_dest", store=False)
    damaged_kilos_dest = fields.Float('Kilos dañados destino ', compute="_compute_damaged_kilos_dest", store=False)
    broken_kilos_dest = fields.Float('Kilos quebrados destino', compute="_compute_broken_kilos_dest", store=False)
    impure_kilos_dest = fields.Float('Kilos impuros destino', compute="_compute_impure_kilos_dest", store=False)

    deducted_kilos_dest = fields.Float('Deducido', compute="_compute_deducted_kilos_dest", store=False)

    clean_kilos_dest = fields.Float('Kilos limpios destino', compute="_compute_clean_kilos_dest", store=False)

    ticket_dest = fields.Integer('Ticket')
    difference = fields.Float('Diferencia', compute="_compute_difference_kilos", store=False)
    stock_origin = fields.Boolean('Movimiento por origen')
    stock_destination = fields.Boolean('Movimiento por Destino',default=True)
    active = fields.Boolean('Activo', default=True)

    state = fields.Selection([
        ('load','Load'),
        ('unload','Unload'),
    	('done','Done')
    ], default='load')

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'load':
                self.write({'state': 'unload'}, 'r')
            elif self.state == 'unload':
                self.write({'state': 'done'}, 'r')

        res = super(truck_internal, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals['state'] = 'unload'
        res = super(truck_internal, self).create(vals)
        return res

    @api.multi
    def truck_reception_stats_sensor_update(self):
        url = 'http://nvryecora.ddns.net:8080'
        response = requests.get(url)
        json_data = json.loads(response.text)
        self.humidity_rate = float(json_data['humedad'].strip())
        self.density = float(json_data['densidad'].strip())
        self.temperature = float(json_data['temperatura'].strip())

    @api.multi
    def weight_update(self):
        url = 'http://nvryecora.ddns.net:8081'
        response = requests.get(url)
        json_data = json.loads(response.text)
        self.input_kilos = float(json_data['peso_entrada'])
        self.output_kilos = float(json_data['peso_salida'])
        self.raw_kilos = float(json_data['peso_neto']) 

    @api.one
    @api.depends('input_kilos', 'output_kilos')
    def _compute_raw_kilos(self):
        #self.ensure_one()
        self.raw_kilos = self.output_kilos -self.input_kilos

    @api.one
    @api.depends('input_kilos_dest', 'output_kilos_dest')
    def _compute_raw_kilos_dest(self):
        self.raw_kilos_dest = self.input_kilos_dest - self.output_kilos_dest

    @api.one
    @api.depends('raw_kilos_dest', 'humidity_rate_dest')
    def _compute_humid_kilos_dest(self):
        if self.humidity_rate_dest > 14:
            self.humid_kilos_dest = round(self.raw_kilos_dest * (self.humidity_rate_dest - 14) * .0116)
        else:
            self.humid_kilos_dest = 0

    @api.one
    @api.depends('raw_kilos_dest', 'damage_rate_dest')
    def _compute_damaged_kilos_dest(self):
        if self.damage_rate_dest > 5:
            self.damaged_kilos_dest = round(self.raw_kilos_dest * (self.damage_rate_dest - 5) / 100)
        else:
            self.damaged_kilos_dest = 0

    @api.one
    @api.depends('raw_kilos_dest', 'break_rate_dest')
    def _compute_broken_kilos_dest(self):
        if self.break_rate_dest > 2:
            self.broken_kilos_dest = round(self.raw_kilos_dest * (self.break_rate_dest - 2) / 100)
        else:
            self.broken_kilos_dest = 0

    @api.one
    @api.depends('raw_kilos_dest', 'impurity_rate_dest')
    def _compute_impure_kilos_dest(self):
        if self.impurity_rate_dest > 2:
            self.impure_kilos_dest = round(self.raw_kilos_dest * (self.impurity_rate_dest - 2) / 100)
        else:
            self.impure_kilos_dest = 0

    @api.one
    @api.depends('humid_kilos_dest', 'damaged_kilos_dest', 'broken_kilos_dest', 'impure_kilos_dest')
    def _compute_deducted_kilos_dest(self):
        self.deducted_kilos_dest = self.humid_kilos_dest + self.damaged_kilos_dest + self.broken_kilos_dest + self.impure_kilos_dest

    @api.one
    @api.depends('raw_kilos_dest', 'deducted_kilos_dest')
    def _compute_clean_kilos_dest(self):
        self.clean_kilos_dest = self.raw_kilos_dest - self.deducted_kilos_dest

    @api.one
    @api.depends('clean_kilos_dest')
    def _compute_difference_kilos(self):
       self.difference = float(self.clean_kilos_dest) - float(self.clean_kilos)

     
    @api.onchange('stock_origin', 'stock_destination')
    def _change_stock_create(self):
        if (self.stock_origin):
            self.stock_destination = False
        elif (self.stock_destination):
            self.stock_origin = False
