from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("spaces/new/", views.create_space, name="create_space"),
    path("tokens/new/", views.create_token, name="create_token"),
    path("tokens/<uuid:token_id>/revoke/", views.revoke_token, name="revoke_token"),
    path("internal/tokens/introspect", views.introspect, name="introspect"),
    path("health", views.health, name="health"),
]
