from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crimereport',
            name='crime_type',
            field=models.CharField(choices=[('theft', 'Theft / Burglary'), ('assault', 'Assault / Physical violence'), ('cybercrime', 'Cybercrime / Online fraud'), ('harassment', 'Harassment / Stalking'), ('vandalism', 'Vandalism / Property damage'), ('drug', 'Drug related'), ('fraud', 'Financial fraud / Scam'), ('missing_person', 'Missing person'), ('accident', 'Road accident'), ('other', 'Other')], max_length=30),
        ),
    ]
