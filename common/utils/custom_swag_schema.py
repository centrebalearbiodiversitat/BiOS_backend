# from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def custom_swag_schema(tags: str = None, operation_id: str = None, operation_description: str = None, manual_parameters: list = None, responses=None):
	if responses is None:
		responses = {200: "Success", 400: "Bad Request", 404: "Not Found"}
	if tags is None:
		raise Exception("Missing tags parameter")

	return swagger_auto_schema(tags=[tags], operation_id=operation_id, operation_description=operation_description, manual_parameters=manual_parameters, responses=responses)
