import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.choices import DERMATOLOGY_CHOICES
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientDermatologyTest

class Command(BaseCommand):
    help = 'Populates the PatientDermatologyTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(1):
            patient = PatientBaseRecord.objects.order_by('?').first()
            
            new_id_in_registry = MedicalRecordRegistry()
            new_id_in_registry.save()
            latest_record = MedicalRecordRegistry.objects.order_by('-id').first()
            
            record = PatientDermatologyTest(
                id=latest_record.id,
                patient=patient,
                date=datetime.now() - timedelta(days=random.randint(0, 365*3)),
                family_history=random.choice([True, False]),
                erythema=random.choice(DERMATOLOGY_CHOICES),
                scaling=random.choice(DERMATOLOGY_CHOICES),
                definite_borders=random.choice(DERMATOLOGY_CHOICES),
                itching=random.choice(DERMATOLOGY_CHOICES),
                koebner_phenomenon=random.choice(DERMATOLOGY_CHOICES),
                polygonal_papules=random.choice(DERMATOLOGY_CHOICES),
                follicular_papules=random.choice(DERMATOLOGY_CHOICES),
                oral_mucosal_involvement=random.choice(DERMATOLOGY_CHOICES),
                knee_and_elbow_involvement=random.choice(DERMATOLOGY_CHOICES),
                scalp_involvement=random.choice(DERMATOLOGY_CHOICES),
                melanin_incontinence=random.choice(DERMATOLOGY_CHOICES),
                eosinophils_in_the_infiltrate=random.choice(DERMATOLOGY_CHOICES),
                PNL_infiltrate=random.choice(DERMATOLOGY_CHOICES),
                fibrosis_of_the_papillary_dermis=random.choice(DERMATOLOGY_CHOICES),
                exocytosis=random.choice(DERMATOLOGY_CHOICES),
                acanthosis=random.choice(DERMATOLOGY_CHOICES),
                hyperkeratosis=random.choice(DERMATOLOGY_CHOICES),
                parakeratosis=random.choice(DERMATOLOGY_CHOICES),
                clubbing_of_the_rete_ridges=random.choice(DERMATOLOGY_CHOICES),
                elongation_of_the_rete_ridges=random.choice(DERMATOLOGY_CHOICES),
                thinning_of_the_suprapapillary_epidermis=random.choice(DERMATOLOGY_CHOICES),
                spongiform_pustule=random.choice(DERMATOLOGY_CHOICES),
                munro_microabcess=random.choice(DERMATOLOGY_CHOICES),
                focal_hypergranulosis=random.choice(DERMATOLOGY_CHOICES),
                disappearance_of_the_granular_layer=random.choice(DERMATOLOGY_CHOICES),
                vacuolisation_and_damage_of_basal_layer=random.choice(DERMATOLOGY_CHOICES),
                spongiosis=random.choice(DERMATOLOGY_CHOICES),
                saw_tooth_appearance_of_retes=random.choice(DERMATOLOGY_CHOICES),
                follicular_horn_plug=random.choice(DERMATOLOGY_CHOICES),
                perifollicular_parakeratosis=random.choice(DERMATOLOGY_CHOICES),
                inflammatory_monoluclear_inflitrate=random.choice(DERMATOLOGY_CHOICES),
                band_like_infiltrate=random.choice(DERMATOLOGY_CHOICES),
            )
            record.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated PatientDermatologyTest model.'))