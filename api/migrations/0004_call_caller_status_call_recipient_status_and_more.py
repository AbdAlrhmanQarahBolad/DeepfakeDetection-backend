# Generated by Django 5.0.6 on 2024-08-11 17:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_call'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='caller_status',
            field=models.IntegerField(choices=[(0, 'Real'), (1, 'Fake')], default=0),
        ),
        migrations.AddField(
            model_name='call',
            name='recipient_status',
            field=models.IntegerField(choices=[(0, 'Real'), (1, 'Fake')], default=1),
        ),
        migrations.CreateModel(
            name='DeepAudioArchive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=1000)),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deep_audio_archive', to='api.call')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='deep_audio_archive', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
