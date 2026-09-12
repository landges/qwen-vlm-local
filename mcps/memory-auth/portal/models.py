import hashlib
import hmac
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Project(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name="memory_projects", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


class MemorySpace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="memory_spaces"
    )
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("owner", "name"), name="unique_memory_space_name_per_owner"
            )
        ]

    def __str__(self):
        return f"{self.owner.username}: {self.name}"


class PersonalAccessToken(models.Model):
    class ScopeType(models.TextChoices):
        SPACE = "space", "Пространство памяти"
        PROJECT = "project", "Проект"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memory_tokens")
    name = models.CharField(max_length=120)
    scope_type = models.CharField(max_length=16, choices=ScopeType.choices)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tokens",
        null=True,
        blank=True,
    )
    memory_space = models.ForeignKey(
        MemorySpace,
        on_delete=models.CASCADE,
        related_name="tokens",
        null=True,
        blank=True,
    )
    secret_digest = models.CharField(max_length=64, editable=False)
    prefix = models.CharField(max_length=32, editable=False, db_index=True)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        scope_type="space",
                        memory_space__isnull=False,
                        project__isnull=True,
                    )
                    | models.Q(
                        scope_type="project",
                        project__isnull=False,
                        memory_space__isnull=True,
                    )
                ),
                name="token_scope_matches_project",
            )
        ]

    @staticmethod
    def _digest(secret: str) -> str:
        return hmac.new(
            settings.PAT_PEPPER.encode(),
            secret.encode(),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    def issue(
        cls, *, user, name, scope_type, project, memory_space, can_read, can_write
    ):
        token_id = uuid.uuid4()
        secret = secrets.token_urlsafe(32)
        prefix = f"mcp_mem_{token_id.hex[:12]}"
        instance = cls.objects.create(
            id=token_id,
            user=user,
            name=name,
            scope_type=scope_type,
            project=project,
            memory_space=memory_space,
            secret_digest=cls._digest(secret),
            prefix=prefix,
            can_read=can_read,
            can_write=can_write,
        )
        return instance, f"{prefix}.{token_id.hex}.{secret}"

    @classmethod
    def authenticate(cls, raw_token: str):
        try:
            prefix, token_id, secret = raw_token.split(".", 2)
            if not prefix.startswith("mcp_mem_"):
                return None
            instance = cls.objects.select_related("user", "project", "memory_space").get(
                id=uuid.UUID(hex=token_id),
                prefix=prefix,
                revoked_at__isnull=True,
                user__is_active=True,
            )
        except (ValueError, cls.DoesNotExist):
            return None

        if not hmac.compare_digest(instance.secret_digest, cls._digest(secret)):
            return None
        if instance.scope_type == cls.ScopeType.PROJECT:
            if not instance.project or not instance.project.is_active:
                return None
            if not instance.project.members.filter(pk=instance.user_id).exists():
                return None
        elif (
            not instance.memory_space
            or not instance.memory_space.is_active
            or instance.memory_space.owner_id != instance.user_id
        ):
            return None
        return instance

    @property
    def namespace_id(self):
        if self.scope_type == self.ScopeType.SPACE:
            return str(self.memory_space_id)
        return self.project.slug

    def mark_used(self):
        now = timezone.now()
        if self.last_used_at and now - self.last_used_at < timedelta(minutes=5):
            return
        self.last_used_at = now
        self.save(update_fields=["last_used_at"])

    def revoke(self):
        self.revoked_at = timezone.now()
        self.save(update_fields=["revoked_at"])

    def __str__(self):
        return f"{self.user.username}: {self.name}"
