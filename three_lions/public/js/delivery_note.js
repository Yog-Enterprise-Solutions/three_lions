


frappe.ui.form.on('Delivery Note Item', {
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
                          // -----add in taxes---------------
                          frm.doc.tax_category='Output Vat'
                          const newEntry = {
                              charge_type: "On Net Total",
                              account_head: "VAT - 3L",
                              description: "VAT",
                              cost_center: "Main - 3L",
                              account_currency: "BHD",
                          };
                          if (frm.doc.taxes){
                          let exists = false;
                          console.log("pppp",frm.doc.currency)
                          frm.doc.taxes.forEach(function(row) {
                              if (row.account_head === newEntry.account_head && row.charge_type === newEntry.charge_type) {
                                  exists = true;
                              }
                          });
                  
                          // If the entry does not exist, add it
                          if (!exists) {
                              const childTable = frm.add_child('taxes', newEntry);
                              frm.refresh_field('taxes');
                          }}
                          else{ const childTable = frm.add_child('taxes', newEntry);
                              frm.refresh_field('taxes');}
                         frm.save()
                    }
                }
            });
        }
    }
});
