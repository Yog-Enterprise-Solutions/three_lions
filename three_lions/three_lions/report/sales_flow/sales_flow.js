// Copyright (c) 2026, yog and contributors
// For license information, please see license.txt

const SALES_FLOW_HEADER_SEQUENCE = [
	{ backgroundColor: "#fff200", color: "#000000" }, // Enquiry Ref. No.
	{ backgroundColor: "#92d050", color: "#000000" }, // PO No.
	{ backgroundColor: "#92d050", color: "#000000" }, // In Qty
	{ backgroundColor: "#92d050", color: "#000000" }, // Supplier Name
	{ backgroundColor: "#92d050", color: "#000000" }, // PO Date
	{ backgroundColor: "#92d050", color: "#000000" }, // PO Amount
	{ backgroundColor: "#00b0f0", color: "#000000" }, // Adv. Payment Date
	{ backgroundColor: "#00b0f0", color: "#000000" }, // Adv. Payment Amount
	{ backgroundColor: "#00b0f0", color: "#000000" }, // Receipt No.
	{ backgroundColor: "#fce4d6", color: "#000000" }, // Receipt Date
	{ backgroundColor: "#fce4d6", color: "#000000" }, // Receipt Amount
	{ backgroundColor: "#fce4d6", color: "#000000" }, // Purchase Invoice No.
	{ backgroundColor: "#c6e0b4", color: "#000000" }, // Purchase Invoice Date
	{ backgroundColor: "#c6e0b4", color: "#000000" }, // Purchase Invoice Amount
	{ backgroundColor: "#c6e0b4", color: "#000000" }, // PI Payment Ref.
	{ backgroundColor: "#c6e0b4", color: "#000000" }, // PI Payment Type
	{ backgroundColor: "#c6e0b4", color: "#000000" }, // PI Payment Date
	{ backgroundColor: "#c6e0b4", color: "#000000" }, // PI Payment Amount
	{ backgroundColor: "#0070c0", color: "#ffffff" }, // Quotation Ref. No.
	{ backgroundColor: "#0070c0", color: "#ffffff" }, // Customer Name
	{ backgroundColor: "#c00000", color: "#ffffff" }, // Customer PO No.
	{ backgroundColor: "#c00000", color: "#ffffff" }, // Customer PO Amount
	{ backgroundColor: "#f4b183", color: "#000000" }, // Customer Delivery No.
	{ backgroundColor: "#f4b183", color: "#000000" }, // Customer Delivery Date
	{ backgroundColor: "#f4b183", color: "#000000" }, // Customer Delivery Amount
	{ backgroundColor: "#d9b3ff", color: "#000000" }, // Out Qty
	{ backgroundColor: "#d9b3ff", color: "#000000" }, // Customer Invoice No.
	{ backgroundColor: "#d9b3ff", color: "#000000" }, // Customer Invoice Date
	{ backgroundColor: "#d9b3ff", color: "#000000" }  // Customer Invoice Amount
];

function applySalesFlowHeaderStyles(datatable) {
	if (!datatable || !datatable.wrapper) {
		return;
	}

	$(datatable.wrapper)
		.find(".dt-header .dt-cell")
		.each(function (index) {
			const style = SALES_FLOW_HEADER_SEQUENCE[index];

			if (!style) {
				return;
			}

			$(this).css({
				"background-color": style.backgroundColor,
				color: style.color,
				"font-weight": "700",
				// "text-transform": "uppercase",
				"border-right": "1px solid #d1d5db"
			});
		});
}

frappe.query_reports["Sales Flow"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("company")
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start()
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end()
		}
	],

	after_datatable_render(datatable) {
		applySalesFlowHeaderStyles(datatable);
	}
};
