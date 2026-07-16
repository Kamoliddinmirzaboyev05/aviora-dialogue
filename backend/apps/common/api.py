from rest_framework.response import Response


def api_error(code, message, fields=None, status=400):
    return Response(
        {"error": {"code": code, "message": message, "fields": fields or {}}},
        status=status,
    )


def api_success(data, status=200):
    return Response(data, status=status)
