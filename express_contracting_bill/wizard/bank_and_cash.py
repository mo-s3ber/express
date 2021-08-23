# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import ValidationError
import base64
import xlsxwriter
import io
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from datetime import datetime
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import date
import datetime


def is_int(n):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError:
        return False
    else:
        return float_n == int_n


def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True


class BankCashWizard(models.TransientModel):
    _name = "bank.cash.report"

    date_from = fields.Date()
    date_to = fields.Date()
    journal_ids = fields.Many2many(
        comodel_name="account.journal",
    )
    total = fields.Boolean()
    excel_sheet = fields.Binary('Download Report')

    @api.constrains('date_from', 'date_to')
    def _validate_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_('"Date To" time cannot be earlier than "Date From" time.'))

    def generate_data(self, account):
        domain = []
        if self.journal_ids:
            domain.append(('journal_id', 'in', [x.id for x in self.journal_ids]))
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        domain.append(('move_id.state', '=', 'posted'))
        domain.append(('account_id', '=', account.id))
        moves = self.env['account.move.line'].search(domain)

        return moves

    @api.multi
    def get_all_move(self):
        if self.total:
            sql = "SELECT move.account_id as account,SUM(move.debit) AS debit,SUM(move.credit) AS credit from account_move_line move LEFT JOIN account_move a ON (move.move_id=a.id) LEFT JOIN account_account account ON (move.account_id=account.id) JOIN account_journal jor ON (move.journal_id=jor.id) WHERE jor.id IN %s AND a.date >= %s AND a.date <= %s AND a.state = 'posted' GROUP BY account;"
            self.env.cr.execute(sql,(tuple(self.journal_ids.ids),self.date_from,self.date_to))
        else:
            sql = "SELECT move.date AS date,move.name AS label,account.name AS acc_name,move.debit AS debit,move.credit AS credit from account_move_line move LEFT JOIN account_move a ON (move.move_id=a.id) LEFT JOIN account_account account ON (move.account_id=account.id) JOIN account_journal jor ON (move.journal_id=jor.id) WHERE jor.id IN %s AND a.date >= %s AND a.date <= %s AND a.state = 'posted';"
            self.env.cr.execute(sql,(tuple(self.journal_ids.ids),self.date_from,self.date_to))
        res_all = self.env.cr.fetchall()
        return res_all


    @api.multi
    def generate_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        custom_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 8,
            'fg_color': 'white',
        })

        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'text_wrap': True,
            'font_size': 10,
            'valign': 'vcenter',
            'fg_color': '#d8d6d6'
        })

        worksheet = workbook.add_worksheet('Bank and Cash')
        worksheet.set_paper(9)
        worksheet.set_portrait()
        worksheet.merge_range(0, 0, 1, 4, 'تقرير أجمالي خزينة او بنك', table_header_format)
        if self.date_from and self.date_to:
            worksheet.write(2, 1, 'من', table_header_format)
            worksheet.write(2, 2, str(self.date_from), table_header_format)
            worksheet.write(2, 3, 'الي', table_header_format)
            worksheet.write(2, 4, str(self.date_to), table_header_format)
        row = 3
        if not self.total:
            worksheet.write(row, 0, 'التاريخ', table_header_format)
            worksheet.write(row, 1, 'الاذن', table_header_format)
            worksheet.write(row, 2, 'أسم الحساب', table_header_format)
            worksheet.write(row, 3, 'مدين', table_header_format)
            worksheet.write(row, 4, 'داين', table_header_format)
            row += 1
            col = 0
            debit = 0.0
            credit = 0.0
            for acc in self.get_all_move():
                worksheet.write(row, col, str(acc[0]), custom_format)
                worksheet.write(row, col + 1, str(acc[1]), custom_format)
                worksheet.write(row, col + 2, str(acc[2]), custom_format)
                worksheet.write(row, col + 3, round(acc[3], 2), custom_format)
                debit += round(acc[3], 2)
                worksheet.write(row, col + 4, round(acc[4], 2), custom_format)
                credit += round(acc[4], 2)
                row += 1
            worksheet.write(row, col + 2, 'الاجمالي', custom_format)
            worksheet.write(row, col + 3, debit, custom_format)
            worksheet.write(row, col + 4, credit, custom_format)
        else:
            worksheet.write(row, 0, 'كود الحساب', table_header_format)
            worksheet.write(row, 1, 'أسم الحساب', table_header_format)
            worksheet.write(row, 2, 'مدين', table_header_format)
            worksheet.write(row, 3, 'داين', table_header_format)
            worksheet.write(row, 4, 'الرصيد', table_header_format)
            row += 1
            col = 0
            debit = 0.0
            credit = 0.0
            balan = 0.0
            for acc in self.get_all_move():
                account = self.env['account.account'].browse(acc[0])
                worksheet.write(row, col, str(account.code), custom_format)
                worksheet.write(row, col + 1, str(account.name), custom_format)
                worksheet.write(row, col + 2, round(acc[1], 2), custom_format)
                debit += round(acc[1], 2)
                worksheet.write(row, col + 3, round(acc[2], 2), custom_format)
                credit += round(acc[2], 2)
                balance = round(acc[1], 2) - round(acc[2], 2)
                worksheet.write(row, col + 4, round(balance, 2), custom_format)
                balan += balance
                row += 1
            worksheet.write(row, col + 1, 'الاجمالي', custom_format)
            worksheet.write(row, col + 2, debit, custom_format)
            worksheet.write(row, col + 3, credit, custom_format)
            worksheet.write(row, col + 4, balan, custom_format)

        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'Bank and Cash',
            'url': '/web/content/bank.cash.report/%s/excel_sheet/Report.xlsx?download=true' % (
                self.id),
            'target': 'self'
        }