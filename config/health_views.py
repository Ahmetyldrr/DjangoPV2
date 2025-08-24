from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import redis
from django.conf import settings
from django.db import connection


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Docker containers
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "version": "1.0.0"
    }
    
    # Database check
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis check - optional
    try:
        cache_backend = settings.CACHES['default']['BACKEND']
        if 'redis' in cache_backend.lower():
            # Redis cache kullanılıyorsa test et
            import redis
            redis_client = redis.from_url(settings.CACHES['default']['LOCATION'])
            redis_client.ping()
            health_status["redis"] = "healthy"
        else:
            # Dummy cache kullanılıyorsa skip
            health_status["redis"] = "skipped (dummy cache)"
    except ImportError:
        health_status["redis"] = "skipped (redis not available)"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        # Redis hatası status'u unhealthy yapmaz (optional service)
    
    # Sadece database hatası status'u unhealthy yapar
    status_code = 200 if health_status["database"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)


@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check endpoint
    """
    return JsonResponse({"status": "ready"})


@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check endpoint
    """
    return JsonResponse({"status": "alive"})
