from rest_framework import permissions

class Owner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, sc):
        return super().has_permission(request, view) and request.user.id == sc.resident.id