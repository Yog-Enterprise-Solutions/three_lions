import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate




@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")
		target.custom_customer_ref_no = ""

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)


	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Purchase Order",
				"validation": {
					"docstatus": ["=", 0],
				},
			},
			"Opportunity Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "Opportunity Item"],
					["parent", "custom_opportunity"],
					["material_request", "material_request"],
					["material_request_item", "material_request_item"],
					["sales_order", "sales_order"],
				],
				"postprocess": update_item,
			},
			"Purchase Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges",
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist