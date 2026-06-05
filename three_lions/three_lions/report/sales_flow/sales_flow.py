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
		{"label": "Enquiry Ref. No.", "fieldname": "ref_nos", "fieldtype": "Data", "width": 200},
		{"label": "PO No.", "fieldname": "po_no", "fieldtype": "Link", "options": "Purchase Order", "width": 120},
		{"label": "In Qty", "fieldname": "in_qty", "fieldtype": "Float", "width": 120},
		{"label": "Supplier Name", "fieldname": "supplier_name", "fieldtype": "Data", "width": 170},
		{"label": "PO Date", "fieldname": "po_date", "fieldtype": "Date", "width": 110},
		{"label": "PO Amount", "fieldname": "po_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Adv. Payment Date", "fieldname": "payment_date", "fieldtype": "Date", "width": 130},
		{"label": "Adv. Payment Amount", "fieldname": "payment_amount", "fieldtype": "Currency", "width": 160},
		{"label": "Receipt No.", "fieldname": "receipt_no", "fieldtype": "Link", "options": "Purchase Receipt", "width": 130},
		{"label": "Receipt Date", "fieldname": "receipt_date", "fieldtype": "Date", "width": 100},
		{"label": "Receipt Amount", "fieldname": "receipt_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Purchase Invoice No.", "fieldname": "purchase_invoice_no", "fieldtype": "Data", "width": 190},
		{"label": "Purchase Invoice Date", "fieldname": "purchase_invoice_date", "fieldtype": "Date", "width": 170},
		{"label": "Purchase Invoice Amount", "fieldname": "purchase_invoice_amount", "fieldtype": "Currency", "width": 190},
		{"label": "PI Payment Ref.", "fieldname": "pi_payment_reference", "fieldtype": "Data", "width": 180},
		{"label": "PI Payment Type", "fieldname": "pi_payment_type", "fieldtype": "Data", "width": 150},
		{"label": "PI Payment Date", "fieldname": "pi_payment_date", "fieldtype": "Date", "width": 150},
		{"label": "PI Payment Amount", "fieldname": "pi_payment_amount", "fieldtype": "Currency", "width": 180},
		{"label": "Quotation Ref. No.", "fieldname": "quotation_ref_nos", "fieldtype": "Data", "width": 220},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
		{"label": "Customer PO No.", "fieldname": "customer_po_no", "fieldtype": "Data", "width": 150},
		{"label": "Customer PO Amount", "fieldname": "customer_po_amount", "fieldtype": "Currency", "width": 170},
		{"label": "Customer Delivery No.", "fieldname": "customer_delivery_no", "fieldtype": "Link", "options": "Delivery Note", "width": 170},
		{"label": "Customer Delivery Date", "fieldname": "customer_delivery_date", "fieldtype": "Date", "width": 170},
		{"label": "Customer Delivery Amount", "fieldname": "customer_delivery_amount", "fieldtype": "Currency", "width": 190},
		{"label": "Out Qty", "fieldname": "out_qty", "fieldtype": "Float", "width": 120},
		{"label": "Customer Invoice No.", "fieldname": "customer_invoice_no", "fieldtype": "Link", "options": "Sales Invoice", "width": 170},
		{"label": "Customer Invoice Date", "fieldname": "customer_invoice_date", "fieldtype": "Date", "width": 170},
		{"label": "Customer Invoice Amount", "fieldname": "customer_invoice_amount", "fieldtype": "Currency", "width": 190},
	]


def get_enquiry_ref_doctype():
	if frappe.db.exists("DocType", "Enquiry Ref No"):
		return "Enquiry Ref No"
	return "PO Reference Items"


def get_enquiry_refs(po_name):
	doctype = get_enquiry_ref_doctype()
	return frappe.get_all(
		doctype,
		filters={"parent": po_name, "parenttype": "Purchase Order"},
		pluck="ref_no",
	)


def get_quotation_refs(po_name):
	return frappe.get_all(
		"Quotation Reference Items",
		filters={"parent": po_name, "parenttype": "Purchase Order"},
		pluck="quotation_ref_no",
	)


def get_out_qty(qtn_name):
	if not qtn_name:
		return 0

	result = frappe.db.sql(
		"""
		SELECT SUM(out_src.out_qty) AS out_qty
		FROM (
			SELECT SUM(ABS(sle.actual_qty)) AS out_qty
			FROM `tabStock Ledger Entry` sle
			INNER JOIN `tabDelivery Note` dn
				ON dn.name = sle.voucher_no
				AND dn.docstatus = 1
			WHERE sle.voucher_type = 'Delivery Note'
				AND sle.is_cancelled = 0
				AND sle.actual_qty < 0
				AND dn.custom_qtn_ref_no = %(qtn_name)s

			UNION ALL

			SELECT SUM(ABS(sle.actual_qty)) AS out_qty
			FROM `tabStock Ledger Entry` sle
			INNER JOIN `tabSales Invoice` si
				ON si.name = sle.voucher_no
				AND si.docstatus = 1
			WHERE sle.voucher_type = 'Sales Invoice'
				AND sle.is_cancelled = 0
				AND sle.actual_qty < 0
				AND si.custom_qtn_ref_no = %(qtn_name)s
		) AS out_src
		""",
		{"qtn_name": qtn_name},
	)
	return result[0][0] if result and result[0][0] is not None else 0


