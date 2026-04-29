// Copyright (c) 2026, yog and contributors
// For license information, please see license.txt

frappe.query_reports["Inventory Check via PO"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "purchase_order",
			"label": __("Purchase Order"),
			"fieldtype": "Link",
			"options": "Purchase Order"
		},
		{
			"fieldname": "hide_zero_balance",
			"label": __("Hide Zero Balance"),
			"fieldtype": "Check",
			"default": 0
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// PO parent rows — bold clickable link
		if (column.fieldname === "purchase_order" && data && data.indent === 0 && value) {
			value = `<b><a href="/app/purchase-order/${data.purchase_order}" style="color: inherit;">${data.purchase_order}</a></b>`;
		}

		// Colour formatting only when a numeric value is present
		if (column.fieldname === "in_qty" && value) {
			value = `<span style="color: green; font-weight: 500;">${value}</span>`;
		}

		if (column.fieldname === "out_qty" && value) {
			value = `<span style="color: red; font-weight: 500;">${value}</span>`;
		}

		if (column.fieldname === "balance_qty" && value) {
			value = `<span style="color: blue; font-weight: 500;">${value}</span>`;
		}

		return value;
	}
};
