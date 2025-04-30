from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.API.serializers import APIStatusSerializer


class APIStatus(APIView):
	@swagger_auto_schema(
		operation_description="Check current API status.",
		responses={
			200: APIStatusSerializer()
		}
	)
	def get(self, request):
		return Response(
			{
				"status": "If you are seeing this, everything should be working OK. Enjoy life!",
				"version": "1.0.0",
				"email": "centre.biodiversitat@uib.cat",
			}
		)
