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
    _name = "total.transactions"

     
    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    account_id = fields.Many2one('account.account', string='الحساب')
    journal_id = fields.Many2one('account.journal', string='قيد اليومي',domain=[('type','=','cash')])
    @api.onchange("account_id")
    def get_domain(self):
        user_log=self.env['res.users'].search([('id','=',self.env.uid)])
        if user_log.lang=='en_US':
            return {'domain':{'journal_id':[('type','=','cash')]}}
        elif user_log.lang=='ar_SY' or user_log.lang=='ar_AA':
            return {'domain':{'account_id':[('user_type_id','=','بنك ونقدية')]}}
  

        
    @api.onchange("account_id")
    def get_domain(self):
        user_log=self.env['res.users'].search([('id','=',self.env.uid)])
        if user_log.lang=='en_US':
            return {'domain':{'account_id':[('user_type_id','=','Bank and Cash')]}}
        elif user_log.lang=='ar_SY' or user_log.lang=='ar_AA':
            return {'domain':{'account_id':[('user_type_id','=','بنك ونقدية')]}}

    @api.multi
    def check_report(self):
         
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'account_id':self.account_id.id,
                'journal_id':self.journal_id.id

            },
        }
        return self.env.ref('total_transactions.action_report_total_transactions').report_action(self, data=data)
    
    def check_debit_report(self):
         
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'account_id':self.account_id.id,
                'journal_id':self.journal_id.id

            },
        }
        return self.env.ref('total_transactions.action_report_total_debit_transactions').report_action(self, data=data)
    
    def check_credit_report(self):
         
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'account_id':self.account_id.id,
                'journal_id':self.journal_id.id

            },
        }
        return self.env.ref('total_transactions.action_report_total_credit_transactions').report_action(self, data=data)