
import frappe

def project_based_on_sales_order(doc,method=None):
    qtn_name = frappe.db.get_value('Quotation',doc.customer,'name')
    f = frappe.db.get_value("Quotation",{"party_name": doc.customer},"name")

    # attachments = [frappe.attach_print('Quotation', f, print_format='Quotation Format')]

    s_o = doc.name
    customer = doc.customer
    o_t = doc.order_type
    estimated_costing = doc.estimated_costing
    total_taxes_and_charges = doc.total_taxes_and_charges
    custom_approved_amount = doc.rounded_total
    f = frappe.db.get_value("Quotation",{"party_name": doc.customer},"name")
    # attachments=[
    #         frappe.attach_print(
    #             'Project',
    #             doc.name,
    #             file_name = f,
    #             print_format = Quotation,
    #         )
    #     ]
    project = frappe.new_doc('Project')
    project.project_name = s_o
    project.custom_enquiry_type_link = doc.custom_enquiry_type_link
    project.customer = customer  # Use project instead of Project
    project.sales_order = s_o
    project.order_type= o_t
    project.total_sales_amount = total_taxes_and_charges
    project.estimated_costing =  estimated_costing
    project.custom_ref_no = doc.custom_ref_no
    project.custom_approved_amount = custom_approved_amount
    project.custom_ref_no = doc.custom_ref_no
    project.custom__qtn_ref_no= doc.custom_qtn_ref_no
    # project.custom_quotation = attachments

    # project.custom_attachments = attachments
    project.insert()
