# Generated by Django 4.1.5 on 2023-05-02 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_alter_creditcard_account_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.IntegerField(max_length=11, null=True),
        ),
    ]
