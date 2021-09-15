# -*- coding: utf-8 -*-
# from odoo import http


# class Solution-pharmacy(http.Controller):
#     @http.route('/solution-pharmacy/solution-pharmacy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solution-pharmacy/solution-pharmacy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('solution-pharmacy.listing', {
#             'root': '/solution-pharmacy/solution-pharmacy',
#             'objects': http.request.env['solution-pharmacy.solution-pharmacy'].search([]),
#         })

#     @http.route('/solution-pharmacy/solution-pharmacy/objects/<model("solution-pharmacy.solution-pharmacy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solution-pharmacy.object', {
#             'object': obj
#         })
