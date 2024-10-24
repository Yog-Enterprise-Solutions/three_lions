import frappe
from frappe.utils import today, getdate,add_months,add_to_date

import time


def monthly_scheduler():
    
    today_date = getdate(today()) 

    # Fetch delivery notes with custom fields set
    delivery_notes = frappe.db.get_list(
        'Delivery Note',
        filters=[
            ['custom_start_date', 'is', 'set'],
            ['custom_end_date', 'is', 'set'],
            ['custom_reference_', 'is', 'set'],
            ['custom_frequency','is','set']
        ],
        fields=['name', 'custom_start_date', 'custom_end_date', 'custom_reference_','custom_frequency']
    )
    
    # Process each delivery note
    for note in delivery_notes:
        try:
            delivery_note = frappe.get_doc('Delivery Note', note.name)
            custom_reference_ = getdate(delivery_note.custom_reference_)  # Convert to date object
            end_date = getdate(delivery_note.custom_end_date)
            start_date = getdate(delivery_note.custom_start_date)
            frequency = delivery_note.custom_frequency
            
            # Log the delivery note details
            frappe.log_error(f'Processing Delivery Note: {delivery_note.name}', "Delivery Note Status")
            
            # Check if today is the reference date
            if today_date == custom_reference_:
                frappe.log_error(f'Delivery Note starts today: {delivery_note.name}', "Delivery Note Status")
                
                if start_date <= end_date:
                    frappe.log_error(f'Delivery Note date range valid: {delivery_note.name}', "Delivery Note Status")
                    
                    # Create a Sales Invoice
                    sales_invoice = frappe.get_doc({
                        "doctype": "Sales Invoice",
                        "customer": delivery_note.customer,  # Access customer from Delivery Note
                        "custom_vat_no": delivery_note.custom_vat_no,  # Custom VAT from the Delivery Note
                        "posting_date": today_date  # Set posting date to today's date
                    })
                    
                    # Append items from the Delivery Note to the Sales Invoice
                    for item in delivery_note.items:
                        sales_invoice.append("items", {
                            "item_code": 'Item-0161',  # Use item code from Delivery Note
                            "qty": item.qty,
                            "rate": item.rate,
                            "custom_vat": item.custom_vat,
                            "serial_no": item.serial_no
                        })
                    
                    sales_invoice.insert()
                    

                    # Update the delivery note's dates to the next month
                    if frequency =='Daily':
                        delivery_note.custom_reference_ = add_to_date(custom_reference_,days=1)
                        frappe.log_error(f'Delivery Note {delivery_note.name} updated for next day', "Delivery Note Status")
                        delivery_note.save()
                    elif frequency =='Weekly':
                        delivery_note.custom_reference_ = add_to_date(custom_reference_, days=7)
                        delivery_note.save()
                    elif frequency =='Monthly':
                        delivery_note.custom_reference_ = add_months(custom_reference_, 1)
                        frappe.log_error(f'Delivery Note {delivery_note.name} updated for next month', "Delivery Note Status")
                        delivery_note.save()
                    elif frequency =='Quarterly':
                        delivery_note.custom_reference_ = add_months(custom_reference_, 3)
                        delivery_note.save()
                    elif frequency =='Half-yearly':
                        delivery_note.custom_reference_ = add_months(custom_reference_, 6)
                        delivery_note.save()
                    elif frequency =='Yearly':
                        delivery_note.custom_reference_ = add_to_date(custom_reference_, 1)
                        delivery_note.save()
                    


                    
                    
                else:
                    frappe.log_error(f"Invalid date range for Delivery Note: {delivery_note.name}", "Delivery Note Status")
        
        except Exception as e:
            frappe.log_error(f'Error processing Delivery Note: {str(e)}', "Error Log")


    

        

        

