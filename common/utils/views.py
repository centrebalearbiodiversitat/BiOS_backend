from django.http import HttpResponse
import csv


class CSVDownloadMixin:
	@staticmethod
	def flatten_json(data, keys_to_flatten):
		flattened_data = []

		for item in data:
			new_item = item.copy()
			for key in keys_to_flatten:
				nested_items = new_item.pop(key, [])
				for nested_item in nested_items:
					for k, v in nested_item.items():
						if isinstance(v, dict):
							for nk, nv in v.items():
								new_item[f"{key}_{k}_{nk}"] = nv
						elif isinstance(v, list):
							new_item[f"{key}_{k}"] = str(v)
						else:
							new_item[f"{key}_{k}"] = v
			flattened_data.append(new_item)

		return flattened_data

	@staticmethod
	def generate_csv(flattened_data, filename="data.csv"):
		response = HttpResponse(content_type="text/csv")
		response["Content-Disposition"] = f'attachment; filename="{filename}"'

		if flattened_data:
			writer = csv.DictWriter(response, fieldnames=flattened_data[0].keys())
			writer.writeheader()
			writer.writerows(flattened_data)

		return response
