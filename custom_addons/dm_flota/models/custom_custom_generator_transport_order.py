import xmlrpc.client
from random import randint, choice, uniform

url = 'http://localhost:8069'
db = 'odoo_factory_new'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

HOW_MANY_ORDERS = 3


currency_id = 17
tax_id = 1
a = randint(0, 23)
b = randint(10, 59)
c = randint(10, 59)
if a < 10:
    a = '0' + str(a)
if b < 10:
    b = '0' + str(b)
if c < 10:
    c = '0' + str(c)
data = f'2021-10-21 {a}:{b}:{c}'


klienci = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['id', 'not in', (3, 1, 2)]]], {'fields': ['name']})
miejsca = models.execute_kw(db, uid, password, 'transport.place', 'search_read', [[]], {'fields': ['name']})
kierowcy = models.execute_kw(db, uid, password, 'hr.employee', 'search_read', [[]], {'fields': ['name']})
pojazdy = models.execute_kw(db, uid, password, 'fleet.vehicle', 'search_read', [[]], {'fields': ['name']})
produkty = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id', 'not in', (9,10,11,12,13)]]], {'fields': ['name']})

for i in range(HOW_MANY_ORDERS):
    print(str(i), ' / ', HOW_MANY_ORDERS)
    klient = choice(klienci)
    inicjaly = klient['name'].split(' ')[0][0] + klient['name'].split(' ')[1][0]
    while True:
        od = choice(miejsca)
        if od['name'][:2] == inicjaly:
            break
    while True:
        do = choice(miejsca)
        if do['name'][:2] != inicjaly:
            break

    cargo_lines = []
    for line in range(randint(1, 4)):
        cargo_lines.append((0, 0, {
            'product_id': choice(produkty)['id'],
            'quantity':  randint(6000, 18000),
            'price_unit': round(uniform(0.1, 6.3), 2),
            'tax_ids': [(6, 0, [tax_id])]
        }))

    models.execute_kw(db, uid, password, 'transport.order', 'create', [{
        'partner_id': klient['id'],
        'date_of_departure': data,
        'place_from': od['id'],
        'place_to': do['id'],
        'driver_id': choice(kierowcy)['id'],
        'vehicle_id': choice(pojazdy)['id'],
        'currency_id': currency_id,
        'cargo_ids': cargo_lines
    }])
