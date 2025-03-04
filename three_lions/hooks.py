from . import __version__ as app_version

app_name = "three_lions"
app_title = "Three Lions"
app_publisher = "yog"
app_description = "for trading "
app_email = "yogenterprisesolutions@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/three_lions/css/three_lions.css"
app_include_js = "/public/js/tax_tempale_vat.js"

# include js, css files in header of web template
# web_include_css = "/assets/three_lions/css/three_lions.css"
# web_include_js = "/assets/three_lions/js/three_lions.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "three_lions/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Quotation" : "public/js/quotation.js",
			# "Leave Application" : "public/js/leave_application.js",
			"Opportunity" : "public/js/enquiry_form.js",
			"Sales Order" : "public/js/sales_order.js",
			"Delivery Note" : "public/js/delivery_note.js",
			"Sales Invoice" : "public/js/sales_invoice.js",
			"Material Request" : "public/js/material_request.js",
			"Purchase Order" : "public/js/purchase_order.js"			}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "three_lions.utils.jinja_methods",
#	"filters": "three_lions.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "three_lions.install.before_install"
# after_install = "three_lions.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "three_lions.uninstall.before_uninstall"
# after_uninstall = "three_lions.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "three_lions.utils.before_app_install"
# after_app_install = "three_lions.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "three_lions.utils.before_app_uninstall"
# after_app_uninstall = "three_lions.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "three_lions.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Opportunity": {
		"on_update": "three_lions.override.enquiry_form.set_customer_vat",
		"validate": "three_lions.override.enquiry_form.create_item"
		
	},
	# "Leave Application": {
	# 	"on_update": "three_lions.override.leave_application.loan_amount"
	# },
	"Sales Order": {
		"on_submit": "three_lions.override.sales_order.project_based_on_sales_order"
	},
	
	# "Branch": {
	# 	"on_update": "three_lions.override.branch.monthly_scheduler"
	# },
    "Petty Cash": {
		"validate": "three_lions.three_lions.doctype.petty_cash.petty_cash.calculate_opening"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"three_lions.override.currency_s.currency_exc",
        # "three_lions.override.branch.monthly_scheduler"
	]
	# "daily": [
	# 	"three_lions.override.currency_s.currency_name"
	# ],
	# "hourly": [
	# 	"three_lions.tasks.hourly"
	# ],
	# "weekly": [
	# 	"three_lions.tasks.weekly"
	# ],
	# "monthly": [
	# 	"three_lions.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "three_lions.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# #	"frappe.desk.doctype.event.event.get_events": "three_lions.event.get_events"
#     'erpnext.setup.utils.get_exchange_rate' : 'three_lions.override.currency.convert_currency'
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "three_lions.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["three_lions.utils.before_request"]
# after_request = ["three_lions.utils.after_request"]

# Job Events
# ----------
# before_job = ["three_lions.utils.before_job"]
# after_job = ["three_lions.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"three_lions.auth.validate"
# ]


fixtures = [
     {
        "dt": "Custom Field",
        "filters": [
            [
                "module", "in", ["Three Lions"]
            ]
        ]
    },
     {
        "dt": "Workspace",
        "filters": [
            [
                "module", "in", ["Three Lions"]
            ]
        ]
    }
     
]