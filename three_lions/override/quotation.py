
import frappe
import json

@frappe.whitelist()
def check_or_create_tax_template(vat_percentage, docname, doctype,row):
    row=json.loads(row)
    item_code=row['item_code']
    tax_category='Output Vat'

    # Fetch the list of Item Tax Templates with the specified VAT percentage
    tax_templates = frappe.get_list('Item Tax Template', 
                                    filters={'title': f"{vat_percentage}%"},
                                    fields=['name'])

    if tax_templates:
        # If a tax template exists, return the template name
        template_name=tax_templates[0].get('name')
        apply_item_tax_template_on_item(item_code,template_name,tax_category)
        return tax_templates[0].get('name')
    else:
        # If no tax template exists, create a new one
        tax_template = frappe.get_doc({
            'doctype': 'Item Tax Template',
            'title': f"{vat_percentage}%",
            'company': '3 Lions',
            'taxes': [
                {
                    'tax_type': 'VAT - 3L',
                    'tax_rate': vat_percentage
                }
            ]
        })

        try:
            # Insert the new tax template into the database
            tax_template.insert()
            template_name=tax_template.name
            apply_item_tax_template_on_item(item_code,template_name,tax_category)
            return tax_template.name
        except Exception as e:
            frappe.throw(f'Failed to create Tax Template. Error: {str(e)}')



def apply_item_tax_template_on_item(item_code, template_name, tax_category):
    # Fetch the item document using the provided item code
    item = frappe.get_doc('Item', item_code)
    for tax in item.taxes:
        if tax.item_tax_template == template_name and tax.tax_category == tax_category:
            # frappe.msgprint(f"Tax template '{template_name}' with category '{tax_category}' already exists for item '{item_code}'")
            return
    
    # Append new tax details if no duplicates found
    item.append('taxes', {
        'item_tax_template': template_name,
        'tax_category': tax_category,
        'valid_from': frappe.utils.getdate()
    })
    
    # Save the updated item document

    item.save()





