frappe.query_reports["Debtor Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"on_change": function() {
				// Get the selected customer
				let customer = frappe.query_report.get_filter_value("customer");

				// If customer is selected, fetch the full name
				if (customer) {
					frappe.db.get_value("Customer", customer, "customer_name", (value) => {
						if (value) {
							// Set the full name in the 'customer_full_name' field
							frappe.query_report.set_filter_value("customer_full_name", value.customer_name);
						}
					});
				} else {
					// Clear the full name if no customer is selected
					frappe.query_report.set_filter_value("customer_full_name", "");
				}
			}
		},
		{
			"fieldname": "customer_full_name",
			"label": __("Customer Full Name"),
			"fieldtype": "Data",
			"read_only": 1
		}
	]
};
