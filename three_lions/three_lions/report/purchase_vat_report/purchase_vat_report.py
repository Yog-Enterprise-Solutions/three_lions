import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"fieldname": "posting_date", "label": ("Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "name", "label": ("Invoice Number"), "fieldtype": "Data", "width": 150},
		{"fieldname": "supplier", "label": ("Supplier"), "fieldtype": "Data", "width": 150},
		{"fieldname": "supplier_name", "label": ("Supplier Name"), "fieldtype": "Data", "width": 150},
		{"fieldname": "tax_id", "label": ("Tax ID"), "fieldtype": "Data", "width": 150},
		{"fieldname": "remarks", "label": ("Description"), "fieldtype": "Data", "width": 200},
		{"fieldname": "currency", "label": ("Currency"), "fieldtype": "Data", "width": 100},
		{"fieldname": "total", "label": ("Taxable Amount"), "fieldtype": "Float", "width": 200, "precision": 3},
		{"fieldname": "rate", "label": ("Rate"), "fieldtype": "Float", "width": 200, "precision": 3},
		{"fieldname": "total_taxes_and_charges", "label": ("Vat Amount"), "fieldtype": "Float", "width": 200, "precision": 3},
		{"fieldname": "grand_total", "label": ("Total Amount"), "fieldtype": "Float", "width": 200, "precision": 3},
	]
	return columns

def get_data(filters=None):
	data = []
	
	# Prepare the filter for date range
	date_filters = {}
	if filters.get("from_date") and filters.get("to_date"):
		date_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]
	date_filters["is_cancelled"] = 0
	date_filters["transaction_currency"]="BHD"
	date_filters["account"] = filters.get("ledger")
	date_filters["voucher_type"] = "Purchase Invoice"

	gl_entries = frappe.get_all(
		"GL Entry",
		filters=date_filters,
		fields=["posting_date", "voucher_no","against", "account", "debit", "credit","transaction_currency"]
	)

	for entry in gl_entries:
		# Skip entries that do not match the specified ledger account
		if entry.account != filters.get("ledger"):
			continue
		
		purchase_invoice = frappe.db.get_value("Purchase Invoice", entry.voucher_no, ["supplier", "supplier_name", "tax_id","remarks","net_total"], as_dict=True)
		# Calculate the taxable amount and VAT amount

		vat_amount = entry.debit if entry.debit > 0 else 0

		# Append data to the report
		
		# Determine the Tax ID
		tax_id = purchase_invoice.tax_id if purchase_invoice.tax_id else None

		# Append data to the report
		data.append({
			"posting_date": entry.posting_date,
			"name": entry.voucher_no,
			"supplier": purchase_invoice.supplier,
			"supplier_name": purchase_invoice.supplier_name,
			"remarks": purchase_invoice.remarks,
			"currency": entry.transaction_currency,
			"total": purchase_invoice.net_total,
			"rate": 10,  # Rate is not directly available in GL Entry
			"total_taxes_and_charges": vat_amount,
			"grand_total": purchase_invoice.net_total + vat_amount,
			"tax_id": tax_id
		})

	return data
