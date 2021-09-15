from odoo import models, fields, api, exceptions
import requests
from urllib.parse import urlencode


class City(models.Model):
    _name = "location.city.epithelium"
    _description = "Location City Epithelium"

    name = fields.Char()


class Location(models.Model):
    _name = "location.epithelium"
    _description = "Location Epithelium"

    name = fields.Char(string="Store name")
    lat = fields.Char(string="latitude", compute="_google_maps", store=True, default="0")
    lng = fields.Char(string="length", compute="_google_maps", store=True, default="0")
    google_map = fields.Char(string="Code google map", compute="_google_maps", store=True)
    phone = fields.Char()
    zone = fields.Selection([("N", "North"),
                             ("S", "South"),
                             ("E", "East"),
                             ("O", "West"),
                             ("C", "Center"),
                             ("NO", "Northwest"),
                             ("NE", "Northeast"),
                             ("SO", "Southwest"),
                             ("SE", "Southeast")])
    street = fields.Char()
    location = fields.Char()
    city_store = fields.Many2one("location.city.epithelium")
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one(
        'res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    schedule = fields.Char(string="Schedule")

    @api.depends("street", "zone", "city_store", "state_id", "country_id")
    def _google_maps(self):
        # method_google_maps: Este metodo hace el llamado api a google maps
        #: depende de los campos que van a ser enviados a la llamada api
        for loc in self:
            if loc.lng == '0' and loc.lat == '0':
                data_type = 'json'
                endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/{data_type}"
                # input: nombre de la ubicacion que se va a enviar como parametro a la llamada api
                input = loc.name_search_maps()
                # params: parametros utilizados para lallamada api
                params = {"input": input,
                          "inputtype": "textquery",
                          "fields": "plus_code,geometry",
                          "key": self.env['website'].get_current_website().google_maps_api_key,
                          }
                # url_params: decodifica la url con los parametros
                url_params = urlencode(params)
                url = f"{endpoint}?{url_params}"
                try:
                    # res: llamada a la api de google
                    res = requests.get(url)
                    # data: convertir diccionario python a json
                    data = res.json()
                    try:
                        # block if: almacena el valor de latitud y longitud
                        if "geometry" in data["candidates"][0]:
                            loc.lat = data["candidates"][0]["geometry"]["location"]["lat"]
                            loc.lng = data["candidates"][0]["geometry"]["location"]["lng"]
                        else:
                            loc.lat = 0
                            loc.lng = 0
                    except:
                        loc.lat = 0
                        loc.lng = 0
                    try:
                        # block if: almacena el valor de codigo de google maps
                        if "plus_code" in data["candidates"][0]:
                            loc.google_map = data["candidates"][0]["plus_code"]["global_code"]
                        else:
                            loc.google_map = ""
                    except:
                        loc.google_map = ""
                except:
                    raise exceptions.ValidationError("Internet connection is unstable")

    def name_search_maps(self):
        # method_name_search_maps: construye el texto que se va a enviar a la llamada api
        for loc in self:
            name_search = ""
            if loc.street:
                name_search = name_search + "" + loc.street
            if loc.zone:
                name_search = name_search + "," + dict(loc._fields['zone'].selection).get(loc.zone)
            if loc.city_store:
                name_search = name_search + "," + loc.city_store.name
            if loc.state_id:
                name_search = name_search + "," + loc.state_id.name
            if loc.country_id:
                name_search = name_search + "," + loc.country_id.name
            return name_search

    def compute_lat_lng(self):
        self._google_maps()
