# Generated by Django 4.2.1 on 2024-05-27 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nutriforce_app', '0020_rename_flavours_productcolourflavours_flavour_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=500)),
                ('flavour', models.CharField(blank=True, max_length=600, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('stock_count', models.IntegerField()),
                ('ingredients', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('created_ts', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Product Details',
                'ordering': ['product__product_id'],
            },
        ),
        migrations.AlterModelOptions(
            name='products',
            options={'ordering': ['product_name'], 'verbose_name_plural': 'Products'},
        ),
        migrations.RemoveField(
            model_name='products',
            name='active',
        ),
        migrations.RemoveField(
            model_name='products',
            name='created_ts',
        ),
        migrations.RemoveField(
            model_name='products',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='products',
            name='price',
        ),
        migrations.RemoveField(
            model_name='products',
            name='stock_count',
        ),
        migrations.DeleteModel(
            name='ProductColourFlavours',
        ),
        migrations.AddField(
            model_name='productdetails',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutriforce_app.products'),
        ),
    ]