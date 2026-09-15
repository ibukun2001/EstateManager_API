from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Company = apps.get_model("accounts", "Company")
    seen = set(Company.objects.exclude(slug="").values_list("slug", flat=True))

    for company in Company.objects.filter(slug=""):
        base_slug = slugify(company.name)[:240] or "company"
        slug = base_slug
        counter = 2
        while slug in seen:
            slug = f"{base_slug}-{counter}"
            counter += 1
        seen.add(slug)
        company.slug = slug
        company.save(update_fields=["slug"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_managers_alter_user_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='website',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, noop),
        migrations.AlterField(
            model_name='company',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
