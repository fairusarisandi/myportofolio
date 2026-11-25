from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0007_experience_starred_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='thumbnail',
            new_name='project_image_url',
        ),
        migrations.AddField(
            model_name='project',
            name='tech_stack',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='project',
            name='project_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
