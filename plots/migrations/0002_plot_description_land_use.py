from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plots', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plot',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plot',
            name='plot_type',
            field=models.CharField(
                choices=[
                    ('Residential', 'Residential'),
                    ('Commercial', 'Commercial'),
                    ('Mixed Use', 'Mixed Use'),
                    ('Agricultural', 'Agricultural'),
                    ('Industrial', 'Industrial'),
                    ('Institutional', 'Institutional'),
                    ('Infrastructure', 'Infrastructure'),
                ],
                default='Residential',
                max_length=30,
            ),
        ),
    ]
