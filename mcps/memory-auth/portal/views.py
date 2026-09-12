import base64
import binascii
import hmac

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import MemorySpaceCreateForm, TokenCreateForm
from .models import MemorySpace, PersonalAccessToken


@login_required
def dashboard(request):
    tokens = PersonalAccessToken.objects.filter(user=request.user).select_related(
        "project", "memory_space"
    )
    spaces = MemorySpace.objects.filter(owner=request.user)
    return render(request, "portal/dashboard.html", {"tokens": tokens, "spaces": spaces})


@login_required
def create_space(request):
    if request.method == "POST":
        form = MemorySpaceCreateForm(request.POST)
        if form.is_valid():
            space = form.save(commit=False)
            space.owner = request.user
            space.save()
            return redirect("dashboard")
    else:
        form = MemorySpaceCreateForm()
    return render(request, "portal/space_form.html", {"form": form})


@login_required
def create_token(request):
    if request.method == "POST":
        form = TokenCreateForm(request.POST, user=request.user)
        if form.is_valid():
            scope_type, project, memory_space = form.resolve_scope(request.user)
            token, raw_token = PersonalAccessToken.issue(
                user=request.user,
                name=form.cleaned_data["name"],
                scope_type=scope_type,
                project=project,
                memory_space=memory_space,
                can_read=form.cleaned_data["can_read"],
                can_write=form.cleaned_data["can_write"],
            )
            return render(
                request,
                "portal/token_created.html",
                {"token": token, "raw_token": raw_token},
            )
    else:
        form = TokenCreateForm(user=request.user)
    return render(request, "portal/token_form.html", {"form": form})


@login_required
@require_POST
def revoke_token(request, token_id):
    token = get_object_or_404(PersonalAccessToken, id=token_id, user=request.user)
    token.revoke()
    return redirect("dashboard")


@csrf_exempt
@require_POST
def introspect(request):
    try:
        scheme, encoded = request.headers.get("Authorization", "").split(" ", 1)
        client_id, supplied_secret = base64.b64decode(encoded).decode().split(":", 1)
    except (ValueError, UnicodeDecodeError, binascii.Error):
        client_id, supplied_secret, scheme = "", "", ""
    if (
        scheme.lower() != "basic"
        or not hmac.compare_digest(client_id, settings.INTROSPECTION_CLIENT_ID)
        or not hmac.compare_digest(supplied_secret, settings.INTROSPECTION_SECRET)
    ):
        return JsonResponse({"detail": "forbidden"}, status=403)

    raw_token = request.POST.get("token")
    if not raw_token:
        return HttpResponseBadRequest("token is required")

    token = PersonalAccessToken.authenticate(raw_token)
    if token is None:
        return JsonResponse({"active": False})

    token.mark_used()
    permissions = []
    if token.can_read:
        permissions.append("memory:read")
    if token.can_write:
        permissions.append("memory:write")
    scopes = permissions + [
        f"memory:namespace:{token.scope_type}:{token.namespace_id}",
        f"memory:subject:{token.user_id}",
    ]
    return JsonResponse(
        {
            "active": True,
            "client_id": str(token.id),
            "subject": str(token.user_id),
            "username": token.user.username,
            "scope_type": token.scope_type,
            "scope_id": token.namespace_id,
            "permissions": permissions,
            "scope": " ".join(scopes),
        }
    )


def health(request):
    return JsonResponse({"status": "ok"})
