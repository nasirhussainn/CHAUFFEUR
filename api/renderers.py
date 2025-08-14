from rest_framework.renderers import JSONRenderer

class CustomResponseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        status_code = response.status_code if response else 200

        # Base response
        response_data = {
            "success": 200 <= status_code < 300,
            "message": "Success" if 200 <= status_code < 300 else "Error"
        }

        # Handle errors more clearly
        if not (200 <= status_code < 300) and isinstance(data, dict):
            if "detail" in data:
                response_data["message"] = str(data["detail"])
            elif "message" in data:
                response_data["message"] = str(data.get("message"))
            else:
                # Build a user-friendly combined message
                error_messages = []
                for field, errors in data.items():
                    field_name = field.replace("_", " ").capitalize()
                    if isinstance(errors, (list, tuple)):
                        for err in errors:
                            error_messages.append(f"{field_name}: {err}")
                    else:
                        error_messages.append(f"{field_name}: {errors}")
                if error_messages:
                    response_data["message"] = "Error: " + "; ".join(error_messages)

        # Keep 'data' for developers
        if isinstance(data, dict):
            payload = {k: v for k, v in data.items() if k not in ["detail", "message"]}
            if payload:
                response_data["data"] = payload
        elif data is not None:
            response_data["data"] = data

        return super().render(response_data, accepted_media_type, renderer_context)
