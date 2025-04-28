import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"fieldname": "posting_date", "label": ("Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "name", "label": ("Invoice Number"), "fieldtype": "Data", "width": 140},
		{"fieldname": "customer", "label": ("Customer"), "fieldtype": "Data", "width": 120},
		{"fieldname": "customer_name", "label": ("Customer Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "tax_id", "label": ("Tax ID"), "fieldtype": "Data", "width": 180},
		{"fieldname": "remarks", "label": ("Description"), "fieldtype": "Data", "width": 150},
		{"fieldname": "currency", "label": ("Currency"), "fieldtype": "Data", "width": 90},
		{"fieldname": "total", "label": ("Taxable Amount"), "fieldtype": "Float", "width": 150, "precision": 3},
		{"fieldname": "rate", "label": ("Rate"), "fieldtype": "Data", "width": 90},
		{"fieldname": "total_taxes_and_charges", "label": ("Vat Amount"), "fieldtype": "Float", "width": 150, "precision": 3},
		{"fieldname": "grand_total", "label": ("Total Amount"), "fieldtype": "Float", "width": 180, "precision": 3},
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
	date_filters["account"] = filters.get("ledger")
	date_filters["voucher_type"] = "Sales Invoice"

	gl_entries = frappe.get_all(
		"GL Entry",
		filters=date_filters,
		fields=["posting_date", "voucher_no","against", "account", "debit", "credit","transaction_currency"]
	)

	for entry in gl_entries:
		# Skip entries that do not match the specified ledger account
		if entry.account != filters.get("ledger"):
			continue
		
		sales_invoice = frappe.db.get_value("Sales Invoice", entry.voucher_no, ["customer", "customer_name", "tax_id","custom_reference","net_total"], as_dict=True)
		# Calculate the taxable amount and VAT amount

		vat_amount = entry.credit if entry.credit > 0 else 0

		# Append data to the report
		data.append({
			"posting_date": entry.posting_date,
			"name": entry.voucher_no,
			"customer": entry.against,
			"customer_name": sales_invoice.customer_name,
			"tax_id": sales_invoice.tax_id,
			"remarks": sales_invoice.custom_reference,
			"currency": entry.transaction_currency,
			"total": sales_invoice.net_total,
			"rate": 10,  # Rate is not directly available in GL Entry
			"total_taxes_and_charges": vat_amount,
			"grand_total": sales_invoice.net_total + vat_amount,
			"tax_id": sales_invoice.tax_id  # Tax ID is not directly available in GL Entry
		})

	return data
