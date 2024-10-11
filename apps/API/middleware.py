class DynamicSerializeMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def _filter_fields(self, data, fields_to_exclude):
		if isinstance(data, dict):
			return {k: self._filter_fields(v, fields_to_exclude) for k, v in data.items() if k not in fields_to_exclude}
		elif isinstance(data, list):
			return [self._filter_fields(item, fields_to_exclude) for item in data]
		else:
			return data

	def process_template_response(self, request, response):
		if (
			hasattr(response, "accepted_media_type") and
			response.accepted_media_type == "application/json" and
			isinstance(response.data, (list, dict))
		):
			choice = request.GET.get("choice")
			exclude = request.GET.get("exclude")

			if choice:
				choice = choice.split(",")
				filtered_data = []
				if isinstance(response.data, dict):
					filtered_data = {k: v for k, v in response.data.items() if k in choice}
				else:
					for item in response.data:
						filtered_data.append({k: v for k, v in item.items() if k in choice})

				response.data = filtered_data

			if exclude:
				exclude = exclude.split(",")
				response.data = self._filter_fields(response.data, exclude)

		return response
