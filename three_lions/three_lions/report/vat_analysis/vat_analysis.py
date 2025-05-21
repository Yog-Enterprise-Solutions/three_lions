# Copyright (c) 2025, yog and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"fieldname": "posting_date", "label": "Date", "fieldtype": "Date", "width": 120},
		{"fieldname": "voucher_no", "label": "Voucher Number", "fieldtype": "Data", "width": 140},
		{"fieldname": "voucher_type", "label": "Voucher Type", "fieldtype": "Data", "width": 120},
		{"fieldname": "user_remark", "label": "Remarks", "fieldtype": "Data", "width": 150},
		{"fieldname": "remarks", "label": "Description", "fieldtype": "Data", "width": 150},
		{"fieldname": "transaction_currency", "label": "Currency", "fieldtype": "Data", "width": 90},
		{"fieldname": "total", "label": "Taxable Amount", "fieldtype": "Float", "width": 150, "precision": 3},
		{"fieldname": "rate", "label": "Rate (%)", "fieldtype": "Float", "width": 90, "precision": 2},
		{"fieldname": "total_taxes_and_charges", "label": "VAT Amount", "fieldtype": "Float", "width": 150, "precision": 3},
	]
	return columns

def get_data(filters=None):
	data = []
	
	# Prepare the filter for date range
	date_filters = {}
	if filters.get("from_date") and filters.get("to_date"):
		date_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]
	date_filters["is_cancelled"] = 0
	# date_filters["transaction_currency"]="BHD"
	if filters.get("ledger"):
		date_filters["account"] = filters.get("ledger")
	date_filters["account"] = ["in", ["10107000 - VAT Receivable - 3L","10201002 - VAT Payable - 3L"]]
	date_filters["voucher_type"] = ["not in", ["Sales Invoice", "Purchase Invoice"]]
	gl_entries = frappe.get_all(
		"GL Entry",
		filters=date_filters,
		fields=["posting_date","voucher_type","transaction_currency", "voucher_no","against", "account", "debit", "credit","remarks"]
	)

	for entry in gl_entries:
		if entry.voucher_type == "Journal Entry":
			user_remarks = frappe.get_value("Journal Entry", entry.voucher_no, "user_remark")

		vat_amount = entry.credit if entry.credit > 0 else entry.debit
		if entry.remarks and entry.remarks.startswith("Note:"):
			entry.remarks = entry.remarks[6:]
			
		# Append data to the report
		data.append({
			"posting_date": entry.posting_date,
			"voucher_type": entry.voucher_type,
			"voucher_no": entry.voucher_no,
			"remarks": entry.remarks,
			"user_remark": user_remarks if user_remarks else "",
			"transaction_currency": entry.transaction_currency,
			"total": (vat_amount/10)*100,  # Assuming VAT is 10%
			"rate": 10,  # Rate is not directly available in GL Entry
			"total_taxes_and_charges": vat_amount,
		})

	return data
