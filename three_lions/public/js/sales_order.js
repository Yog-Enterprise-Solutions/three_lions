frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.custom_ref_no) {
            frm.set_df_property("custom_qtn_ref_no", "hidden", 1);
        } else {
            frm.set_df_property("custom_qtn_ref_no", "hidden", 0);
        }
    }
});
