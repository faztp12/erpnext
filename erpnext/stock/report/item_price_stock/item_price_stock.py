# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_data(filters,columns)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Link",
			"options": "Item",
			"width": 120
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 120
		},
		{
			"label": _("Stock Available"),
			"fieldname": "stock_available",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Buying Price List"),
			"fieldname": "buying_price_list",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 120
		},
		{
			"label": _("Buying Rate"),
			"fieldname": "buying_rate",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Selling Price List"),
			"fieldname": "selling_price_list",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 120
		},
		{
			"label": _("Selling Rate"),
			"fieldname": "selling_rate",
			"fieldtype": "Currency",
			"width": 120
		}
	]

def get_data(filters, columns):
	item_price_qty_data = []
	item_price_qty_data = get_item_price_qty_data(filters)
	return item_price_qty_data

def get_item_price_qty_data(filters):
	item_dicts = []
	conditions = ""
	if filters.get("item_code"):
		conditions += "where a.item_code=%(item_code)s"

	item_results = frappe.db.sql("""select a.item_code as item_name, a.name as price_list_name,
		b.warehouse as warehouse, b.actual_qty as actual_qty
		from `tabItem Price` a left join `tabBin` b
		ON a.item_code = b.item_code
		{conditions}"""
		.format(conditions=conditions), filters, as_dict=1)

	price_list_names = ",".join(['"' + frappe.db.escape(item['price_list_name']) + '"'
		for item in item_results])

	buying_price_map = get_buying_price_map(price_list_names)
	selling_price_map = get_selling_price_map(price_list_names)

	result = []
	if item_results:
		for item_dict in item_results:
			data = {
				'item_name': item_dict.item_name,
				'warehouse': item_dict.warehouse,
				'stock_available': item_dict.actual_qty or 0,
				'buying_price_list': "",
				'buying_rate': 0.0,
				'selling_price_list': "",
				'selling_rate': 0.0
			}

			price_list = item_dict["price_list_name"]
			if buying_price_map.get(price_list):
				data["buying_price_list"] = buying_price_map.get(price_list)["Buying Price List"] or ""
				data["buying_rate"] = buying_price_map.get(price_list)["Buying Rate"] or 0
			if selling_price_map.get(price_list):
				data["selling_price_list"] = selling_price_map.get(price_list)["Selling Price List"] or ""
				data["selling_rate"] = selling_price_map.get(price_list)["Selling Rate"] or 0

			result.append(data)

	return result

def get_buying_price_map(price_list_names):
	buying_price = frappe.db.sql("""
		select
			name,price_list,price_list_rate
		from
			`tabItem Price`
		where
			name in ({price_list_names}) and buying=1
		""".format(price_list_names=price_list_names), as_dict=1)

	buying_price_map = {}
	for d in buying_price:
		name = d["name"]
		buying_price_map[name] = {
			"Buying Price List" :d["price_list"],
			"Buying Rate" :d["price_list_rate"]
		}
	return buying_price_map

def get_selling_price_map(price_list_names):
	selling_price = frappe.db.sql("""
		select
			name,price_list,price_list_rate
		from
			`tabItem Price`
		where
			name in ({price_list_names}) and selling=1
		""".format(price_list_names=price_list_names), as_dict=1)

	selling_price_map = {}
	for d in selling_price:
		name = d["name"]
		selling_price_map[name] = {
			"Selling Price List" :d["price_list"],
			"Selling Rate" :d["price_list_rate"]
		}
	return selling_price_map