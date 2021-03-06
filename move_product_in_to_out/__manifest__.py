# -*- coding: utf-8 -*-

###############################################################################
#
#    Periodical Sales Report
#
#    Copyright (C) 2019 Aminia Technology
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
###############################################################################

{
    'name' : 'Move product in out ',
    'version' : '12.0.1',
    'summary': 'Module move  product in and out.',
    'sequence': 16,
    'category': 'Purchase',
    'author' : 'BBl',
    'description': """
Custom Sales Report
=====================================
This module print daily, last week and last month sale report.
Also print report for particular duration.
    """,
    "license": "AGPL-3",
    'depends' : ['base_setup', 'sale_management','purchase'],
    'data': [
        'wizard/wiz_periodical_report_view.xml',
        'views/move_in_out_report_product.xml',
        'views/report_move_in_out_product.xml'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
