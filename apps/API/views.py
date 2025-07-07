# from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

# from apps.API.serializers import APIStatusSerializer
from common.utils.custom_swag_schema import custom_swag_schema


class APIStatus(APIView):
	@custom_swag_schema(
		tags="Status",
		operation_id="Check API status",
		operation_description="Check current API status.",
	)
	def get(self, request):
		return Response(
			{
				"status": "If you are seeing this, everything should be working OK. Enjoy life!",
				"version": "1.0.0",
				"email": "centre.biodiversitat@uib.cat",
			}
		)
