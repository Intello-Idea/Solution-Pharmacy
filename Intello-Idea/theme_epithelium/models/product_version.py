from odoo import models, fields, api
import xmltodict
import pprint
import json
from xml.etree.ElementTree import Element
from lxml import etree
import xml.etree.ElementTree as ET


class ProductVersion(models.Model):
    _name = "product.version"
    _description = "Product version Epithelium"


    product_id = fields.Many2one("product.template")
    name = fields.Char()
    icon = fields.Binary()
    description = fields.Html()
