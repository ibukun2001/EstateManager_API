from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='professional_type',
            field=models.CharField(
                choices=[
                    ('Surveyor', 'Surveyor'),
                    ('Lawyer', 'Lawyer'),
                    ('Architect', 'Architect'),
                    ('Builder', 'Builder'),
                    ('Valuer', 'Valuer'),
                ],
                max_length=20,
            ),
        ),
    ]
