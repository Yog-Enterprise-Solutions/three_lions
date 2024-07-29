frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.custom_ref_no) {
            frm.set_df_property("custom_qtn_ref_no", "hidden", 1);
        } else {
            frm.set_df_property("custom_qtn_ref_no", "hidden", 0);
        }
    }
});





frappe.ui.form.on('Sales Order Item', {
    custom_vat: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.custom_vat) {
            // console.log(row.custom_vat, "uuu");

            frappe.call({
                method: 'three_lions.override.quotation.check_or_create_tax_template',
                args: {
                    vat_percentage: row.custom_vat,
                    docname: frm.doc.name,
                    doctype: frm.doc.doctype,
                    row:row
                },
                callback: function(response) {
                    if (response.message) {
                        row.item_tax_template = response.message;
                        frm.refresh_field('items'); 
                        frm.save()
                         // Assuming 'items' is the field name for the child table
                        // frappe.msgprint(__('Tax Template processed successfully.'));
                    }
                }
            });
        }
    }
});

