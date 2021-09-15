from odoo import api, fields, models


class HrChangeControl(models.TransientModel):
    _name = 'hr.change.control.wizard'
    _description = 'Hr Change Control'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def charge_employee(self):
        if self.employee_ids:
            change_control = self.env['hr.change.control'].browse(self.env.context['active_ids'])
            if change_control:
                for employee in self.employee_ids:
                    contract = self.env['hr.contract'].search(
                        [('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)

                    vals = {
                        'employee_id': employee.id,
                        'contract_id': contract.id,
                        'change_control_id': change_control.id,
                        'previous_salary': None,
                        'new_salary': None,
                        'previous_administrator_id': None,
                        'new_administrator_id': None,
                        'type_change_administrator': None,
                    }

                    if change_control.is_change_administrator:

                        if change_control.type_change_administrator == 'is_eps':
                            vals.update({
                                'previous_administrator_id': contract.eps_id.id,
                                'type_change_administrator': change_control.type_change_administrator, })

                        if change_control.type_change_administrator == 'is_arl':
                            vals.update({
                                'previous_administrator_id': contract.arl_id.id,
                                'type_change_administrator': change_control.type_change_administrator, })
                        if change_control.type_change_administrator == 'is_ccf':
                            vals.update({
                                'previous_administrator_id': contract.ccf_id.id,
                                'type_change_administrator': change_control.type_change_administrator, })
                        if change_control.type_change_administrator == 'pension_found':
                            vals.update({
                                'previous_administrator_id': contract.pension_fund_id.id,
                                'type_change_administrator': change_control.type_change_administrator, })

                        if change_control.type_change_administrator == 'cesantia_fund':
                            vals.update({
                                'previous_administrator_id': contract.cesantia_fund_id.id,
                                'type_change_administrator': change_control.type_change_administrator, })

                        vals.update({
                            'new_administrator_id': change_control.new_administrator_id.id,
                        })
                    else:
                        if change_control.is_change_percentage:
                            new_salary = contract.wage + ((contract.wage * change_control.percentage) / 100)
                        else:
                            new_salary = change_control.new_salary
                        vals.update({
                            'previous_salary': contract.wage,
                            'new_salary': new_salary,
                        })
                    change_control.lines_ids.create(vals)
