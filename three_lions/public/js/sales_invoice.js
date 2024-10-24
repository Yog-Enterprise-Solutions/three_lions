frappe.ui.form.on('Sales Invoice Item', {
    custom_vat: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.custom_vat > 0) {
            // Calculate VAT amounts
            calculate_and_update_vat(frm, row);
            
            // Call server method to check or create tax template
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
                        frm.save()

                        // Add or update tax entry
                        frm.doc.tax_category = 'Output Vat';
                        const newEntry = {
                            charge_type: "On Net Total",
                            account_head: "VAT - 3L",
                            description: "VAT",
                            cost_center: "Main - 3L",
                            account_currency: "BHD",
                        };
                        
                        let exists = false;
                        if (frm.doc.taxes) {
                            frm.doc.taxes.forEach(function(tax_row) {
                                if (tax_row.account_head === newEntry.account_head && tax_row.charge_type === newEntry.charge_type) {
                                    exists = true;
                                }
                            });
                        }
                        
                        // If the entry does not exist, add it
                        if (!exists) {
                            frm.add_child('taxes', newEntry);
                            frm.refresh_field('taxes');
                        }
                    }
                },
                error: function(error) {
                    console.error("Server call failed:", error);
                }
            });
        } else {
            // Set VAT amounts to 0 if custom_vat is 0
            row.custom_vat_on_net_amount = 0;
            row.custom_vat_on_amount = 0;
            row.item_tax_template = null;
            frm.refresh_field('items');
            
            // Remove the related tax entry if present
            remove_tax_entry(frm);
            frm.save()
        }
    },
    rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.qty && row.rate) {
            row.amount = row.qty * row.rate;
            frm.refresh_field('items');
            
            // Recalculate VAT amounts when qty changes
            if (row.custom_vat > 0) {
                calculate_and_update_vat(frm, row);
            }
        }
    },
    qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Update the amount based on qty and rate
        if (row.qty && row.rate) {
            row.amount = row.qty * row.rate;
            row.custom_total_on_price_list = row.qty * row.price_list_rate
            frm.refresh_field('items');
            
            // Recalculate VAT amounts when qty changes
            if (row.custom_vat > 0) {
                calculate_and_update_vat(frm, row);
            }
        }
    },
    price_list_rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Update the amount based on qty and rate
        if (row.price_list_rate ) {
            
            console.log(row.custom_total_on_price_list)
            row.custom_total_on_price_list = row.qty * row.price_list_rate
           
            frm.refresh_field('items');
            
            // Recalculate VAT amounts when qty changes
            if (row.custom_vat > 0) {
                calculate_and_update_vat(frm, row);
            }
        }
    }
    
});

// Helper function to calculate and update VAT fields
function calculate_and_update_vat(frm, row) {
    if (row.custom_vat > 0) {
        let net_amount = (row.net_amount * row.custom_vat) / 100;

        row.custom_vat_on_net_amount =  net_amount + row.net_amount;
        row.custom_total_on_price_list = row.qty * row.price_list_rate
        let vat_net =(row.amount * row.custom_vat) / 100; 

        row.custom_vat_on_amount =  vat_net + row.price_list_rate
    } else {
        row.custom_vat_on_net_amount = 0;
        row.custom_vat_on_amount = 0;
    }
    frm.refresh_field('items');
}

// Helper function to remove the related tax entry
function remove_tax_entry(frm) {
    if (frm.doc.taxes) {
        frm.doc.taxes = frm.doc.taxes.filter(tax_row => {
            return !(tax_row.account_head === "VAT - 3L" && tax_row.charge_type === "On Net Total");
        });
        frm.refresh_field('taxes');
    }
}
