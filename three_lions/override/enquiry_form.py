import frappe
import json

def set_customer_vat(doc, method=None):
    if doc.has_value_changed("custom_vat_no"):
        if doc.custom_vat_no:
            frappe.db.set_value('Customer', doc.party_name, 'tax_id', doc.custom_vat_no)
            frappe.msgprint("VAT(Tax Id) number has been updated in customer.")

def create_item(doc, method=None):
    # Extract items data from the document
    items_data = doc.get('items')
    
    if not items_data:
        frappe.throw("No items data provided")

    updated_items = []

    for item_data in items_data:
        # Process the description
        
        item_name = item_data.get('item_name', '')

    if not item_name: 
        frappe.throw("Please add an item name")
    else:
        description = item_name.lower()
        description_new = item_data.get('description')
        description_text = description.replace("we provide", "").strip()
        stock = item_data.get('custom_maintain_stock')
        

        # Check if an item with the same description already exists
        existing_item = frappe.db.exists('Item', {'item_name': description_text})
        
        if not existing_item:
            # Create a new item document
            item = frappe.get_doc({
                "doctype": "Item",
                "item_name": description_text,
                "item_group": 'All Item Groups',
                "stock_uom": item_data.get('uom'),
                "description": description_new,
                'is_stock_item':stock,
            })

            try:
                # Insert the document into the database
                # item_code = frappe.db.get_value("Item",description_text,'item_code')
                
                item.insert()
                item_data.item_code = item.name
               

                 # item.name contains the item code after insert
                # item_code = frappe.db.get_value("Item",description_text,'item_code')
                # frappe.throw(item_code)
                
                frappe.db.commit()
                frappe.msgprint(f"Item '{description_text}' created successfully.")

                # Add the created item to the updated items list
                

            except Exception as e:
                frappe.throw(f"Error creating item {description_text}: {str(e)}")
        

    
