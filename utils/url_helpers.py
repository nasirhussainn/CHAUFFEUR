from django.conf import settings
import environ

# Initialize env
env = environ.Env()
CUSTOM_PORT = env('CUSTOM_PORT', default='8080')  # fallback if not in .env

def build_full_url(request, path):
    """
    Build a full URL. Adds :8080 in production automatically.
    """
    if settings.DEBUG:
        return request.build_absolute_uri(path)

    domain = request.get_host().split(':')[0]
    domain_with_port = f"{domain}:{CUSTOM_PORT}"
    scheme = 'https' if request.is_secure() else 'http'
    return f"{scheme}://{domain_with_port}{path}"
