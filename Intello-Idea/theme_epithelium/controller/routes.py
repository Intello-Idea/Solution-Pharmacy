# -- coding: utf-8 --
import odoo.http as http
from odoo import api


class RoutesWebSite(http.Controller):
    @http.route('/purchases', type='http', auth="public", website=True)
    def show_purchases_web_page(self, **kw):
        # ruta purchases: renderiza la pagina de ventas
        return http.request.render('theme_epithelium.web_purchases', {})

    # ruta (/) home: renderiza la pagina de inicio
    @http.route('/', type='http', auth="public", website=True)
    def show_home_web_page(self, **kwargs):
        # var (categories): llama y almacena todas las categorias website
        categories = http.request.env['product.category.website'].sudo().search([])
        # var (locationsMap): llama y almacena todas las localizaciones de la tienda
        locationsMap = http.request.env['location.epithelium'].sudo().search([])
        # var (locations): lista vacia donde se guardaran todas las localizaciones pero con los datos que necesitamos para la pagina
        locations = []
        for locMap in locationsMap:
            # bloque if: construye el texto de localizacion con la calle y la ubicacion especifica
            if locMap["location"]:
                location = locMap["location"]
            else:
                location = ""
            if locMap["street"]:
                street = locMap["street"]
            else:
                street = ""
            # var (address): almacena el texto completo de la ubicacion
            address = street + " " + location
            # guardamos un diccionario con los dattos que necesitamos en la pagina
            locations.append({
                'id': locMap["id"],
                'name': locMap["name"],
                'city': locMap["city_store"]["name"],
                'id_city': locMap["city_store"]["id"],
                'map': locMap["google_map"],
                'lat': locMap["lat"],
                'lng': locMap["lng"],
                'address': address,
                'shedule': 'Horario: ' + str(locMap["schedule"]),
            })
        # bloque if: se guardan las categorias por listas, dependiendo del numero de categorias que hayan
        if categories:
            list_categ = []
            list_categ_2 = []
            cont = 0

            for category in categories:
                cont += 1
                list_categ.append(category)

                if cont % 2 == 0:
                    list_categ_2.append(list_categ)
                    list_categ = []

            if len(list_categ) > 0:
                list_categ_2.append(list_categ)
            # si todo sale bien, se renderiza la pagina, este render lleva un filtro de mapas por defecto que es 0
            return http.request.render('theme_epithelium.home_page_ep',
                                       {'list_categories': list_categ_2, 'locations': locations, 'filter_map': 0,
                                        'google_key': http.request.env[
                                            'website'].get_current_website().google_maps_api_key})
        else:
            return http.request.render('http_routing.404', {})

    # ruta (/category/id=<int:id>) categoria: renderiza la pagina de categoria de pendiendo del parametro que s ele pase
    # parametro (<id=<int:id>): id de una categoria
    @http.route('/category/id=<int:id>', type='http', auth="public", website=True)
    def show_category_web_page(self, **kwargs):
        # var (param): almacena el parametro que se le pasa a la ruta
        param = kwargs.get('id')
        # var (category): almacena la categoria website filtrando la llamada por el parametro de la ruta
        category = http.request.env['product.category.website'].sudo().search([('id', '=', param)])
        # var (products): almacena los productos de la categoria website filtrando la llamada por el parametro de la ruta, y los productos website = True
        products = http.request.env["product.template"].sudo().search(
            ['&', ('website_category.id', '=', param), ('website', '=', True)])
        # bloque if: si se encuentra la categoria se renderiza la pagina
        if category:
            return http.request.render('theme_epithelium.web_category', {'category': category, 'products': products})
        else:
            return http.request.render('http_routing.404', {})

    # ruta (/product/id=<int:id>) producto: renderiza la pagina de producto dependiendo del parametro que se le pase
    # parametro (<id=<int:id>): id de un producto
    @http.route('/product/id=<int:id>', type='http', auth="public", website=True)
    def show_product_web_page(self, **kwargs):
        # var (param): almacena el parametro que se le pasa a la ruta
        param = kwargs.get('id')
        # var (product): almacena el producto website filtrando la llamada por el parametro de la ruta y los productos website = True
        product = http.request.env["product.template"].sudo().search(['&', ('id', '=', param), ('website', '=', True)])
        # bloque if: si se encuentra el producto se renderiza la pagina de producto
        if product:
            return http.request.render('theme_epithelium.web_product', {'product': product})
        else:
            return http.request.render('http_routing.404', {})

    # ruta (/master_forms) formalas magistrales: renderiza la pagina de formulas magistrales
    @http.route('/master_forms', type='http', auth="public", website=True)
    def show_master_forms_web_page(self, **kw):
        # var (product): almacena las formulas magistrales
        forms = http.request.env['product.form.magistral'].sudo().search([])
        # bloque if: guarda las formulas magistrales por listas
        if forms:
            list_form = []
            list_form_2 = []
            cont = 0

            for form in forms:
                cont += 1
                list_form.append(form)

                if cont % 4 == 0:
                    list_form_2.append(list_form)
                    list_form = []

            if len(list_form) > 0:
                list_form_2.append(list_form)

            return http.request.render('theme_epithelium.web_master_forms', {'list_form': list_form_2})
        else:
            return http.request.render('http_routing.404', {})

    # ruta (/master_forms/id=<int:id) formalas magistrales: renderiza la pagina de formula magistral dependiendo del parametro que se le pase
    @http.route('/master_form/id=<int:id>', type='http', auth="public", website=True)
    def show_master_form_web_page(self, **kwargs):
        # var (id): almacena el parametro de la ruta
        id = kwargs.get('id')
        # var (form): almacena la formula magistral filtrando en la llamada el parametro de la ruta
        form = http.request.env['product.form.magistral'].sudo().search([('id', '=', id)])
        # bloque if: si se encuentra la formula se renderiza la pagina
        if form:
            return http.request.render('theme_epithelium.web_master_form', {'form': form})
        else:
            return http.request.render('http_routing.404', {})

    # ruta (/info_master_form) informacion de formulas magistrales: renderiza la pagina de info. de formulas magistrales
    @http.route('/info_master_form', type='http', auth="public", website=True)
    def show_info_master_form_web_page(self, **kw):
        return http.request.render('theme_epithelium.web_info_master_form', {})

    # ruta (/products/cat_id=<int:id>) productos terminados: renderiza la pagina de productos dependiendo de la categoria
    @http.route('/products/cat_id=<int:id>', type='http', auth="public", website=True)
    def show_products_form_magistral_web_page(self, **kwargs):
        # var (param): almacena el parametro de la ruta
        param = kwargs.get('id')
        # var (form_magistral): almacena la formula magistral filtrando en la llamada el parametro de la ruta
        form_magistral = http.request.env["product.form.magistral"].sudo().search([('id', '=', param)])
        # var (products): almacena los productos website filtrando la llamada por el parametro de la ruta y los productos website = True
        products = http.request.env["product.template"].sudo().search(
            [('form_magistral.id', '=', param), ('website', '=', True)])
        if form_magistral:
            return http.request.render('theme_epithelium.web_products_forms',
                                       {"form_magistral": form_magistral, 'products': products})
        else:
            return http.request.render('http_routing.404', {})

    # ruta (/home/id_filter_map=<int:id>) home: renderiza la pagina de inicio
    # parametro id_filter_map=<int:id>: parametro para filtrar las localizaciones del mapa segun la ciudad
    @http.route('/home/id_filter_map=<int:id>', type='http', auth="public", website=True)
    def show_homepage_web_page(self, **kwargs):
        # var (id): almacena el parametro que se le pasa a la ruta
        id = kwargs.get('id')
        # var (categories): llama y almacena todas las categorias website
        categories = http.request.env['product.category.website'].sudo().search([])
        # var (locationsMap): llama y almacena todas las localizaciones de la tienda
        locationsMap = http.request.env['location.epithelium'].sudo().search([])
        # var (locations): lista vacia donde se guardaran todas las localizaciones pero con los datos que necesitamos para la pagina
        locations = []
        for i in locationsMap:
            # bloque if: construye el texto de localizacion con la calle y la ubicacion especifica
            if i["location"]:
                location = i["location"]
            else:
                location = ""
            if i["street"]:
                street = i["street"]
            else:
                street = ""
            # var (address): almacena el texto completo de la ubicacion
            address = street + " " + location
            # guardamos un diccionario con los dattos que necesitamos en la pagina
            locations.append({
                'id': i["id"],
                'name': i["name"],
                'city': i["city_store"]["name"],
                'id_city': i["city_store"]["id"],
                'map': i["google_map"],
                'lat': i["lat"],
                'lng': i["lng"],
                'address': address,
                'shedule': 'Horario: Lunes a Jueves: 9:00am a 8:30pm',
            })
        # bloque if: se guardan las categorias por listas, dependiendo del numero de categorias que hayan
        if categories:
            list_categ = []
            list_categ_2 = []
            cont = 0

            for category in categories:
                cont += 1
                list_categ.append(category)

                if cont % 3 == 0:
                    list_categ_2.append(list_categ)
                    list_categ = []

            if len(list_categ) > 0:
                list_categ_2.append(list_categ)
            # si todo sale bien, se renderiza la pagina, este render lleva un filtro de mapas que es el parametro de la ruta
            return http.request.render('theme_epithelium.home_page_ep',
                                       {'list_categories': list_categ_2, 'locations': locations, 'filter_map': id,
                                        'google_key': http.request.env[
                                            'website'].get_current_website().google_maps_api_key})
        else:
            return http.request.render('http_routing.404', {})

    @http.route('/contactus-thank-you', type='http', auth='public', website=True)
    def show_tranks_form_web_page(self):
        return http.request.render('theme_epithelium.contactus_thanks_ep', {})
