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
    """,
    'author': 'Damian Mazepa',
    'depends': ['base', 'sale', 'calendar', 'contacts', 'sale', 'hr', 'fleet'],
    'data': [
        'views/transport_order_view.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/transport_place_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}