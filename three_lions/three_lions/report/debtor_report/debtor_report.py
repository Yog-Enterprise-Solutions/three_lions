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
	receivable_acc=None
	if frappe.db.exists('Party Account',{'parenttype':'Customer','parent':filters.get("customer")},'account'):
		customer_account=frappe.db.get_value('Party Account',{'parenttype':'Customer','parent':filters.get("customer")},'account')
		receivable_acc=customer_account
	else:
		default_company=frappe.defaults.get_user_default("Company")
		company_doc=frappe.get_doc('Company',default_company)
		default_rece_account=company_doc.default_receivable_account
		receivable_acc=default_rece_account
	filters['receivable_acc'] = receivable_acc
	
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
		# address=get_customer_address(filters)
		# data['address']=address
	
	if filters.get("receivable_acc"):
		where_conditions.append("account = %(receivable_acc)s")

	# Add conditions to query
	filters_query = " AND " + " AND ".join(where_conditions) if where_conditions else ""
	query = query.format(filters=filters_query)

	# Execute query
	data = frappe.db.sql(query, filters, as_dict=True)

	# Organize data by currency
	for gl in data:
		if filters.get("customer"):
			address=get_customer_address(filters)
			gl['address']=address
			contact=get_customer_contact(filters)
			gl['contact']=contact
		currency = gl['transaction_currency']
		if currency not in data_based_on_currency:
			data_based_on_currency[currency] = []
		data_based_on_currency[currency].append(gl)

	# Iterate over each currency in data_based_on_currency
	for currency, entries in data_based_on_currency.items():
		 # Calculate the total balance for the current currency
		total_balance = sum(entry['balance'] for entry in entries)
		
		# Dynamically create the header row for the current currency
		header_row = {
			'transaction_currency': f'Currency({currency})',
			'posting_date': 'INV.DATE',
			'due_date': 'Due.DATE',
			'voucher_no': 'INV.NO',
			'name': 'REF.NO',
			'remarks': 'No Remarks',
			'debit_in_transaction_currency': f'DEBIT({currency})',
			'credit_in_transaction_currency': f'Credit ({currency})',
			'balance': f'BALANCE ({currency})',
			'inv_age': 'INV.AGE'
		}
		total_balance_row = {
		'transaction_currency':None,
		'posting_date': None,
		'due_date': None,
		'voucher_no':None,
		'name': None,
		'remarks': None,
		'debit_in_transaction_currency': None,
		'credit_in_transaction_currency':'Total Balance',
		'balance':total_balance,
		'inv_age': None
	}
		header_row_None = {
		'transaction_currency':None,
		'posting_date': None,
		'due_date': None,
		'voucher_no':None,
		'name': None,
		'remarks': None,
		'debit_in_transaction_currency': None,
		'credit_in_transaction_currency':None,
		'balance':None,
		'inv_age': None
	}


		formatted_data.extend(entries)
	return formatted_data





	
def get_columns(filters):
	columns = [
		{
			"label":  ("Currency"),
			"fieldname": "transaction_currency",
			"fieldtype": "Data",
			"width": 150,
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

