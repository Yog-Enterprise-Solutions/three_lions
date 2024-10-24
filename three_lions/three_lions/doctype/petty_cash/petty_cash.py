# Copyright (c) 2024, yog and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PettyCash(Document):
    pass
    
   
     



@frappe.whitelist()
def calculate_opening_balance(account):
    # Fetch GL entries for the given account
    entries = frappe.db.get_list('GL Entry', 
                                 filters={'account': account}, 
                                 fields=['debit', 'credit'],
                                 limit_page_length=0)  # No limit on the number of records

    # Initialize total debit and credit
    total_debit = sum(entry['debit'] for entry in entries if entry['debit'])
    total_credit = sum(entry['credit'] for entry in entries if entry['credit'])

    # Calculate the net amount
    net_amount = total_debit - total_credit
    

    # Assuming this function is part of a form handler, set the 'opening_balance' field
    # Replace 'frm' with your doc or field handler
    

    return net_amount
	


def calculate_opening(doc,method=None):
    # Fetch GL entries for the given account
    entries = frappe.db.get_list('GL Entry', 
                                 filters={'account': doc.account}, 
                                 fields=['debit', 'credit'],
                                 limit_page_length=0)  # No limit on the number of records

    # Initialize total debit and credit
    total_debit = sum(entry['debit'] for entry in entries if entry['debit'])
    total_credit = sum(entry['credit'] for entry in entries if entry['credit'])

    # Calculate the net amount
    net_amount_p = total_debit - total_credit
    doc.opening_balance  = net_amount_p
    

    # Assuming this function is part of a form handler, set the 'opening_balance' field
    # Replace 'frm' with your doc or field handler
    


# def calculate_totals(self):
#     debit_total = 0
#     credit_total = 0

#     # Sum up all debit amounts from the 'deductions' child table
#     if self.deductions:
#         for row in self.deductions:
#             debit_total += row.debit_amount or 0

#     # Sum up all credit amounts from the 'addition' child table
#     if self.addition:
#         for row in self.addition:
#             credit_total += row.credit_amount or 0

#     # Calculate the total and net_total
#     self.total = debit_total - credit_total
#     self.net_total = (self.opening_balance or 0) - debit_total + credit_total

#     # Optionally save the document if you want to persist these changes
#     self.save()

