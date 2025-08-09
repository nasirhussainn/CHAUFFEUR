from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data
        # Flatten if detail is the only key
        if isinstance(detail, dict) and set(detail.keys()) == {"detail"}:
            detail = detail["detail"]
        return Response({
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "detail": detail,
            }
        }, status=response.status_code)
    else:
        return Response({
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "detail": str(exc),
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
