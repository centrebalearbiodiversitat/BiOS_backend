class DynamicSerializeMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		return response

	def process_template_response(self, request, response):
		if response.accepted_media_type == "application/json" and isinstance(response.data, (list, dict)):
			choice = request.GET.get("choice")

			if choice:
				choice = choice.split(",")
				filtered_data = []

				if isinstance(response.data, dict):
					filtered_data = {k: v for k, v in response.data.items() if k in choice}

				else:
					for item in response.data:
						filtered_data.append({k: v for k, v in item.items() if k in choice})

				response.data = filtered_data

		return response
