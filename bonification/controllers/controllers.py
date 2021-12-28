# -*- coding: utf-8 -*-
# from odoo import http


# class Bonification(http.Controller):
#     @http.route('/bonification/bonification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bonification/bonification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bonification.listing', {
#             'root': '/bonification/bonification',
#             'objects': http.request.env['bonification.bonification'].search([]),
#         })

#     @http.route('/bonification/bonification/objects/<model("bonification.bonification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bonification.object', {
#             'object': obj
#         })
