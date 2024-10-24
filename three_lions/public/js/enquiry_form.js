frappe.ui.form.on('Opportunity', {
    refresh(frm) {
        // Set query to filter 'opportunity_from' by linked Customer
        frm.set_query('opportunity_from', () => {
            return {
                filters: {
                    'doctype': 'Customer'  // Ensure this is the correct filter if 'opportunity_from' links to Customer
                }
            };
        });

        // Add a custom button to create and open a new Purchase Order
        frm.add_custom_button(__('Purchase Order'), function() {
            frm.trigger('make_purchase_order');
        }, __('Create'));
    },

    // Define the function to handle Purchase Order creation
    make_purchase_order(frm) {
        frappe.model.open_mapped_doc({
            method: "three_lions.override.purchse_order.make_purchase_order",
            frm: frm
        });
    }
});
