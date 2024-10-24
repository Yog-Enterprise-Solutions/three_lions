// frappe.ui.form.on('Request for Quotation', {
//     refresh(frm) {
//         frm.doc.items.forEach(function(item) {
//             // Check if prevdoc_docname exists
//             if (item.prevdoc_docname) {
//                 frappe.throw(item.prevdoc_docname);
                
//                 // Fetch the Opportunity document using prevdoc_docname
//                 frappe.call({
//                     method: 'three_lions.override.quotation.rfq_update',
//                     args: {
//                         name: item.prevdoc_docname
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             // Loop through each returned item info
//                             response.message.forEach(function(item_names) {
//                                 // Find the corresponding row in the items table and update it
//                                 frm.doc.items.forEach(function(row) {
//                                     // You may want to add a condition to match specific rows if needed
//                                     row.item_code = item_names.item_code;
//                                     row.item_name = item_names.item_code; // Adjust if you need a different field
//                                     row.description = item_names.description;
//                                 });
//                             });
//                             frm.refresh_field('items'); // Refresh the field to reflect changes
//                         }
//                     }
//                 });
//             }
//         });
//     }
// });
