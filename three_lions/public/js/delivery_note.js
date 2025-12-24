frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        console.log('hello')
        if (frm.doc.custom_ref_no) {
            frm.set_df_property("custom_qtn_ref_no", "hidden", 1);
        } else {
            frm.set_df_property("custom_qtn_ref_no", "hidden", 0);
        }
    },
     validate: function (frm) {
        for (let row of frm.doc.items){
            row.custom_vat_on_amount = row.custom_vat * row.net_amount / 100;
        }
    //    if(frm.doc.currency=='BHD'){

            handleVATAndTax(frm)
        // }
    }
});

frappe.ui.form.on('Delivery Note Item', {
    custom_vat: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.custom_vat_on_amount = row.custom_vat * row.net_amount / 100;
        frm.refresh_field('items');
        // if(frm.doc.currency=='BHD'){

            handleVATAndTax(frm, cdt, cdn)
        // }
    }
});

function handleVATAndTax(frm) {
    let total_tax = 0;
    let actual_rate = 0;
    frm.doc.items.forEach(item => {
        if (item.custom_vat_on_amount) {
            total_tax += item.custom_vat_on_amount;
        }
    });

    // Prepare new tax entry
    const newEntry = {
        charge_type: "Actual",
        account_head: "10201002 - VAT Payable - 3L",
        description: "VAT",
        cost_center: "Main - 3L",
        account_currency: "BHD",
        rate: actual_rate,
        tax_amount: total_tax,
    };
    // Check if entry already exists, else add it
    let exists = false;
    if (frm.doc.taxes && frm.doc.taxes.length) {
        for (let tax of frm.doc.taxes) {
            if (tax.account_head === newEntry.account_head && tax.charge_type === newEntry.charge_type) {
                tax.tax_amount = newEntry.tax_amount;
                exists = true;
                break;
            }
        }
    }
    if (!exists) {
        frm.add_child('taxes', newEntry);
    }
    frm.refresh_field('taxes');
}
