from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_alter_servicerequest_professional_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='service_type',
            field=models.CharField(
                choices=[
                    ('Land Survey', 'Land Survey'),
                    ('Drone Survey', 'Drone Survey'),
                    ('GIS Mapping', 'GIS Mapping'),
                    ('Valuation', 'Valuation'),
                    ('Deed of Assignment', 'Deed of Assignment'),
                    ('Construction', 'Construction'),
                    ('Appointment', 'Appointment'),
                ],
                max_length=30,
            ),
        ),
    ]
