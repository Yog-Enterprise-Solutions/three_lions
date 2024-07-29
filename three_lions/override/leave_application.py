import frappe


def loan_amount(doc,method=None):
    # Execute the SQL query to get the sum of debits grouped by party
    data = frappe.db.sql("""
    Select
        party,
        SUM(debit) AS total_debit,
        SUM(credit) AS total_credit,
        SUM(debit) - SUM(credit) AS total_debit_minus_credit
    FROM 
        `tabGL Entry`
    WHERE  
        party_type = 'Employee'
    GROUP BY 
        party;
    """, as_dict=1)

    # Throw the result data for debugging (optional, can be removed in production)


    # Filter the data to get the record for the specific employee
    filtered_party = None
    for record in data:
        if record['party'] == doc.employee:
            filtered_party = record['total_debit_minus_credit']
            doc.custom_loan_amount = filtered_party
            doc.custom_employee_currently_have_any_loan_from_company = 'Yes'
            break  # Exit the loop once a match is found

    if filtered_party is None:
        # If no match was found, set the loan status accordingly
        doc.custom_employee_currently_have_any_loan_from_company = 'No'

        


    # Assuming 'frappe' module is already imported and properly configured

    # Retrieve all records from the 'tabTraining Event Employee' table
    data_employee = frappe.db.sql("""
        SELECT * FROM `tabTraining Event Employee`
    """, as_dict=1)

    # Iterate over each employee record to find the specific employee
    for emp_record in data_employee:
        if emp_record['employee'] == doc.employee:
            # If the employee is found, update the document field
            doc.custom_whether_the_employee_attended_training_ = "Yes"
            # Optionally, you can break the loop once the employee is found
            break

    # Save the document if it needs to be saved back to the database
    # doc.save()  # Uncomment if you need to save the document

       