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
	# Header dictionary to insert before each currency's data
	header_row = {
		'transaction_currency': 'Currency',
		'posting_date': 'INV.DATE',
		'due_date': 'Due.DATE',
		'voucher_no': 'INV.NO',
		'name': 'REF.NO',
		'remarks': 'No Remarks',
		'debit_in_transaction_currency': 'DEBIT',
		'credit_in_transaction_currency': 'Credit',
		'balance': 'BALANCE',
		'inv_age': 'INV.AGE'
	}

	# Base query with placeholders for dynamic filtering
	query = """
		SELECT 
			transaction_currency,
			posting_date, due_date, voucher_no, name, remarks,
			debit_in_transaction_currency, credit_in_transaction_currency,
			(debit_in_transaction_currency - credit_in_transaction_currency) AS balance,
			DATEDIFF(CURDATE(), posting_date) AS inv_age
		FROM 
			`tabGL Entry`
		WHERE 
			is_cancelled = 0 AND voucher_type = 'Sales Invoice' AND account = 'Debtors - 3L'
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
	if filters.get("cost_center"):
		where_conditions.append("cost_center = %(cost_center)s")
	if filters.get("customer"):
		where_conditions.append("customer = %(customer)s")

	# Add conditions to query
	filters_query = " AND " + " AND ".join(where_conditions) if where_conditions else ""
	query = query.format(filters=filters_query)

	# Execute query
	data = frappe.db.sql(query, filters, as_dict=True)

	# Organize data by currency
	for gl in data:
		currency = gl['transaction_currency']
		if currency not in data_based_on_currency:
			data_based_on_currency[currency] = []
		data_based_on_currency[currency].append(gl)

	# Iterate over each currency in data_based_on_currency
	for currency, entries in data_based_on_currency.items():
		# Append the header row for the current currency
		formatted_data.append(header_row)

		# Append all entries for the current currency
		formatted_data.extend(entries)
	# frappe.throw(f"{formatted_data}")
	return formatted_data





	
def get_columns(filters):
	columns = [
		{
			"label":  ("Currency"),
			"fieldname": "transaction_currency",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label":  ("INV.DATE"),
			"fieldname": "posting_date",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label":  ("Due.DATE"),
			"fieldname": "due_date",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label":  ("INV.AGE"),
			"fieldname": "inv_age",
			"fieldtype": "Data",
			"width": 100,
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
			"fieldname": "name",
			"fieldtype": "Data",
			# "options":'GL Entry',
			"width": 150,
		},
		{
			"label":  ("Description"),
			"fieldname": "remarks",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label":  ("DEBIT (BHD)"),
			"fieldname": "debit_in_transaction_currency",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label":  ("CREDIT (BHD)"),
			"fieldname": "credit_bhd",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label":  ("BALANCE (BHD)"),
			"fieldname": "balance",
			"fieldtype": "Data",
			"width": 120,
		},
	]

	return columns
