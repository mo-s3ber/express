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

from odoo import api, fields, models


class PeriodicalReportProduct(models.TransientModel):
    _name = "vendor.cheques"

     
    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    vendor=fields.Many2one('res.partner','المورد',domain="[('supplier','=',True)]")
    state = fields.Selection(selection=[('holding','خزنة'),('depoisted','تحت التحصيل'),
                                         ('approved','معتمدة'),('rejected','مرفوض')
                                         , ('returned', 'مرتجعة'), ('handed', 'صادرة'),
                                        ('debited', 'مدينه'),('canceled', 'ملغية'),('cs_return','مرتجعه للعميل')]
                             ,string='الحالة')
    due_date_from=fields.Date(string=' تاريخ الاستـــحقاق من  ')
    due_date_to=fields.Date(string=' تاريخ الاستـــحقاق الـــي  ')
    @api.multi
    def check_report(self):
         
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'vendor':self.vendor.id,
                'state':self.state,
                'due_date_from':self.due_date_from,
                'due_date_to':self.due_date_to


            },
        }
        return self.env.ref('vendor_cheques.action_report_vendor_cheques').report_action(self, data=data)
