import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_user_tokens_to_spaces(apps, schema_editor):
    MemorySpace = apps.get_model("portal", "MemorySpace")
    PersonalAccessToken = apps.get_model("portal", "PersonalAccessToken")
    user_ids = (
        PersonalAccessToken.objects.filter(scope_type="user")
        .order_by()
        .values_list("user_id", flat=True)
        .distinct()
    )
    for user_id in user_ids:
        space = MemorySpace.objects.create(
            id=uuid.uuid4(), owner_id=user_id, name="Личное пространство"
        )
        PersonalAccessToken.objects.filter(
            user_id=user_id, scope_type="user"
        ).update(scope_type="space", memory_space_id=space.id)


class Migration(migrations.Migration):
    dependencies = [("portal", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="MemorySpace",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memory_spaces", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddConstraint(
            model_name="memoryspace",
            constraint=models.UniqueConstraint(fields=("owner", "name"), name="unique_memory_space_name_per_owner"),
        ),
        migrations.AddField(
            model_name="personalaccesstoken",
            name="memory_space",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="tokens", to="portal.memoryspace"),
        ),
        migrations.RemoveConstraint(
            model_name="personalaccesstoken",
            name="token_scope_matches_project",
        ),
        migrations.RunPython(migrate_user_tokens_to_spaces, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="personalaccesstoken",
            name="scope_type",
            field=models.CharField(choices=[("space", "Пространство памяти"), ("project", "Проект")], max_length=16),
        ),
        migrations.AddConstraint(
            model_name="personalaccesstoken",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("memory_space__isnull", False), ("project__isnull", True), ("scope_type", "space")),
                    models.Q(("memory_space__isnull", True), ("project__isnull", False), ("scope_type", "project")),
                    _connector="OR",
                ),
                name="token_scope_matches_project",
            ),
        ),
    ]
