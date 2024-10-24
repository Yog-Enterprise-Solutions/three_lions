frappe.ui.form.on('Quotation Item', {
    
    custom_vat: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.custom_vat) {
            frappe.call({
                method: 'three_lions.override.quotation.check_or_create_tax_template',
                args: {
                    vat_percentage: row.custom_vat,
                    docname: frm.doc.name,
                    doctype: frm.doc.doctype,
                    row: row
                },
                callback: function(response) {
                    if (response.message) {
                        row.item_tax_template = response.message;
                        frm.refresh_field('items');

                        // Set tax category
                        frm.doc.tax_category = 'Output Vat';

                        // Prepare new tax entry
                        const newEntry = {
                            charge_type: "On Net Total",
                            account_head: "VAT - 3L",
                            description: "VAT",
                            cost_center: "Main - 3L",
                            account_currency: "BHD"
                        };

                        // Check if entry already exists
                        let exists = frm.doc.taxes && frm.doc.taxes.some(tax => 
                            tax.account_head === newEntry.account_head &&
                            tax.charge_type === newEntry.charge_type
                        );

                        // If the entry does not exist, add it
                        if (!exists) {
                            frm.add_child('taxes', newEntry);
                            frm.refresh_field('taxes');
                        }

                        // Save the document
                        frm.save();
                    }
                },
                error: function(error) {
                    // Handle errors here
                    console.error('Error while creating tax template:', error);
                }
            });
        }
    }
});


