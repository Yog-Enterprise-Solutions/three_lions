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
        
        description = item_name.lower()
        description_new = item_data.get('description')
        description_text = description.replace("we provide", "").strip()
        stock = item_data.get('custom_maintain_stock')

        # Check if an item with the same description already exists
        existing_item = frappe.db.exists('Item', {'item_name': description_text})

        if not existing_item:
            # last_item = frappe.db.get_list('Item',
            #     order_by='creation desc',
            #     page_length=1
            # )
            # last_item_code = f"""{item_data.custom_item_type_code}{int(last_item[0].get('name')[-4:]) + 1}"""
            item = frappe.get_doc({
                "doctype": "Item",
                # "item_code":last_item_code,
                "item_name": description_text,
                "item_group": item_data.get('item_group'),
                "custom_item_type_code": item_data.get('custom_item_type_code'),
                "stock_uom": item_data.get('uom'),
                "description": description_new,
                'is_stock_item': stock,
            })

            try:
                # Insert the document into the database
                item.insert()
                item_data.item_code = item.name  # item.name contains the item code after insertion
                
                
                frappe.msgprint(f"Item '{description_text}' created successfully.")
                
                # Add the created item to the updated items list
                updated_items.append(item.name)

            except Exception as e:
                frappe.log_error(f"Error creating item '{description_text}': {str(e)}")
                frappe.throw(f"Error creating item '{description_text}': {str(e)}")

    return updated_items

    
