# Generated by Django 3.1.7 on 2021-03-19 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_fill_in_courier_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assign_time', models.DateTimeField(blank=True, null=True)),
                ('complete_time', models.DateTimeField(blank=True, null=True)),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to='core.courier')),
                ('initial_courier_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to='core.couriertype'))
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='shipment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='core.shipment'),
        ),
    ]
