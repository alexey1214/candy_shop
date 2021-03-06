# Generated by Django 3.1.7 on 2021-03-14 06:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='CourierType',
            fields=[
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('capacity', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='OrderDeliveryInterval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.region'),
        ),
        migrations.CreateModel(
            name='CourierWorkShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.courier')),
            ],
        ),
        migrations.CreateModel(
            name='CourierRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.courier')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.region')),
            ],
        ),
        migrations.AddField(
            model_name='courier',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.couriertype'),
        ),
        migrations.AddConstraint(
            model_name='courierregion',
            constraint=models.UniqueConstraint(fields=('courier', 'region'), name='unique_courier_region'),
        ),
    ]
