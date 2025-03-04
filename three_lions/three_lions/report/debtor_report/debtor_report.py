# Copyright (c) 2024, yog and contributors
# For license information, please see license.txt

import frappe

from datetime import datetime

def execute(filters=None):
	columns, data =get_columns(filters),get_data(filters)
	return columns, data

def get_data(filters):
	# Initialize dictionary to store data based on currency
	data_based_on_currency = {}
	# Initialize the final list to store formatted data
	formatted_data = []
	receivable_acc = None
	if frappe.db.exists('Party Account', {'parenttype': 'Customer', 'parent': filters.get("customer")}, 'account'):
		customer_account = frappe.db.get_value('Party Account', {'parenttype': 'Customer', 'parent': filters.get("customer")}, 'account')
		receivable_acc = customer_account
	else:
		default_company = frappe.defaults.get_user_default("Company")
		company_doc = frappe.get_doc('Company', default_company)
		default_rece_account = company_doc.default_receivable_account
		receivable_acc = default_rece_account
	filters['receivable_acc'] = receivable_acc
	
	# Base query with placeholders for dynamic filtering
	query = """
		SELECT 
			transaction_currency,
			posting_date, due_date, voucher_no, name, remarks,against_voucher_type,against_voucher,voucher_type,
			debit_in_transaction_currency, credit_in_transaction_currency,

			DATEDIFF(CURDATE(), posting_date) AS inv_age
		FROM 
			`tabGL Entry`
		WHERE 
			is_cancelled = 0
			{filters}  -- Dynamic filters will be added here
		ORDER BY 
			posting_date
	"""

	# Build dynamic filters
	where_conditions = []
	if filters.get("from_date"):
		where_conditions.append("posting_date >= %(from_date)s")
	if filters.get("to_date"):
		where_conditions.append("posting_date <= %(to_date)s")
	if filters.get("customer"):
		where_conditions.append("party = %(customer)s")
	
	if filters.get("receivable_acc"):
		where_conditions.append("account = %(receivable_acc)s")

	# Add conditions to query
	filters_query = " AND " + " AND ".join(where_conditions) if where_conditions else ""
	query = query.format(filters=filters_query)

	# Execute query
	data = frappe.db.sql(query, filters, as_dict=True)

	other_voucher = [row for row in data if row["voucher_type"] != "Sales Invoice"]
	sales_invoices = [row for row in data if row["voucher_type"] == "Sales Invoice"]
	for gl in sales_invoices:
		if filters.get("customer"):
			address = get_customer_address(filters)
			gl['address'] = address
			contact = get_customer_contact(filters)
			gl['contact'] = contact

		gl['remarks_s'] = gl["remarks"]
		# Format posting_date and due_date
		gl['posting_date'] = datetime.strftime(gl['posting_date'], "%d-%m-%Y") if gl['posting_date'] else None
		gl['due_date'] = datetime.strftime(gl['due_date'], "%d-%m-%Y") if gl['due_date'] else None

		if gl["voucher_type"] == "Sales Invoice":
			for payment in other_voucher:
				if payment["against_voucher"] == gl["voucher_no"]:
					gl['credit_in_transaction_currency'] = float(gl['credit_in_transaction_currency']) + float(payment['credit_in_transaction_currency'])
					remove_index = other_voucher.index(payment)
					other_voucher.pop(remove_index)

			sales_invoice_doc = frappe.db.get_value("Sales Invoice", {"name": gl["voucher_no"]},["po_no","remarks"], as_dict=1)
			gl['remarks_s'] = sales_invoice_doc["remarks"]
			gl['sales_doc'] = sales_invoice_doc["po_no"]
			
		else:
			gl['sales_doc'] = gl["against_voucher"]

		# Calculate balance
		gl['balance'] = "{:,.3f}".format(gl['debit_in_transaction_currency'] - gl['credit_in_transaction_currency'])
		
		gl['debit_in_transaction_currency'] = "{:,.3f}".format(gl['debit_in_transaction_currency']) if gl['debit_in_transaction_currency'] else "0.000"
		gl['credit_in_transaction_currency'] = "{:,.3f}".format(gl['credit_in_transaction_currency']) if gl['credit_in_transaction_currency'] else "0.000"
		
		currency = gl['transaction_currency']
		if currency not in data_based_on_currency:
			data_based_on_currency[currency] = []
		if gl['balance'] != "0.000":
			data_based_on_currency[currency].append(gl)

	# Iterate over each currency in data_based_on_currency
	for currency, entries in data_based_on_currency.items():
		# Calculate the total debit, credit, and balance for the current currency
		total_debit = sum(float(entry['debit_in_transaction_currency'].replace(',', '')) for entry in entries)
		total_credit = sum(float(entry['credit_in_transaction_currency'].replace(',', '')) for entry in entries)
		total_balance = sum(float(entry['balance'].replace(',', '')) for entry in entries)  # Remove commas before sum
		
		# Dynamically create the header row for the current currency
		header_row = {
			'transaction_currency': f'Currency({currency})',
			'posting_date': 'INV.DATE',
			'due_date': 'Due.DATE',
			'voucher_no': 'INV.NO',
			'sales_doc': 'REF.NO',
			'remarks_s': 'No Remarks 1',
			'debit_in_transaction_currency': f'DEBIT({currency})',
			'credit_in_transaction_currency': f'Credit ({currency})',
			'balance': f'BALANCE ({currency})',
			'inv_age': 'INV.AGE'
		}
		total_row = {
			'transaction_currency': None,
			'posting_date': None,
			'due_date': None,
			'voucher_no': None,
			'sales_doc': None,
			'remarks_s': 'Total',
			'debit_in_transaction_currency': "{:,.3f}".format(total_debit),
			'credit_in_transaction_currency': "{:,.3f}".format(total_credit),
			'balance': "{:,.3f}".format(total_balance),
			'inv_age': None
		}

		formatted_data.extend(entries)
		formatted_data.append(total_row)
	return formatted_data
	
