frappe.query_reports["Sales Vat Report"] = {
    "filters": [
        // {
        //     fieldname: "company",
        //     label: __("Company"),
        //     fieldtype: "Link",
        //     options: "Company",
        //     reqd: 1,
        //     default: frappe.defaults.get_user_default("Company"),
        // },
        {
            fieldname: "period_type",
            label: __("Period Type"),
            fieldtype: "Select",
            options: ["Monthly", "Quarterly", "Yearly"],
            default: "Monthly",
            reqd: 1,
            on_change: function() {
                let period_type = frappe.query_report.get_filter_value('period_type');
                let today = frappe.datetime.get_today();
                let from_date, to_date;

                if (period_type === "Monthly") {
                    from_date = frappe.datetime.month_start(today);
                    to_date = frappe.datetime.month_end(today);
                } else if (period_type === "Quarterly") {
                    // Subtract 2 months from today's date
                    from_date = frappe.datetime.add_months(today, -2);
                    let year = from_date.split("-")[0];
                    let month = from_date.split("-")[1];

                    // Construct the first day of that month
                    let start_of_month = `${year}-${month}-01`;
                    console.log("ff",start_of_month)
                
                    from_date =start_of_month
                    to_date = frappe.datetime.month_end(today);
                
                    console.log("From Date:", from_date);
                    console.log("To Date:", to_date);
                }
                 else if (period_type === "Yearly") {
                    from_date = frappe.datetime.year_start(today);
                    console.log
                    to_date = frappe.datetime.year_end(today);
                }

                frappe.query_report.set_filter_value('from_date', from_date);
                frappe.query_report.set_filter_value('to_date', to_date);
            }
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start(),
            width: "80",
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end(),
        },
    ]
};
