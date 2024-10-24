# Copyright (c) 2024, YOG and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data =get_columns(),get_data(filters)
	return columns, data




def get_columns():
	columns = [
		{"fieldname": "name", "label": ("Invoice Number"), "fieldtype": "Data", "width": 150},
		{"fieldname": "customer", "label": ("Customer"), "fieldtype": "Data", "width": 150},
		{"fieldname": "total", "label": ("Amt Before Tax"), "fieldtype": "Data", "width": 200},
		{"fieldname": "rate", "label": ("Rate"), "fieldtype": "Data", "width": 200},
		{"fieldname": "total_taxes_and_charges", "label": ("Tax Amt"), "fieldtype": "Float", "width": 200},
		{"fieldname": "grand_total", "label": ("Total Amt"), "fieldtype": "Data", "width": 200}
	]
	return columns


def get_data(filters=None):
	data = []
	
	# Prepare the filter for date range
	date_filters = {}
	if filters.get("from_date") and filters.get("to_date"):
		date_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]
	
	# Fetch sales invoices based on the given filters (if any)
	sales_invoices = frappe.get_all(
		"Sales Invoice", 
		filters=date_filters,
		fields=["name", "customer", "total", "total_taxes_and_charges", "grand_total","taxes_and_charges"]
	)
	for invoice in sales_invoices:
		if not invoice.taxes_and_charges:
			continue
		temp_rate,temp_account_head=frappe.db.get_value('Sales Taxes and Charges',{'parent':invoice.taxes_and_charges},['rate','account_head'])
		# Fetch the tax details from the child table (Taxes and Charges) for the invoice
		rate,account_head=frappe.db.get_value('Sales Taxes and Charges',{'parent':invoice.name},['rate','account_head'])
		
		
		if temp_account_head != account_head:
			continue  # Skip this invoice if the ledger account doesn't match
	
		# Append data to the report
		data.append({
			"name": invoice.name,
			"customer": invoice.customer,
			"total": invoice.total,
			"rate": rate,
			"total_taxes_and_charges": invoice.total_taxes_and_charges,
			"grand_total": invoice.grand_total
		})
		total_tax_amt=0
		grand_total=0
		total_amt=0
	for dic in data:
		total_tax_amt+=dic.get('total_taxes_and_charges')
		grand_total+=dic.get('grand_total')
		total_amt+=dic.get('total')

	data.append({
		"name": 'Total',
		"customer":None,
		"total":total_amt,
		"rate":None,
		"total_taxes_and_charges": total_tax_amt,
		"grand_total":grand_total
	})

	return data
