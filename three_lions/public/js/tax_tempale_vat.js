$(document).on("form-refresh", function (event, frm) {
    if (['Sales Invoice'].includes(frm.doctype)) {
        frappe.ui.form.on(frm.doctype, {
            // Uncomment if you need to add validation logic
            // validate: function (frm) {
            //     check_total(frm);
            // }
        });

        frappe.ui.form.on('Sales Invoice Item', {
            custom_vat: function (frm, cdt, cdn) {
                console.log('hello'); // Fixed typo from 'cosole' to 'console'
                handleVATAndTax(frm, cdt, cdn);
            }
        });
    }
});

function handleVATAndTax(frm, cdt, cdn) {
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
            callback: function (response) {
                if (response.message) {
                    row.item_tax_template = response.message;
                    frm.refresh_field('items');

                    // Add tax entry
                    frm.doc.tax_category = 'Output Vat';
                    const newEntry = {
                        charge_type: "On Net Total",
                        account_head: "VAT - 3L",
                        description: "VAT",
                        cost_center: "Main - 3L",
                        account_currency: "BHD"
                    };

                    if (frm.doc.taxes) {
                        let exists = false;
                        console.log("Currency:", frm.doc.currency);
                        frm.doc.taxes.forEach(function (row) {
                            if (row.account_head === newEntry.account_head && row.charge_type === newEntry.charge_type) {
                                exists = true;
                            }
                        });

                        // If the entry does not exist, add it
                        if (!exists) {
                            frm.add_child('taxes', newEntry);
                            frm.refresh_field('taxes');
                        }
                    } else {
                        frm.add_child('taxes', newEntry);
                        frm.refresh_field('taxes');
                    }

                    frm.save();
                }
            }
        });
    }
}



    
    