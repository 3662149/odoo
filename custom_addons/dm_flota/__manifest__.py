# -*- coding: utf-8 -*-
{
    'name': 'Damian Mazepa Flota',
    'version': '0.1',
    'summary': 'Moduł rozbudowujący fleet',
    'description': """
Moduł utworzony w ramach pracy inżynierskiej
Wydział Matematyki i Informatyki
Uniwesytet Mikołaja Kopernika w Toruniu 2021/2022r.
================================
Uses OSRM API based on BSD 2-Clause licence https://choosealicense.com/licenses/bsd-2-clause/ https://project-osrm.org/
    """,
    'author': 'Damian Mazepa',
    'depends': ['base', 'sale', 'calendar', 'contacts', 'sale', 'hr', 'fleet', 'mail'],
    'data': [
        'views/transport_order_view.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/transport_place_view.xml',
        'views/hr_employee_view.xml',
        'data/cron.xml',
        'wizard/end_cargo_wizard_view.xml',
        'views/fleet_vehicle_log_services_view.xml',
        'views/fleet_vehicle_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}