import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_company_slug_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referred_by_company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referred_buyers',
                to='accounts.company',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='referred_by_url',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
