from rest_framework.exceptions import APIException


class CBBAPIException(APIException):
	def __init__(self, detail=None, code=None):
		if isinstance(detail, list) or isinstance(detail, dict):
			detail = {"detail": detail}
		super().__init__(detail, code)
		self.status_code = code
