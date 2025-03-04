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

    for row in items_data:
        # Process the description
        item_name = row.get('item_name', '')

        if not item_name: 
            frappe.throw("Please add an item name")
        
        description = row.get('description')
        stock = row.get('custom_maintain_stock')

        # Check if an item with the same description already exists
        existing_item = frappe.db.exists('Item', {'item_name': item_name})

        if not existing_item:

            item = frappe.get_doc({
                "doctype": "Item",
                "item_name": item_name,
                "item_group": row.get('item_group'),
                "custom_item_type_code": row.get('custom_item_type_code'),
                "stock_uom": row.get('uom'),
                "description": description,
                'is_stock_item': stock,
            })

            try:
                # Insert the document into the database
                item.insert()
                row.item_code = item.name  # item.name contains the item code after insertion
                
                
                frappe.msgprint(f"Item '{description}' created successfully.")
                
                # Add the created item to the updated items list
                updated_items.append(item.name)

            except Exception as e:
                frappe.log_error(f"Error creating item '{description}': {str(e)}")
                frappe.throw(f"Error creating item '{description}': {str(e)}")

    return updated_items

    
