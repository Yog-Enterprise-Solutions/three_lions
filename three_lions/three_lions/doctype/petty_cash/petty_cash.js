// Copyright (c) 2024, yog and contributors
// For license information, please see license.txt

frappe.ui.form.on('Petty Cash', {
    // account: function(frm) {
    //     console.log('Account selected');
        
    //     const accountName = frm.doc.account; // Get the selected account name

    //     // Fetch GL Entry records related to the selected account
    //     frappe.db.get_list('GL Entry', {
    //         filters: {
    //             account: accountName
    //         },
    //         fields: ['debit', 'credit'],
    //         limit_page_length: 0  // No limit on number of records fetched
    //     }).then(entries => {
    //         let total_debit = 0;
    //         let total_credit = 0;

    //         // Sum up the debit and credit amounts
    //         entries.forEach(entry => {
    //             total_debit += entry.debit || 0;
    //             total_credit += entry.credit || 0;
    //         });

    //         const net_amount = total_debit - total_credit;
    //         console.log('Net amount:', net_amount);

    //         // Update the form fields with the calculated values
    //         frm.set_value('opening_balance', net_amount);
    //     }).catch(err => {
    //         console.error("Error fetching GL Entries:", err);
    //     });
    // },
    // validate: function(frm) {
    //     console.log('Form validation');
        
    //     const accountName = frm.doc.account; // Get the selected account name

    //     // Fetch GL Entry records related to the selected account
    //     frappe.db.get_list('GL Entry', {
    //         filters: {
    //             account: accountName
    //         },
    //         fields: ['debit', 'credit'],
    //         limit_page_length: 0  // No limit on number of records fetched
    //     }).then(entries => {
    //         let total_debit = 0;
    //         let total_credit = 0;

    //         // Sum up the debit and credit amounts
    //         entries.forEach(entry => {
    //             total_debit += entry.debit || 0;
    //             total_credit += entry.credit || 0;
    //         });

    //         const net_amount = total_debit - total_credit;
    //         console.log('Net amount:', net_amount);

    //         // Update the form fields with the calculated values
    //         frm.set_value('opening_balance', net_amount);
    //     }).catch(err => {
    //         console.error("Error fetching GL Entries:", err);
    //     });
    // },
    // validate: function(frm) {
    //     console.log('Account selected');

    //     // Ensure that the account field has a value before calling the server-side method
    //     if (frm.doc.account) {
    //         frappe.call({
    //             method: "three_lions.three_lions.doctype.petty_cash.petty_cash.calculate_opening_balance",
    //             args: {
    //                 account: frm.doc.account
    //             },
    //             callback: function(r) {
    //                 if (r.message) {
    //                     // Perform any necessary action with the returned message
    //                     console.log('Opening balance:', r.message);
    //                     // Assuming you're updating a field with the balance:
    //                     frm.set_value('opening_balance', r.message);
    //                 }
    //             }
    //         });
      
    //     }
    // },
    account: function(frm) {
        console.log('hello')
        console.log('Account selected');

        // Ensure that the account field has a value before calling the server-side method
        if (frm.doc.account) {
            frappe.call({
                method: "three_lions.three_lions.doctype.petty_cash.petty_cash.calculate_opening_balance",
                args: {
                    account: frm.doc.account
                },
                callback: function(r) {
                    if (r.message) {
                        // Perform any necessary action with the returned message
                        console.log('Opening balance:', r.message);
                        // Assuming you're updating a field with the balance:
                        frm.set_value('opening_balance', r.message);
                    }
                }
            });
        }
    },
    refresh: function(frm) {
       
            console.log("ppp");
            frm.set_query('account', () => {
                return {
                    filters: {
                        'parent_account': 'Current Assets - 3L' // Adjust the field name and value as necessary
                    }
                };
            });
        
        console.log('hello')
        console.log('Account selected');

        // Ensure that the account field has a value before calling the server-side method
        if (frm.doc.account) {
            frappe.call({
                method: "three_lions.three_lions.doctype.petty_cash.petty_cash.calculate_opening_balance",
                args: {
                    account: frm.doc.account
                },
                callback: function(r) {
                    if (r.message) {
                        // Perform any necessary action with the returned message
                        console.log('Opening balance:', r.message);
                        // Assuming you're updating a field with the balance:
                        frm.set_value('opening_balance', r.message);
                        frm.save()
                        
                    }
                }
            });
        }
    }
    
    
   
   
    
    
});



