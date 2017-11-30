# -*- coding: utf-8 -*-
from odoo import http

# class TruckInternal(http.Controller):
#     @http.route('/truck_internal/truck_internal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/truck_internal/truck_internal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('truck_internal.listing', {
#             'root': '/truck_internal/truck_internal',
#             'objects': http.request.env['truck_internal.truck_internal'].search([]),
#         })

#     @http.route('/truck_internal/truck_internal/objects/<model("truck_internal.truck_internal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('truck_internal.object', {
#             'object': obj
#         })