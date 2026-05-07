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
		{"label": "IN QTY", "fieldname": "in_qty", "fieldtype": "Float", "width": 120},
		{"label": "SUPPLIER NAME", "fieldname": "supplier_name", "fieldtype": "Data", "width": 170},
		{"label": "PO DATE", "fieldname": "po_date", "fieldtype": "Date", "width": 110},
		{"label": "AMOUNT", "fieldname": "po_amount", "fieldtype": "Currency", "width": 120},
		{"label": "ADV PAYMENT DATE", "fieldname": "payment_date", "fieldtype": "Date", "width": 130},
		{"label": "ADV PAYMENT AMOUNT", "fieldname": "payment_amount", "fieldtype": "Currency", "width": 160},
		{"label": "RECEIPT NO", "fieldname": "receipt_no", "fieldtype": "Link", "options": "Purchase Receipt", "width": 130},
		{"label": "DATE", "fieldname": "receipt_date", "fieldtype": "Date", "width": 100},
		{"label": "AMOUNT", "fieldname": "receipt_amount", "fieldtype": "Currency", "width": 120},
		{"label": "PURCHASE INVOICE NO", "fieldname": "purchase_invoice_no", "fieldtype": "Data", "width": 190},
		{"label": "PURCHASE INVOICE DATE", "fieldname": "purchase_invoice_date", "fieldtype": "Date", "width": 170},
		{"label": "PURCHASE INVOICE AMOUNT", "fieldname": "purchase_invoice_amount", "fieldtype": "Currency", "width": 190},
		{"label": "PI PAYMENT REF", "fieldname": "pi_payment_reference", "fieldtype": "Data", "width": 180},
		{"label": "PI PAYMENT TYPE", "fieldname": "pi_payment_type", "fieldtype": "Data", "width": 150},
		{"label": "PI PAYMENT DATE", "fieldname": "pi_payment_date", "fieldtype": "Date", "width": 150},
		{"label": "PI PAYMENT AMOUNT", "fieldname": "pi_payment_amount", "fieldtype": "Currency", "width": 180},
		{"label": "CUSTOMER PO NO", "fieldname": "customer_po_no", "fieldtype": "Data", "width": 150},
		{"label": "CUSTOMER PO AMOUNT", "fieldname": "customer_po_amount", "fieldtype": "Currency", "width": 170},
		{"label": "CUSTOMER DELIVERY NO", "fieldname": "customer_delivery_no", "fieldtype": "Link", "options": "Delivery Note", "width": 170},
		{"label": "CUSTOMER DELIVERY DATE", "fieldname": "customer_delivery_date", "fieldtype": "Date", "width": 170},
		{"label": "CUSTOMER DELIVERY AMOUNT", "fieldname": "customer_delivery_amount", "fieldtype": "Currency", "width": 190},
		{"label": "OUT QTY", "fieldname": "out_qty", "fieldtype": "Float", "width": 120},
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
			po.base_grand_total AS po_amount,
			advance_payment_data.payment_date,
			advance_payment_data.payment_amount,
			receipt_data.receipt_no,
			receipt_data.receipt_date,
			receipt_data.receipt_amount,
			purchase_invoice_data.purchase_invoice_no,
			purchase_invoice_data.purchase_invoice_date,
			purchase_invoice_data.purchase_invoice_amount,
			purchase_invoice_payment_data.pi_payment_reference,
			purchase_invoice_payment_data.pi_payment_type,
			purchase_invoice_payment_data.pi_payment_date,
			purchase_invoice_payment_data.pi_payment_amount,
			quotation_data.customer_po_no,
			quotation_data.customer_po_amount,
			delivery_data.customer_delivery_no,
			delivery_data.customer_delivery_date,
			delivery_data.customer_delivery_amount,
			invoice_data.customer_invoice_no,
			invoice_data.customer_invoice_date,
			invoice_data.customer_invoice_amount,
			in_qty_data.in_qty,
			out_qty_data.out_qty
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
			SELECT
				payment_union.purchase_order,
				MAX(payment_union.payment_date) AS payment_date,
				SUM(payment_union.payment_amount) AS payment_amount
			FROM (
				SELECT
					per.reference_name AS purchase_order,
					pe.posting_date AS payment_date,
					COALESCE(per.allocated_amount, 0) AS payment_amount
				FROM `tabPayment Entry Reference` per
				INNER JOIN `tabPayment Entry` pe
					ON pe.name = per.parent
					AND pe.docstatus = 1
				WHERE per.reference_doctype = 'Purchase Order'
					AND IFNULL(per.reference_name, '') != ''

				UNION ALL

				SELECT
					jea.reference_name AS purchase_order,
					je.posting_date AS payment_date,
					GREATEST(ABS(COALESCE(jea.debit, 0)), ABS(COALESCE(jea.credit, 0))) AS payment_amount
				FROM `tabJournal Entry Account` jea
				INNER JOIN `tabJournal Entry` je
					ON je.name = jea.parent
					AND je.docstatus = 1
				WHERE jea.reference_type = 'Purchase Order'
					AND IFNULL(jea.reference_name, '') != ''
			) AS payment_union
			GROUP BY payment_union.purchase_order
		) AS advance_payment_data
			ON advance_payment_data.purchase_order = po.name
		LEFT JOIN (
			SELECT
				pii.purchase_order,
				GROUP_CONCAT(DISTINCT pi.name ORDER BY pi.posting_date SEPARATOR ', ') AS purchase_invoice_no,
				MAX(pi.posting_date) AS purchase_invoice_date,
				SUM(DISTINCT COALESCE(pi.base_grand_total, 0)) AS purchase_invoice_amount
			FROM `tabPurchase Invoice Item` pii
			INNER JOIN `tabPurchase Invoice` pi
				ON pi.name = pii.parent
				AND pi.docstatus = 1
			WHERE IFNULL(pii.purchase_order, '') != ''
			GROUP BY pii.purchase_order
		) AS purchase_invoice_data
			ON purchase_invoice_data.purchase_order = po.name
		LEFT JOIN (
			SELECT
				payment_against_invoice.purchase_order,
				GROUP_CONCAT(DISTINCT payment_against_invoice.payment_reference ORDER BY payment_against_invoice.payment_reference SEPARATOR ', ') AS pi_payment_reference,
				GROUP_CONCAT(DISTINCT payment_against_invoice.payment_type ORDER BY payment_against_invoice.payment_type SEPARATOR ', ') AS pi_payment_type,
				MAX(payment_against_invoice.payment_date) AS pi_payment_date,
				SUM(payment_against_invoice.payment_amount) AS pi_payment_amount
			FROM (
				SELECT
					pii.purchase_order,
					pe.name AS payment_reference,
					'Payment Entry' AS payment_type,
					pe.posting_date AS payment_date,
					COALESCE(per.allocated_amount, 0) AS payment_amount
				FROM `tabPurchase Invoice Item` pii
				INNER JOIN `tabPurchase Invoice` pi
					ON pi.name = pii.parent
					AND pi.docstatus = 1
				INNER JOIN `tabPayment Entry Reference` per
					ON per.reference_doctype = 'Purchase Invoice'
					AND per.reference_name = pi.name
				INNER JOIN `tabPayment Entry` pe
					ON pe.name = per.parent
					AND pe.docstatus = 1
				WHERE IFNULL(pii.purchase_order, '') != ''

				UNION ALL

				SELECT
					pii.purchase_order,
					je.name AS payment_reference,
					'Journal Entry' AS payment_type,
					je.posting_date AS payment_date,
					GREATEST(ABS(COALESCE(jea.debit, 0)), ABS(COALESCE(jea.credit, 0))) AS payment_amount
				FROM `tabPurchase Invoice Item` pii
				INNER JOIN `tabPurchase Invoice` pi
					ON pi.name = pii.parent
					AND pi.docstatus = 1
				INNER JOIN `tabJournal Entry Account` jea
					ON jea.reference_type = 'Purchase Invoice'
					AND jea.reference_name = pi.name
				INNER JOIN `tabJournal Entry` je
					ON je.name = jea.parent
					AND je.docstatus = 1
				WHERE IFNULL(pii.purchase_order, '') != ''
			) AS payment_against_invoice
			GROUP BY payment_against_invoice.purchase_order
		) AS purchase_invoice_payment_data
			ON purchase_invoice_payment_data.purchase_order = po.name
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
		LEFT JOIN (
			SELECT in_src.po_name, SUM(in_src.in_qty) AS in_qty
			FROM (
				SELECT pri.purchase_order AS po_name,
				       SUM(sle.actual_qty) AS in_qty
				FROM `tabStock Ledger Entry` sle
				JOIN `tabPurchase Receipt Item` pri ON pri.name = sle.voucher_detail_no
				WHERE sle.voucher_type = 'Purchase Receipt'
				  AND sle.is_cancelled = 0
				  AND IFNULL(pri.purchase_order, '') != ''
				GROUP BY pri.purchase_order

				UNION ALL

				SELECT pii.purchase_order AS po_name,
				       SUM(sle.actual_qty) AS in_qty
				FROM `tabStock Ledger Entry` sle
				JOIN `tabPurchase Invoice Item` pii ON pii.name = sle.voucher_detail_no
				JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent AND pi.update_stock = 1
				WHERE sle.voucher_type = 'Purchase Invoice'
				  AND sle.is_cancelled = 0
				  AND IFNULL(pii.purchase_order, '') != ''
				GROUP BY pii.purchase_order
			) AS in_src
			GROUP BY in_src.po_name
		) AS in_qty_data ON in_qty_data.po_name = po.name
		LEFT JOIN (
			SELECT out_src.qtn_ref, SUM(out_src.out_qty) AS out_qty
			FROM (
				SELECT dn.custom_qtn_ref_no AS qtn_ref,
				       SUM(ABS(sle.actual_qty)) AS out_qty
				FROM `tabStock Ledger Entry` sle
				JOIN `tabDelivery Note` dn ON dn.name = sle.voucher_no AND dn.docstatus = 1
				WHERE sle.voucher_type = 'Delivery Note'
				  AND sle.is_cancelled = 0
				  AND sle.actual_qty < 0
				  AND IFNULL(dn.custom_qtn_ref_no, '') != ''
				GROUP BY dn.custom_qtn_ref_no

				UNION ALL

				SELECT si.custom_qtn_ref_no AS qtn_ref,
				       SUM(ABS(sle.actual_qty)) AS out_qty
				FROM `tabStock Ledger Entry` sle
				JOIN `tabSales Invoice` si ON si.name = sle.voucher_no AND si.docstatus = 1
				WHERE sle.voucher_type = 'Sales Invoice'
				  AND sle.is_cancelled = 0
				  AND sle.actual_qty < 0
				  AND IFNULL(si.custom_qtn_ref_no, '') != ''
				GROUP BY si.custom_qtn_ref_no
			) AS out_src
			GROUP BY out_src.qtn_ref
		) AS out_qty_data ON out_qty_data.qtn_ref = quotation_data.quotation_name
		WHERE {conditions_sql}
		ORDER BY po.transaction_date DESC, po.name DESC
		""",
		query_filters,
		as_dict=True,
	)
