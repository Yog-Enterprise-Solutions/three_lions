# Copyright (c) 2026, yog and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "PO NO", "fieldname": "po_no", "fieldtype": "Link", "options": "Purchase Order", "width": 120},
		{"label": "SUPPLIER NAME", "fieldname": "supplier_name", "fieldtype": "Data", "width": 170},
		{"label": "PO DATE", "fieldname": "po_date", "fieldtype": "Date", "width": 110},
		{"label": "AMOUNT", "fieldname": "po_amount", "fieldtype": "Currency", "width": 120},
		{"label": "PAYMENT DATE", "fieldname": "payment_date", "fieldtype": "Date", "width": 120},
		{"label": "PAYMENT AMOUNT", "fieldname": "payment_amount", "fieldtype": "Currency", "width": 140},
		{"label": "RECEIPT NO", "fieldname": "receipt_no", "fieldtype": "Link", "options": "Purchase Receipt", "width": 130},
		{"label": "DATE", "fieldname": "receipt_date", "fieldtype": "Date", "width": 100},
		{"label": "AMOUNT", "fieldname": "receipt_amount", "fieldtype": "Currency", "width": 120},
		{"label": "CUSTOMER PO NO", "fieldname": "customer_po_no", "fieldtype": "Data", "width": 150},
		{"label": "CUSTOMER PO AMOUNT", "fieldname": "customer_po_amount", "fieldtype": "Currency", "width": 170},
		{"label": "CUSTOMER DELIVERY NO", "fieldname": "customer_delivery_no", "fieldtype": "Link", "options": "Delivery Note", "width": 170},
		{"label": "CUSTOMER DELIVERY DATE", "fieldname": "customer_delivery_date", "fieldtype": "Date", "width": 170},
		{"label": "CUSTOMER DELIVERY AMOUNT", "fieldname": "customer_delivery_amount", "fieldtype": "Currency", "width": 190},
		{"label": "CUSTOMER INVOICE NO", "fieldname": "customer_invoice_no", "fieldtype": "Link", "options": "Sales Invoice", "width": 170},
		{"label": "CUSTOMER INVOICE DATE", "fieldname": "customer_invoice_date", "fieldtype": "Date", "width": 170},
		{"label": "CUSTOMER INVOICE AMOUNT", "fieldname": "customer_invoice_amount", "fieldtype": "Currency", "width": 190},
	]


