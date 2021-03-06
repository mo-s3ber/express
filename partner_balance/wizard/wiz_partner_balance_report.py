from odoo import api, fields, models


class Partnerblance(models.TransientModel):
    _name = "partner.balance"

     
    date_from = fields.Date(string='تاريخ البدء')
    date_to = fields.Date(string='تاريخ الانتهاء')
    partner=fields.Many2one('res.partner','الشريك')
    vendor_mode=fields.Boolean('Vendor',default=False)
    analytical_account_id=fields.Many2one('account.analytic.account',string="الحساب التحليلي")
    @api.onchange('vendor_mode')
    def get_partner(self):
        if self.vendor_mode==True:
            return{'domain':{'partner':[('supplier','=',True)]}}
        else:
             return{'domain':{'partner':[('customer','=',True)]}}
    @api.multi
    def check_report(self):
        
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'partner':self.partner.id,
                'vendor_mode':self.vendor_mode,
                'analytical_account_id':self.analytical_account_id.id


            },
        }
        return self.env.ref('partner_balance.action_report_partner_balance').report_action(self, data=data)
