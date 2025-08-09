from rest_framework.renderers import JSONRenderer

class CustomResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        status_code = response.status_code if response else 200

        # If already in custom error format, return as-is
        if (
            isinstance(data, dict)
            and "success" in data
            and "error" in data
        ):
            return super().render(data, accepted_media_type, renderer_context)

        # If this is an error (status >= 400), wrap in your custom error structure
        if status_code >= 400:
            return super().render({
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "detail": data,
                }
            }, accepted_media_type, renderer_context)

        # Base structure for success
        response_data = {
            "success": True,
            "message": "Success"
        }

        if isinstance(data, dict):
            if "message" in data:
                response_data["message"] = data.get("message", response_data["message"])
            payload = {k: v for k, v in data.items() if k != "message"}
            if payload:
                response_data["data"] = payload
        elif data is not None:
            response_data["data"] = data

        return super().render(response_data, accepted_media_type, renderer_context)
