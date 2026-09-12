import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("auth", "0012_alter_user_first_name_max_length")]
    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("members", models.ManyToManyField(blank=True, related_name="memory_projects", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="PersonalAccessToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("scope_type", models.CharField(choices=[("user", "Личная память"), ("project", "Проект")], max_length=16)),
                ("secret_digest", models.CharField(editable=False, max_length=64)),
                ("prefix", models.CharField(db_index=True, editable=False, max_length=32)),
                ("can_read", models.BooleanField(default=True)),
                ("can_write", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="tokens", to="portal.project")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memory_tokens", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="personalaccesstoken",
            constraint=models.CheckConstraint(
                condition=models.Q(("project__isnull", True), ("scope_type", "user"), _connector="AND")
                | models.Q(("project__isnull", False), ("scope_type", "project"), _connector="AND"),
                name="token_scope_matches_project",
            ),
        ),
    ]

