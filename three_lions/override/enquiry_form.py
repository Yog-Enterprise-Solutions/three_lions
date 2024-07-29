import frappe
def set_customer_vat(doc,method=None):
    if doc.has_value_changed("custom_vat_no_new"):
        if doc.custom_vat_no_new:
            frappe.db.set_value('Customer',doc.party_name, 'custom_vat_no_', doc.custom_vat_no_new)
            frappe.msgprint("VAT number has been updated in customer.")