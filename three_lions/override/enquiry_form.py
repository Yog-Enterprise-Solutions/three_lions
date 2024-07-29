import frappe
def set_customer_vat(doc,method=None):
    if doc.has_value_changed("custom_vat_no"):
        if doc.custom_vat_no:
            frappe.db.set_value('Customer',doc.party_name, 'tax_id', doc.custom_vat_no)
            frappe.msgprint("VAT(Tax Id) number has been updated in customer.")