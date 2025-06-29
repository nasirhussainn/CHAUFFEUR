from rest_framework.renderers import JSONRenderer

class CustomResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        status_code = response.status_code if response else 200

        # Base structure
        response_data = {
            "success": 200 <= status_code < 300,
            "message": "Success" if 200 <= status_code < 300 else "Error"
        }

        # Override message if detail present
        if isinstance(data, dict):
            if "detail" in data:
                response_data["message"] = data["detail"]
            elif "message" in data:
                response_data["message"] = data.get("message", response_data["message"])

            # Add `data` field only if other keys exist
            payload = {k: v for k, v in data.items() if k not in ["detail", "message"]}
            if payload:
                response_data["data"] = payload
        elif data is not None:
            # Non-dict (e.g. list or string) case
            response_data["data"] = data

        return super().render(response_data, accepted_media_type, renderer_context)