frappe.ui.form.on('Deductions', {
    debit_amount(frm) {
        console.log('TEST')
        calculate_totals(frm);
    },
    vat(frm) {
        console.log('vt')
        calculate_totals(frm);
    },
    opening_balance(frm) {
        calculate_totals(frm);
    },
    vat(frm) {
        console.log('Function debit_amount triggered');
        
        if (frm.doc.deductions && frm.doc.deductions.length > 0) {
            frm.doc.deductions.forEach(function(row) {
                console.log('VAT:', row.vat);
                console.log('Debit Amount:', row.debit_amount);
        
                // Assuming VAT percentage is being calculated as a percentage of 'vat'
                // let vatPercentage = 5;  // Assuming 5% VAT or any desired percentage
                let calculatedAmount = (row.vat * row.debit_amount) /100
        
                console.log('Calculated Amount:', calculatedAmount);
        
                // Example of setting the calculated amount back into a field
                
        
                // Optionally adjust the debit_amount field based on the calculation
                row.net_debit_amount = calculatedAmount + row.debit_amount; // Update if required
                
            });
        
            // Refresh the child table after updating the fields
            // frm.refresh_field('deductions');
        }
        
    },
    debit_amount(frm) {
        console.log('Function debit_amount triggered');
        
        if (frm.doc.deductions && frm.doc.deductions.length > 0) {
            frm.doc.deductions.forEach(function(row) {
                console.log('VAT:', row.vat);
                console.log('Debit Amount:', row.debit_amount);
        
                // Assuming VAT percentage is being calculated as a percentage of 'vat'
                // let vatPercentage = 5;  // Assuming 5% VAT or any desired percentage
                let calculatedAmount = (row.vat * row.debit_amount) /100
        
                console.log('Calculated Amount:', calculatedAmount);
        
                // Example of setting the calculated amount back into a field
                
        
                // Optionally adjust the debit_amount field based on the calculation
                // row.debit_amount = calculatedAmount; // Update if required
                row.net_debit_amount = calculatedAmount + row.debit_amount;
               
            });
        
            // Refresh the child table after updating the fields
            // frm.refresh_field('deductions');
        }
    }
    
    
    
});

frappe.ui.form.on('Addition', {
    credit_amount(frm) {
        calculate_totals(frm);
    },
    vat(frm) {
        calculate_totals(frm);
    },
    opening_balance(frm) {
        calculate_totals(frm);
    },
    vat(frm) {
        console.log('Function debit_amount triggered');
        
        if (frm.doc.addition && frm.doc.addition.length > 0) {
            frm.doc.addition.forEach(function(row) {
                console.log('VAT:', row.vat);
                console.log('Amount:', row.net_credit_amount);
        
                // Assuming VAT percentage is being calculated as a percentage of 'vat'
                // let vatPercentage = 5;  // Assuming 5% VAT or any desired percentage
                let calculatedAmount = (row.vat * row.credit_amount) /100
        
                console.log('Calculated Amount:', calculatedAmount);
        
                // Example of setting the calculated amount back into a field
                
        
                // Optionally adjust the debit_amount field based on the calculation
                row.net_credit_amount = calculatedAmount + row.credit_amount; // Update if required
                // frm.save()
            });
        
            // Refresh the child table after updating the fields
            // frm.refresh_field('addition');
        }
        
    },
    credit_amount(frm) {
        console.log('Function debit_amount triggered');
        
        if (frm.doc.addition && frm.doc.addition.length > 0) {
            frm.doc.addition.forEach(function(row) {
                console.log('VAT:', row.vat);
                console.log('Debit Amount:', row.credit_amount);
        
                // Assuming VAT percentage is being calculated as a percentage of 'vat'
                // let vatPercentage = 5;  // Assuming 5% VAT or any desired percentage
                let calculatedAmount = (row.vat * row.credit_amount) /100
        
                console.log('Calculated Amount:', calculatedAmount);
        
                // Example of setting the calculated amount back into a field
                
        
                // Optionally adjust the debit_amount field based on the calculation
                // row.debit_amount = calculatedAmount; // Update if required
                row.net_credit_amount = calculatedAmount + row.credit_amount;
                // frm.save()
            });
        
            // Refresh the child table after updating the fields
            // frm.refresh_field('addition');
        }
    }
    

});

// Function to calculate total and net total
function calculate_totals(frm) {
    let debit_total = 0;
    let credit_total = 0;

    // Sum up all debit amounts from the 'deductions' table
    if (frm.doc.deductions && frm.doc.deductions.length > 0) {
        frm.doc.deductions.forEach(function(row) {
            console.log("GGG",row.net_debit_amount)
            debit_total += row.net_debit_amount || 0;
        });
    }

    // Sum up all credit amounts from the 'addition' table
    if (frm.doc.addition && frm.doc.addition.length > 0) {
        frm.doc.addition.forEach(function(row) {
            credit_total += row.credit_amount || 0;
        });
    }

    // Calculate the total and net_total
    let total_amount = debit_total - credit_total;
    frm.set_value('total', total_amount);

    let net_total = (frm.doc.opening_balance || 0) - debit_total + credit_total;
    frm.set_value('net_total', net_total);
    
}


frappe.ui.form.on('Petty Cash', {
    
});


