from dataclasses import dataclass

from fastmcp.server.dependencies import get_access_token


@dataclass(frozen=True)
class NamespaceGrant:
    token_id: str
    subject: str
    scope_type: str
    scope_id: str
    permissions: frozenset[str]


def current_grant(required_permission: str) -> NamespaceGrant:
    token = get_access_token()
    if token is None:
        raise PermissionError("Authentication is required")

    namespace_scope = next(
        (scope for scope in token.scopes if scope.startswith("memory:namespace:")),
        None,
    )
    subject_scope = next(
        (scope for scope in token.scopes if scope.startswith("memory:subject:")),
        None,
    )
    if namespace_scope is None or subject_scope is None:
        raise PermissionError("Token does not contain a memory namespace")
    if required_permission not in token.scopes:
        raise PermissionError(f"Token lacks {required_permission}")

    _, _, scope_type, scope_id = namespace_scope.split(":", 3)
    _, _, subject = subject_scope.split(":", 2)
    return NamespaceGrant(
        token_id=token.client_id,
        subject=subject,
        scope_type=scope_type,
        scope_id=scope_id,
        permissions=frozenset(
            scope for scope in token.scopes if scope in {"memory:read", "memory:write"}
        ),
    )
