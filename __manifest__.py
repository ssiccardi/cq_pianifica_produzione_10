# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 CQ creativiquadrati snc
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Pianificazione Produzione',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'description': """
Pianificazione produzione per r.10.0
=======================================
 * Aggiunge calendario per prevedere/pianificare gli ordini di produzione
""",
    'author': 'Stefano Siccardi @ Creativi Quadrati',
    'website': 'http://www.creativiquadrati.it',
    'license': 'AGPL-3',
    'depends': ['mrp','cq_hydronit_2017'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/config_risorse_view.xml',
        'views/reparti_view.xml',
        'wizard/calcola_risorse_view.xml',
        'wizard/pianifica_mo_view.xml', 
                
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True
}
