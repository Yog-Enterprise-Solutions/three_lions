frappe.ui.form.on('Leave Application', {
    to_date(frm) { 

        // Get the current value of 'to_date'
        let toDate = frm.doc.to_date;

        // Add one day to 'to_date' and set it as the value of 'custom_date_of_rejoining'
        frm.set_value('custom_date_of_rejoining', frappe.datetime.add_days(toDate, 1));
    },
    onload: function(frm) {
        // Function to hide sections
        function hideSections() {
            cur_frm.set_df_property("sb_other_details", "hidden", 1);
            cur_frm.set_df_property("custom_approval_from_finance_department", "hidden", 1);
            cur_frm.set_df_property("custom_approval_from_hr_department", "hidden", 1);
            cur_frm.set_df_property("custom_tools", "hidden", 1);
        }

        // Check if the form is new
        if (frm.is_new()) {
            // Check if the current user is not the Administrator
            if (frappe.session.user !== 'Administrator') {
                // Hide sections for all users except the Administrator if the form is new
                hideSections();
            }
        }
        // Check if the current user is not the leave approver and not the Administrator
        else if (frappe.session.user !== frm.doc.leave_approver && frappe.session.user !== 'Administrator') {
            // Hide sections if the conditions are met
            hideSections();
        }
    }
});