def get_sales_flow_for_quotation(qtn_name):
	delivery = frappe.db.sql(
		"""
		SELECT
			MAX(dn.name) AS customer_delivery_no,
			MAX(dn.posting_date) AS customer_delivery_date,
			SUM(COALESCE(dni.amount, 0)) AS customer_delivery_amount
		FROM `tabDelivery Note` dn
		INNER JOIN `tabDelivery Note Item` dni
			ON dni.parent = dn.name
		WHERE dn.docstatus = 1
			AND dn.custom_qtn_ref_no = %(qtn_name)s
		""",
		{"qtn_name": qtn_name},
		as_dict=True,
	)

	invoice = frappe.db.sql(
		"""
		SELECT
			MAX(si.name) AS customer_invoice_no,
			MAX(si.posting_date) AS customer_invoice_date,
			SUM(COALESCE(sii.amount, 0)) AS customer_invoice_amount
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii
			ON sii.parent = si.name
		WHERE si.docstatus = 1
			AND si.custom_qtn_ref_no = %(qtn_name)s
		""",
		{"qtn_name": qtn_name},
		as_dict=True,
	)

	delivery_row = delivery[0] if delivery else {}
	invoice_row = invoice[0] if invoice else {}

	return {
		"customer_delivery_no": delivery_row.get("customer_delivery_no"),
		"customer_delivery_date": delivery_row.get("customer_delivery_date"),
		"customer_delivery_amount": delivery_row.get("customer_delivery_amount"),
		"customer_invoice_no": invoice_row.get("customer_invoice_no"),
		"customer_invoice_date": invoice_row.get("customer_invoice_date"),
		"customer_invoice_amount": invoice_row.get("customer_invoice_amount"),
		"out_qty": get_out_qty(qtn_name),
	}


def apply_quotation_to_row(new_row, quotation, qtn_ref=None):
	if qtn_ref:
		new_row["quotation_ref_nos"] = qtn_ref
	elif quotation:
		new_row["quotation_ref_nos"] = quotation.name

	if not quotation:
		return new_row

	new_row["ref_nos"] = quotation.opportunity or new_row.get("ref_nos") or ""
	new_row["customer_name"] = quotation.customer_name
	new_row["customer_po_no"] = quotation.custom_customer_ref_no
	new_row["customer_po_amount"] = quotation.grand_total

	sales_flow = get_sales_flow_for_quotation(quotation.name)
	new_row.update(sales_flow)
	return new_row


def expand_po_rows(raw_row):
	rows = []
	seen_ref_nos = set()

	for qtn_ref in get_quotation_refs(raw_row.po_no):
		quotation = frappe.db.get_value(
			"Quotation",
			{"docstatus": 1, "name": qtn_ref},
			["name", "customer_name", "custom_customer_ref_no", "grand_total", "opportunity"],
			as_dict=True,
		)

		new_row = raw_row.copy()
		new_row = apply_quotation_to_row(new_row, quotation, qtn_ref=qtn_ref)
		if new_row.get("ref_nos"):
			seen_ref_nos.add(new_row["ref_nos"])
		rows.append(new_row)

	enquiry_refs = get_enquiry_refs(raw_row.po_no)
	if not enquiry_refs and raw_row.get("custom_enquiry_ref_no"):
		enquiry_refs = [raw_row.custom_enquiry_ref_no]

	for ref in enquiry_refs:
		if ref in seen_ref_nos:
			continue

		quotation = frappe.db.get_value(
			"Quotation",
			{"docstatus": 1, "opportunity": ref},
			["name", "customer_name", "custom_customer_ref_no", "grand_total", "opportunity"],
			as_dict=True,
		)

		new_row = raw_row.copy()
		new_row["ref_nos"] = ref
		new_row = apply_quotation_to_row(new_row, quotation)
		rows.append(new_row)
		seen_ref_nos.add(ref)

	if not rows:
		rows.append(raw_row.copy())

	return rows


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

	raw_data = frappe.db.sql(
		f"""
		SELECT
			po.name AS po_no,
			po.custom_enquiry_ref_no,
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
			in_qty_data.in_qty
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
			SELECT in_src.po_name, SUM(in_src.in_qty) AS in_qty
			FROM (
				SELECT pri.purchase_order AS po_name,
					SUM(sle.actual_qty) AS in_qty
				FROM `tabStock Ledger Entry` sle
				INNER JOIN `tabPurchase Receipt Item` pri ON pri.name = sle.voucher_detail_no
				WHERE sle.voucher_type = 'Purchase Receipt'
					AND sle.is_cancelled = 0
					AND IFNULL(pri.purchase_order, '') != ''
				GROUP BY pri.purchase_order

				UNION ALL

				SELECT pii.purchase_order AS po_name,
					SUM(sle.actual_qty) AS in_qty
				FROM `tabStock Ledger Entry` sle
				INNER JOIN `tabPurchase Invoice Item` pii ON pii.name = sle.voucher_detail_no
				INNER JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent AND pi.update_stock = 1
				WHERE sle.voucher_type = 'Purchase Invoice'
					AND sle.is_cancelled = 0
					AND IFNULL(pii.purchase_order, '') != ''
				GROUP BY pii.purchase_order
			) AS in_src
			GROUP BY in_src.po_name
		) AS in_qty_data ON in_qty_data.po_name = po.name
		WHERE {conditions_sql}
		ORDER BY po.transaction_date DESC, po.name DESC
		""",
		query_filters,
		as_dict=True,
	)

	final_data = []
	for row in raw_data:
		final_data.extend(expand_po_rows(row))

	return final_data
