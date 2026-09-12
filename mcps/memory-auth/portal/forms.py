from django import forms

from .models import MemorySpace, PersonalAccessToken, Project


class MemorySpaceCreateForm(forms.ModelForm):
    class Meta:
        model = MemorySpace
        fields = ("name",)
        labels = {"name": "Название"}


class TokenCreateForm(forms.Form):
    name = forms.CharField(label="Название", max_length=120)
    namespace = forms.ChoiceField(label="Область памяти")
    can_read = forms.BooleanField(label="Чтение", required=False, initial=True)
    can_write = forms.BooleanField(label="Запись", required=False, initial=True)

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        spaces = MemorySpace.objects.filter(owner=user, is_active=True).order_by("name")
        choices = [
            (f"space:{space.pk}", f"Пространство: {space.name}") for space in spaces
        ]
        projects = Project.objects.filter(members=user, is_active=True).order_by("name")
        choices.extend((f"project:{project.pk}", f"Проект: {project.name}") for project in projects)
        self.fields["namespace"].choices = choices

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("can_read") and not cleaned.get("can_write"):
            raise forms.ValidationError("Выберите хотя бы одно разрешение.")
        return cleaned

    def resolve_scope(self, user):
        namespace = self.cleaned_data["namespace"]
        if namespace.startswith("space:"):
            space_id = namespace.removeprefix("space:")
            space = MemorySpace.objects.get(pk=space_id, owner=user, is_active=True)
            return PersonalAccessToken.ScopeType.SPACE, None, space
        project_id = namespace.removeprefix("project:")
        project = Project.objects.get(pk=project_id, members=user, is_active=True)
        return PersonalAccessToken.ScopeType.PROJECT, project, None
