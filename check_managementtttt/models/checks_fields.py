# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions,_
import odoo.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from odoo.fields import Date as fDate
import logging
_logger = logging.getLogger(__name__)
class check_management(models.Model):

    _name = 'check.management'
    _description = 'Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'check_number'

    check_number = fields.Char(string=_("Check Number"),required=True,default="0")
    check_date = fields.Date(string=_("Check Date"),required=True)
    check_payment = fields.Date(string=_("Check Payment"),required=True)
    check_bank = fields.Many2one('res.bank', string=_('Check Bank'))
    dep_bank = fields.Many2one('res.bank', string=_('Depoist Bank'))
    amount = fields.Float(string=_('Check Amount'),digits=dp.get_precision('Product Price'))

    amount_reg = fields.Float(string="Check Regular Amount", digits=dp.get_precision('Product Price'))


    open_amount_reg = fields.Float(string="Check Regular Open Amount", digits=dp.get_precision('Product Price'))

    open_amount = fields.Float(string=_('Open Amount'), digits=dp.get_precision('Product Price'),track_visibility='onchange')
    investor_id = fields.Many2one('res.partner',string=_("Partner"))

    check_id=fields.Integer(string="cheque Id")
    bank_deposite=fields.Many2one('res.bank',string="البنك المسحوب عليه")



    type = fields.Selection(string="Type", selection=[('reservation', 'Reservation Installment'),
                                                      ('contracting', 'Contracting Installment'),
                                                      ('regular', 'Regular Installment'),
                                                      ('ser', 'Services Installment'),
                                                      ('garage', 'Garage Installment'),
                                                      ('mod', 'Modification Installment'),
                                                      ], required=True,translate=True,
                            default="regular")
    state = fields.Selection(selection=[('holding','Holding'),('depoisted','Depoisted'),
                                         ('approved','Approved'),('rejected','Rejected')
                                         , ('returned', 'Returned'), ('handed', 'Handed'),
                                        ('debited', 'Debited'),('canceled', 'Canceled'),('cs_return','Customer Returned'),
                                        ('vendor_return','vendor Returned')]
                             ,translate=True,track_visibility='onchange')

    notes_rece_id = fields.Many2one('account.account')
    under_collect_id  = fields.Many2one('account.account')
    notespayable_id = fields.Many2one('account.account')
    under_collect_jour = fields.Many2one('account.journal')
    under_debited = fields.Many2one('account.journal')
    deposited_journal = fields.Many2one('account.journal')
    check_type = fields.Selection(selection=[('rece','Notes Receivable'),('pay','Notes Payable')])
    check_state = fields.Selection(selection=[('active','Active'),('suspended','Suspended')],default='active')
    check_from_check_man = fields.Boolean(string="Check Managment",default=False)
    #will_collection = fields.Date(string="Maturity Date" , compute = "_compute_days")
    will_collection_user = fields.Date(string="Bank Maturity Date"  ,track_visibility='onchange')
    payment_line = fields.Many2one('native.payments.check.create',compute='_get_state')

    new_due_date = fields.Date('تاريخ الاستحقاق الجديد')

    # @api.multi
    # def _compute_days(self):
    #     d1=datetime.strptime(str(self.check_date),'%Y-%m-%d')
    #     self.will_collection= d1 + timedelta(days=10)
    @api.multi
    @api.depends('check_id','state')
    def _get_state(self):
        print(">>>>>>>>")
        checks = self.env['check.management'].search([])
        for rec in checks:
            normal = self.env['native.payments.check.create'].search([('id', '=', rec.check_id)])
            rec.payment_line=normal.id

            rec.payment_line.state=rec.state
            rec.payment_line.write({'state':rec.state})


            print("state", rec.payment_line.state)
            print("state", rec.payment_line)

    @api.model
    def create(self,vals):
        check_object=self.env['check.management'].search([('check_number','=',self.check_number)]) 
        _logger.info(check_object.state)

        if 'amount' in vals:
            vals['open_amount'] = vals['amount']
        return super(check_management,self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'amount' in vals:
                rec.open_amount = vals['amount']
        return super(check_management, self).write(vals)


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,submenu=False):
        res = super(check_management, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
        _logger.info('MENU SENT')
        _logger.info(res)
        _logger.info(self.check_type)
         
        if 'fields' in res:
            if 'state' in res['fields']:
                if 'menu_sent' in self.env.context:
                    """if self.env.context['menu_sent'] in ('handed','debited'):
                        _logger.info('HANDED OR DEBITED')

                        res['fields']['state']['selection'] = [('handed', 'Handed'), ('debited', 'Debited')]
                        if self.env.context['lang'] == 'ar_SY':
                            res['fields']['state']['selection'] = [('handed', 'مسلمة'), ('debited', 'محصلة')]
                    else:
                        res['fields']['state']['selection'] = [('holding', 'Holding'), ('depoisted', 'Depoisted'), ('approved', 'Approved'),
                                                               ('rejected', 'Rejected'), ('returned', 'Returned'),('canceled', 'Canceled')
                                                               ,('cs_return','Customer Returned')]
                        if self.env.context['lang'] == 'ar_SY':
                            res['fields']['state']['selection'] = [('holding', 'قابضة'), ('depoisted', 'تحت التحصيل'),
                                                                   ('approved', 'خالصة'),('rejected', 'مرفوضة'), ('returned', 'مرتجعة'),
                                                                   ('canceled', 'ملغله'),('cs_return','مرتجع للعميل')]"""

                    _logger.info('ALL PAYABLE')
                    _logger.info(res['fields']['state']['selection'])
        if 'toolbar' in res:
            if 'menu_sent' in self.env.context:
                
                if self.env.context['menu_sent'] == 'holding':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for i in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][i]['name'] =="رفض شيــك":
                                del res['toolbar']['action'][i]
                                break
                        for i in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][i]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][i]
                                break
                        for i in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][i]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][i]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                         
                    elif self.env.context['lang'] == 'en_US':
                        for i in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][i]['name'] == 'Reject Checks':
                                del res['toolbar']['action'][i]
                                break
                        for i in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][i]['name'] == 'Company Return':
                                del res['toolbar']['action'][i]
                                break
                        for i in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][i]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][i]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                del res['toolbar']['action'][j]
                                break
                if self.env.context['menu_sent'] == 'depoist':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "تقسيم الشيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                    elif self.env.context['lang'] == 'en_US':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Company Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Customer Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                                del res['toolbar']['action'][j]
                                break


                if self.env.context['menu_sent'] == 'approved':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "تقسيم الشيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                        
                    elif self.env.context['lang'] == 'en_US':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Company Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Customer Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                                del res['toolbar']['action'][j]
                                break


                if self.env.context['menu_sent'] == 'rejected':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                         
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "تقسيم الشيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                               
                    elif self.env.context['lang'] == 'en_US':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                del res['toolbar']['action'][j]
                                break
                        
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                                del res['toolbar']['action'][j]
                                break

                if self.env.context['menu_sent'] == 'returned':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                    elif self.env.context['lang'] == 'en_US':
                            for j in range(len(res['toolbar']['action'])):
                                if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                                    del res['toolbar']['action'][j]
                                    break
                            for j in range(len(res['toolbar']['action'])):
                                if res['toolbar']['action'][j]['name'] == 'Company Return':
                                    del res['toolbar']['action'][j]
                                    break
                            for j in range(len(res['toolbar']['action'])):
                                if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                    del res['toolbar']['action'][j]
                                    break
                            for j in range(len(res['toolbar']['action'])):
                                if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                    del res['toolbar']['action'][j]
                                    break

                         


                if self.env.context['menu_sent'] == 'handed':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                         
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                elif self.env.context['lang'] == 'en_US':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break



                if self.env.context['menu_sent'] == 'debited':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':

                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "تقسيم الشيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                         
                    elif self.env.context['lang'] == 'en_US':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Company Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Customer Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                                del res['toolbar']['action'][j]
                                break
                if self.env.context['menu_sent'] == 'canceled':
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Company Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Customer Return':
                            del res['toolbar']['action'][j]
                            break
                    for j in range(len(res['toolbar']['action'])):
                        if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                            del res['toolbar']['action'][j]
                            break

                if self.env.context['menu_sent'] == 'vendor_return':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "تقسيم الشيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك للـــشركه":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                if self.env.context['menu_sent'] == 'cs_return':
                    if self.env.context['lang'] == 'ar_SY' or self.env.context['lang'] == 'ar_AA':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "اعتمــــــــاد الشيك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "رفض شيــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ايــــــداع شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "صــرف شيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "ارجاع الشيك  للعميل ":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == "تقسيم الشيــــك":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك للمورد":
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] ==  "ارجاع الشيك الي الشيكات الصادره":
                                del res['toolbar']['action'][j]
                                break
                    elif self.env.context['lang'] == 'en_US':
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Approve Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Reject Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Company Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Cancel Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Depoist Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Debit Checks':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Customer Return':
                                del res['toolbar']['action'][j]
                                break
                        for j in range(len(res['toolbar']['action'])):
                            if res['toolbar']['action'][j]['name'] == 'Split-Merge':
                                del res['toolbar']['action'][j]
                                break
        return res
