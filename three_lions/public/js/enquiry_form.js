frappe.ui.form.on('Opportunity', {
    refresh(frm) {
       
        frm.set_query('opportunity_from', () => {
            return {
                filters: {
                    'name': 'Customer' // Filter by doctype 'Customer'
                }
            };
        });
    }
});
