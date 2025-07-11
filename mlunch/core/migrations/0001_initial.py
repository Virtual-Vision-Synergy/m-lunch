# Generated by Django 5.2.3 on 2025-07-09 14:15

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('mot_de_passe', models.CharField(max_length=128)),
                ('date_inscri', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('mot_de_passe', models.CharField(max_length=128)),
                ('contact', models.CharField(blank=True, max_length=50, null=True)),
                ('prenom', models.CharField(blank=True, max_length=100, null=True)),
                ('nom', models.CharField(blank=True, max_length=100, null=True)),
                ('date_inscri', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Entite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LimiteCommandesJournalieres',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_commandes', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Livreur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('contact', models.TextField(blank=True, null=True)),
                ('position', models.CharField(blank=True, max_length=100, null=True)),
                ('geo_position', models.CharField(blank=True, default='0,0', help_text='Format: latitude,longitude', max_length=100, null=True)),
                ('date_inscri', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='ModePaiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='PointRecup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150)),
                ('geo_position', models.CharField(blank=True, default='0,0', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Repas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.TextField(blank=True, null=True)),
                ('prix', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('mot_de_passe', models.CharField(max_length=128)),
                ('adresse', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.TextField(blank=True, null=True)),
                ('geo_position', models.CharField(blank=True, default='0,0', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatutCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatutEntite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StatutLivraison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatutLivreur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatutRestaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatutZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypeRepas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('zone', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cree_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commandes', to='core.client')),
                ('mode_paiement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.modepaiement')),
                ('point_recup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pointrecup')),
            ],
        ),
        migrations.CreateModel(
            name='Livraison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribue_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livraisons', to='core.commande')),
                ('livreur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livraisons', to='core.livreur')),
            ],
        ),
        migrations.CreateModel(
            name='CommandePaiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ajouter_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('paiement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.modepaiement')),
            ],
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pourcentage_reduction', models.IntegerField()),
                ('date_concerne', models.DateField()),
                ('repas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.repas')),
            ],
        ),
        migrations.CreateModel(
            name='DisponibiliteRepas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('est_dispo', models.BooleanField(default=True)),
                ('mis_a_jour_le', models.DateTimeField(auto_now=True)),
                ('repas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disponibilites', to='core.repas')),
            ],
        ),
        migrations.CreateModel(
            name='HoraireSpecial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_concerne', models.DateField()),
                ('horaire_debut', models.TimeField()),
                ('horaire_fin', models.TimeField()),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='Horaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('le_jour', models.IntegerField()),
                ('horaire_debut', models.TimeField()),
                ('horaire_fin', models.TimeField()),
                ('mis_a_jour_le', models.DateTimeField(auto_now=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horaire', to='core.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valeur', models.IntegerField()),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueStatutCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques', to='core.commande')),
                ('statut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.statutcommande')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueStatutEntite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('entite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques', to='core.entite')),
                ('statut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.statutentite')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueStatutLivraison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('livraison', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques', to='core.livraison')),
                ('statut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.statutlivraison')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueStatutLivreur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('livreur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques', to='core.livreur')),
                ('statut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.statutlivreur')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueStatutRestaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques', to='core.restaurant')),
                ('statut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.statutrestaurant')),
            ],
        ),
        migrations.AddField(
            model_name='repas',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.typerepas'),
        ),
        migrations.CreateModel(
            name='HistoriqueZonesRecuperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('point_recup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pointrecup')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques_recuperation', to='core.zone')),
            ],
        ),
        migrations.CreateModel(
            name='HistoriqueStatutZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('statut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.statutzone')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques', to='core.zone')),
            ],
        ),
        migrations.CreateModel(
            name='CommandeRepas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.IntegerField()),
                ('ajoute_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repas_commandes', to='core.commande')),
                ('repas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commandes_repas', to='core.repas')),
            ],
            options={
                'unique_together': {('commande', 'repas')},
            },
        ),
        migrations.CreateModel(
            name='RestaurantRepas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.repas')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.restaurant')),
            ],
            options={
                'unique_together': {('restaurant', 'repas')},
            },
        ),
        migrations.CreateModel(
            name='SuivisCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statut', models.BooleanField(default=False)),
                ('mis_a_jour_le', models.DateTimeField(default=django.utils.timezone.now)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suivis_commandes', to='core.commande')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suivis_commandes', to='core.restaurant')),
            ],
            options={
                'ordering': ['-mis_a_jour_le'],
                'unique_together': {('commande', 'restaurant', 'mis_a_jour_le')},
            },
        ),
        migrations.CreateModel(
            name='ReferenceZoneEntite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entite')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.zone')),
            ],
            options={
                'unique_together': {('zone', 'entite')},
            },
        ),
        migrations.CreateModel(
            name='ZoneClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.client')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.zone')),
            ],
            options={
                'unique_together': {('client', 'zone')},
            },
        ),
        migrations.CreateModel(
            name='ZoneLivreur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('livreur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.livreur')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.zone')),
            ],
            options={
                'unique_together': {('zone', 'livreur')},
            },
        ),
        migrations.CreateModel(
            name='ZoneRestaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.restaurant')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.zone')),
            ],
            options={
                'unique_together': {('restaurant', 'zone')},
            },
        ),
    ]
