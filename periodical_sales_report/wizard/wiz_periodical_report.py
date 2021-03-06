
from odoo import api, fields, models


class PeriodicalReportWizard(models.TransientModel):
    _name = "periodical.report.wizard"

     
    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    customer=fields.Many2one('res.partner','العميل',domain="[('customer','=',True)]")
    product=fields.Many2one('product.product','المنتج')
    analytical_account_id=fields.Many2one('account.analytic.account',string="الحساب التحليلي")
    @api.multi
    def check_report(self):
        
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'customer':self.customer.id,
                'product':self.product.id,
                'analytical_account_id':self.analytical_account_id.id
               
            },
        }
        return self.env.ref('periodical_sales_report.action_report_periodical_sales').report_action(self, data=data)
