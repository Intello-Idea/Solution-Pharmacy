# -*- coding: utf-8 -*-
# from odoo import http


# class BonificationSolution(http.Controller):
#     @http.route('/bonification_solution/bonification_solution/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bonification_solution/bonification_solution/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bonification_solution.listing', {
#             'root': '/bonification_solution/bonification_solution',
#             'objects': http.request.env['bonification_solution.bonification_solution'].search([]),
#         })

#     @http.route('/bonification_solution/bonification_solution/objects/<model("bonification_solution.bonification_solution"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bonification_solution.object', {
#             'object': obj
#         })