def get_data(filters):
	conditions = ["po.docstatus = 1"]
	query_filters = {}

	if filters.get("company"):
		conditions.append("po.company = %(company)s")
		query_filters["company"] = filters.company

	if filters.get("from_date"):
		conditions.append("po.transaction_date >= %(from_date)s")
		query_filters["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("po.transaction_date <= %(to_date)s")
		query_filters["to_date"] = filters.to_date

	conditions_sql = " AND ".join(conditions)

	return frappe.db.sql(
		f"""
		SELECT
			po.name AS po_no,
			po.supplier_name,
			po.transaction_date AS po_date,
			po.grand_total AS po_amount,
			payment_data.payment_date,
			payment_data.payment_amount,
			receipt_data.receipt_no,
			receipt_data.receipt_date,
			receipt_data.receipt_amount,
			quotation_data.customer_po_no,
			quotation_data.customer_po_amount,
			delivery_data.customer_delivery_no,
			delivery_data.customer_delivery_date,
			delivery_data.customer_delivery_amount,
			invoice_data.customer_invoice_no,
			invoice_data.customer_invoice_date,
			invoice_data.customer_invoice_amount
		FROM `tabPurchase Order` po
		LEFT JOIN (
			SELECT
				pri.purchase_order,
				MAX(pr.name) AS receipt_no,
				MAX(pr.posting_date) AS receipt_date,
				SUM(COALESCE(pri.amount, 0)) AS receipt_amount
			FROM `tabPurchase Receipt Item` pri
			INNER JOIN `tabPurchase Receipt` pr
				ON pr.name = pri.parent
				AND pr.docstatus = 1
			WHERE IFNULL(pri.purchase_order, '') != ''
			GROUP BY pri.purchase_order
		) AS receipt_data
			ON receipt_data.purchase_order = po.name
		LEFT JOIN (
			-- Path 1: PI → Payment Entry (existing payment path)
			SELECT
				pii.purchase_order,
				MAX(pe.posting_date) AS payment_date,
				SUM(COALESCE(per.allocated_amount, 0)) AS payment_amount
			FROM `tabPurchase Invoice Item` pii
			INNER JOIN `tabPurchase Invoice` pi
				ON pi.name = pii.parent
				AND pi.docstatus = 1
			LEFT JOIN `tabPayment Entry Reference` per
				ON per.reference_doctype = 'Purchase Invoice'
				AND per.reference_name = pi.name
			LEFT JOIN `tabPayment Entry` pe
				ON pe.name = per.parent
				AND pe.docstatus = 1
			WHERE IFNULL(pii.purchase_order, '') != ''
			GROUP BY pii.purchase_order

			UNION ALL

			-- Path 2: Direct PE → PO (advance/direct payments to PO)
			SELECT
				per.reference_name AS purchase_order,
				MAX(pe.posting_date) AS payment_date,
				SUM(COALESCE(per.allocated_amount, 0)) AS payment_amount
			FROM `tabPayment Entry Reference` per
			INNER JOIN `tabPayment Entry` pe
				ON pe.name = per.parent
				AND pe.docstatus = 1
			WHERE per.reference_doctype = 'Purchase Order'
			AND IFNULL(per.reference_name, '') != ''
			GROUP BY per.reference_name

			UNION ALL

			-- Path 3: JE → PO (journal entry direct payment to PO)
			SELECT
				jea.reference_name AS purchase_order,
				MAX(je.posting_date) AS payment_date,
				SUM(COALESCE(jea.debit, 0) + COALESCE(jea.credit, 0)) AS payment_amount
			FROM `tabJournal Entry Account` jea
			INNER JOIN `tabJournal Entry` je
				ON je.name = jea.parent
				AND je.docstatus = 1
			WHERE jea.reference_type = 'Purchase Order'
			AND IFNULL(jea.reference_name, '') != ''
			GROUP BY jea.reference_name
		) AS payment_data
			ON payment_data.purchase_order = po.name
		LEFT JOIN (
			SELECT
				qt_link.enquiry_ref_no,
				MAX(qt_link.quotation_name) AS quotation_name,
				MAX(qt_link.customer_po_no) AS customer_po_no,
				MAX(qt_link.customer_po_amount) AS customer_po_amount
			FROM (
				SELECT
					COALESCE(NULLIF(qt.opportunity, ''), NULLIF(qt.enq_det, '')) AS enquiry_ref_no,
					qt.name AS quotation_name,
					qt.custom_customer_ref_no AS customer_po_no,
					qt.grand_total AS customer_po_amount
				FROM `tabQuotation` qt
				WHERE qt.docstatus = 1
					AND COALESCE(NULLIF(qt.opportunity, ''), NULLIF(qt.enq_det, '')) IS NOT NULL
			) AS qt_link
			GROUP BY qt_link.enquiry_ref_no
		) AS quotation_data
			ON quotation_data.enquiry_ref_no = po.custom_enquiry_ref_no
		LEFT JOIN (
			SELECT
				dn.custom_qtn_ref_no AS quotation_name,
				MAX(dn.name) AS customer_delivery_no,
				MAX(dn.posting_date) AS customer_delivery_date,
				SUM(COALESCE(dni.amount, 0)) AS customer_delivery_amount
			FROM `tabDelivery Note` dn
			INNER JOIN `tabDelivery Note Item` dni
				ON dni.parent = dn.name
			WHERE dn.docstatus = 1
				AND IFNULL(dn.custom_qtn_ref_no, '') != ''
			GROUP BY dn.custom_qtn_ref_no
		) AS delivery_data
			ON delivery_data.quotation_name = quotation_data.quotation_name
		LEFT JOIN (
			SELECT
				si.custom_qtn_ref_no AS quotation_name,
				MAX(si.name) AS customer_invoice_no,
				MAX(si.posting_date) AS customer_invoice_date,
				SUM(COALESCE(sii.amount, 0)) AS customer_invoice_amount
			FROM `tabSales Invoice` si
			INNER JOIN `tabSales Invoice Item` sii
				ON sii.parent = si.name
			WHERE si.docstatus = 1
				AND IFNULL(si.custom_qtn_ref_no, '') != ''
			GROUP BY si.custom_qtn_ref_no
		) AS invoice_data
			ON invoice_data.quotation_name = quotation_data.quotation_name
		WHERE {conditions_sql}
		ORDER BY po.transaction_date DESC, po.name DESC
		""",
		query_filters,
		as_dict=True,
	)
