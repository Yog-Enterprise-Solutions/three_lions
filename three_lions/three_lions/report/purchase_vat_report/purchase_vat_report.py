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
	date_filters["docstatus"] = 1
	date_filters["is_return"] = 0
	date_filters["currency"]="BHD"
	# Fetch purchase invoices based on the given filters (if any)
	purchase_invoices = frappe.get_all(
		"Purchase Invoice", 
		filters=date_filters,
		fields=["posting_date", "name", "supplier", "supplier_name", "remarks", "total", "tax_id", "total_taxes_and_charges", "grand_total","taxes_and_charges"]
	)
	for invoice in purchase_invoices:
		# if not invoice.taxes_and_charges:
		# 	continue
		# temp_rate, temp_account_head = frappe.db.get_value('Purchase Taxes and Charges', {'parent': invoice.taxes_and_charges}, ['rate', 'account_head'])
		# # Fetch the tax details from the child table (Taxes and Charges) for the invoice
		rate = frappe.db.get_value('Purchase Taxes and Charges', {'parent': invoice.name}, 'rate') or 0
		
		# if temp_account_head != account_head:
		# 	continue  # Skip this invoice if the ledger account doesn't match
		
		# Determine the Tax ID
		tax_id = invoice.tax_id if invoice.tax_id else invoice.custom_vat_no

		# Append data to the report
		data.append({
			"posting_date": invoice.posting_date,
			"name": invoice.name,
			"supplier": invoice.supplier,
			"supplier_name": invoice.supplier_name,
			"remarks": invoice.remarks,
			"total": invoice.total,
			"rate": rate,
			"total_taxes_and_charges": invoice.total_taxes_and_charges,
			"grand_total": invoice.grand_total,
			"tax_id": tax_id
		})
	
	# Calculate totals
	total_tax_amt = sum(item['total_taxes_and_charges'] for item in data)
	grand_total = sum(item['grand_total'] for item in data)
	total_amt = sum(item['total'] for item in data)

	# Append totals to the report
	data.append({
		"posting_date": None,
		"name": 'Total',
		"supplier": None,
		"supplier_name": None,
		"remarks": None,
		"total": total_amt,
		"rate": None,
		"total_taxes_and_charges": total_tax_amt,
		"grand_total": grand_total,
		"tax_id": None
	})

	return data
