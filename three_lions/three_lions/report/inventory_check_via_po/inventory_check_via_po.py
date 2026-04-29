# Copyright (c) 2026, yog and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	if not filters:
		filters = frappe._dict()
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Purchase Order / Item"),
			"fieldname": "purchase_order",
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("In Qty"),
			"fieldname": "in_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Out Qty"),
			"fieldname": "out_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Balance Qty"),
			"fieldname": "balance_qty",
			"fieldtype": "Float",
			"width": 120,
		},
	]


def get_data(filters):
	po_list = get_po_list(filters)
	if not po_list:
		return []

	in_map = get_in_qty_map(filters, po_list)
	if not in_map:
		return []

	item_list = list({item_code for (_, item_code, _) in in_map})
	out_map = get_out_qty_map(filters, item_list)
	item_name_map = {
		r.name: r.item_name
		for r in frappe.get_all("Item", filters={"name": ["in", item_list]}, fields=["name", "item_name"])
	}

	# Group by PO → items
	po_item_map = {}
	for (po, item_code, warehouse), in_qty in in_map.items():
		po_item_map.setdefault(po, []).append(
			frappe._dict(item_code=item_code, warehouse=warehouse, in_qty=flt(in_qty))
		)

	# Item-level aggregates (out_qty is always the item total, not per-PO)
	item_agg = {}
	for item_code in item_list:
		agg_in = sum(v for (_, ic, _), v in in_map.items() if ic == item_code)
		agg_out = sum(v for (ic, _wh), v in out_map.items() if ic == item_code)
		item_agg[item_code] = frappe._dict(agg_in=agg_in, agg_out=agg_out, balance=agg_in - agg_out)

	hide_zero = filters.get("hide_zero_balance")
	data = []

	for po in po_list:
		items = po_item_map.get(po)
		if not items:
			continue

		# Filter children first so we can skip empty PO parents
		child_rows = []
		for item in items:
			agg = item_agg.get(item.item_code, frappe._dict(agg_out=0, balance=0))
			if hide_zero and agg.balance == 0:
				continue
			child_rows.append(
				frappe._dict(
					purchase_order=item.item_code,
					item_name=item_name_map.get(item.item_code, ""),
					in_qty=item.in_qty,
					out_qty=agg.agg_out,
					balance_qty=agg.balance,
					indent=1,
				)
			)

		if not child_rows:
			continue

		po_in = sum(i.in_qty for i in child_rows)
		data.append(
			frappe._dict(
				purchase_order=po,
				item_name="",
				in_qty=po_in,
				out_qty=None,
				balance_qty=None,
				indent=0,
			)
		)
		data.extend(child_rows)

	return data


def get_po_list(filters):
	conditions = {"docstatus": 1}

	if filters.get("purchase_order"):
		conditions["name"] = filters.purchase_order

	return frappe.get_all("Purchase Order", filters=conditions, pluck="name")


def get_in_qty_map(filters, po_list):
	in_map = {}

	# via Purchase Receipt
	pr_rows = frappe.db.sql(
		"""
		SELECT pri.purchase_order, pri.item_code, pri.warehouse,
		       SUM(sle.actual_qty) as in_qty
		FROM `tabStock Ledger Entry` sle
		JOIN `tabPurchase Receipt Item` pri ON pri.name = sle.voucher_detail_no
		WHERE sle.voucher_type = 'Purchase Receipt'
		  AND sle.is_cancelled = 0
		  AND sle.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND pri.purchase_order IN %(po_list)s
		GROUP BY pri.purchase_order, pri.item_code, pri.warehouse
		""",
		{"from_date": filters.from_date, "to_date": filters.to_date, "po_list": po_list},
		as_dict=1,
	)

	for row in pr_rows:
		key = (row.purchase_order, row.item_code, row.warehouse)
		in_map[key] = in_map.get(key, 0) + flt(row.in_qty)

	# via Purchase Invoice (update_stock = 1)
	pi_rows = frappe.db.sql(
		"""
		SELECT pii.purchase_order, pii.item_code, pii.warehouse,
		       SUM(sle.actual_qty) as in_qty
		FROM `tabStock Ledger Entry` sle
		JOIN `tabPurchase Invoice Item` pii ON pii.name = sle.voucher_detail_no
		JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent
		WHERE sle.voucher_type = 'Purchase Invoice'
		  AND pi.update_stock = 1
		  AND sle.is_cancelled = 0
		  AND sle.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND pii.purchase_order IN %(po_list)s
		GROUP BY pii.purchase_order, pii.item_code, pii.warehouse
		""",
		{"from_date": filters.from_date, "to_date": filters.to_date, "po_list": po_list},
		as_dict=1,
	)

	for row in pi_rows:
		if not row.purchase_order:
			continue
		key = (row.purchase_order, row.item_code, row.warehouse)
		in_map[key] = in_map.get(key, 0) + flt(row.in_qty)

	return in_map


def get_out_qty_map(filters, item_list):
	if not item_list:
		return {}

	out_map = {}

	rows = frappe.db.sql(
		"""
		SELECT sle.item_code, sle.warehouse,
		       SUM(ABS(sle.actual_qty)) as out_qty
		FROM `tabStock Ledger Entry` sle
		WHERE sle.voucher_type IN ('Delivery Note', 'Sales Invoice')
		  AND sle.is_cancelled = 0
		  AND sle.actual_qty < 0
		  AND sle.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND sle.item_code IN %(item_list)s
		GROUP BY sle.item_code, sle.warehouse
		""",
		{"from_date": filters.from_date, "to_date": filters.to_date, "item_list": item_list},
		as_dict=1,
	)

	for row in rows:
		out_map[(row.item_code, row.warehouse)] = flt(row.out_qty)

	return out_map