def get_columns(filters):
	columns = [
		{
			"label":  ("Currency"),
			"fieldname": "transaction_currency",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label":  ("INV.DATE"),
			"fieldname": "posting_date",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label":  ("Due.DATE"),
			"fieldname": "due_date",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label":  ("INV.AGE"),
			"fieldname": "inv_age",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label":  ("INV.NO"),
			"fieldname": "voucher_no",
			"fieldtype": "Data",
			# "options":'Sales Invoice',
			"width": 150,
		},
		{
			"label":  ("REF.NO"),
			"fieldname": "sales_doc",
			"fieldtype": "Data",
			# "options":'GL Entry',
			"width": 150,
		},
		{
			"label":  ("Description"),
			"fieldname": "remarks_s",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label":  ("DEBIT"),
			"fieldname": "debit_in_transaction_currency",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label":  ("CREDIT"),
			"fieldname": "credit_in_transaction_currency",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label":  ("BALANCE"),
			"fieldname": "balance",
			"fieldtype": "Data",
			"width": 120,
		},
	]

	return columns



def get_customer_address(filters):
	"""Fetch and concatenate all addresses linked to a customer."""
	full_address = ""

	if filters.get("customer"):
		# Fetch linked address(es) using the Dynamic Link table
		linked_addresses = frappe.db.sql("""
			SELECT parent
			FROM `tabDynamic Link`
			WHERE link_doctype = 'Customer'
			  AND link_name = %s
			  AND parenttype = 'Address'
		""", (filters.get("customer")), as_list=True)

		# Check if any linked addresses are found
		if linked_addresses:
			for address in linked_addresses:
				# Get the address document using the linked address ID
				address_doc = frappe.get_doc('Address', address[0])
				# Concatenate address fields into one string
				address_parts = [
					address_doc.address_line1,
					address_doc.address_line2,
					address_doc.city,
					address_doc.state,
					address_doc.country
				]
				# Filter out any empty address fields
				full_address += ", ".join(filter(None, address_parts)) + "\n"
	
	return full_address.strip()  # Strip any extra newlines at the end


def get_customer_contact(filters):
	linked_contact = None

	if filters.get("customer"):
		primary_contact = frappe.db.get_value('Customer', filters.get("customer"), 'customer_primary_contact')

		# Fetch linked contact phone(s) using the Dynamic Link table
		linked_contact = frappe.db.sql("""
			SELECT phone
			FROM `tabContact Phone`
			WHERE parent = %s
			  AND parenttype = 'Contact'
		""", (primary_contact,), as_list=True)

	return linked_contact

