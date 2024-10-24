import frappe
import requests
from frappe.utils import nowdate

def currency_exc(doc,method=None):
    try:
        # Log the start of the function execution
        frappe.log_error('Starting currency exchange rate update.')

        # Get the list of all currencies
        currencies = frappe.db.get_list('Currency', fields=['name'])
        
        # Get the company currency name
        company_currency_name = "BHD"

        if not company_currency_name:
            return {"status": "error", "message": "Company currency not found."}

        # Iterate over all currencies and perform conversion if needed
        for currency in currencies:
            to_currency = currency['name']

            # Skip if the company currency and to_currency are the same
            if company_currency_name == to_currency:
                continue

            # Construct the API URL
            url = f'https://v6.exchangerate-api.com/v6/3691b761f95a9b4fda4d6da9/latest/{to_currency}'

            response = requests.get(url)

            # Check if the response was successful
            if response.status_code != 200:
                return {"status": "error", "message": f"Failed to fetch exchange rates for {to_currency}. Status code: {response.status_code}"}

            data = response.json()
            
            # Get the conversion rates
            rates = data.get('conversion_rates', {})
            if not rates:
                return {"status": "error", "message": f"No conversion rates found in the API response for {to_currency}."}

            # Check if the company currency is in the conversion rates
            if company_currency_name not in rates:
                return {"status": "error", "message": f"Currency code {company_currency_name} not found in conversion rates for {to_currency}."}

            # Get the conversion rate
            conversion_rate = rates[company_currency_name]
            frappe.log_error(f'{to_currency} to {company_currency_name}: {conversion_rate}')
            frappe.log_error("Done1")

            # Create the Currency Exchange document
            exchange_doc = frappe.get_doc({
                'doctype': 'Currency Exchange',
                'from_currency': to_currency,
                'to_currency': company_currency_name,
                'exchange_rate': conversion_rate,
                'date': nowdate()
            })
            exchange_doc.insert()
            frappe.log_error("Done")

        return {"status": "success", "message": "Currency exchange rates updated successfully."}

    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

