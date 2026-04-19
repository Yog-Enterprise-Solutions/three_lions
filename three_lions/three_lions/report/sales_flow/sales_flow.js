// Copyright (c) 2026, yog and contributors
// For license information, please see license.txt

const SALES_FLOW_HEADER_SEQUENCE = [
	{ backgroundColor: "#fff200", color: "#000000" },
	{ backgroundColor: "#fff200", color: "#000000" },
	{ backgroundColor: "#fff200", color: "#000000" },
	{ backgroundColor: "#fff200", color: "#000000" },
	{ backgroundColor: "#92d050", color: "#000000" },
	{ backgroundColor: "#92d050", color: "#000000" },
	{ backgroundColor: "#00b0f0", color: "#000000" },
	{ backgroundColor: "#00b0f0", color: "#000000" },
	{ backgroundColor: "#00b0f0", color: "#000000" },
	{ backgroundColor: "#fce4d6", color: "#000000" },
	{ backgroundColor: "#fce4d6", color: "#000000" },
	{ backgroundColor: "#fce4d6", color: "#000000" },
	{ backgroundColor: "#c6e0b4", color: "#000000" },
	{ backgroundColor: "#c6e0b4", color: "#000000" },
	{ backgroundColor: "#c6e0b4", color: "#000000" },
	{ backgroundColor: "#c6e0b4", color: "#000000" },
	{ backgroundColor: "#0070c0", color: "#ffffff" },
	{ backgroundColor: "#0070c0", color: "#ffffff" },
	{ backgroundColor: "#c00000", color: "#ffffff" },
	{ backgroundColor: "#c00000", color: "#ffffff" },
	{ backgroundColor: "#c00000", color: "#ffffff" },
	{ backgroundColor: "#f4b183", color: "#000000" },
	{ backgroundColor: "#f4b183", color: "#000000" },
	{ backgroundColor: "#f4b183", color: "#000000" }
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
				"text-transform": "uppercase",
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
