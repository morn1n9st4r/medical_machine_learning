import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from main.choices import DERMATOLOGY_CHOICES
from main.models import MedicalRecordRegistry, PatientBaseRecord, PatientDermatologyTest
from main.utils import create_diagnosis, create_treatment

class Command(BaseCommand):
    help = 'Populates the PatientDermatologyTest model with 1 instances.'

    def handle(self, *args, **options):

        for i in range(20):
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
            if  record.family_history and '3' in record.erythema  and '3' in record.scaling :
                diag_id = create_diagnosis(patient, 'Severe Psoriasis', 'MO', 'chronic skin condition causing red, itchy scaly patches', 'SD', False, record)
                create_treatment(patient, 'Methotrexate', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Cyclosporine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Acitretin', 1, 'tablet', 'DA', diag_id)
            elif '2' in record.definite_borders  and '2' in record.itching  and  '2' in record.koebner_phenomenon:
                diag_id = create_diagnosis(patient, 'Moderate Lichen Planus', 'MO', 'condition that can cause swelling and irritation in the skin, hair, nails and mucous membranes', 'SD', False, record)
                create_treatment(patient, 'Corticosteroids', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Antihistamines', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Retinoids', 1, 'cream', 'DA', diag_id)
            elif '1' in record.polygonal_papules and '1' in record.follicular_papules and '1' in record.oral_mucosal_involvement:
                diag_id = create_diagnosis(patient, 'Mild Pityriasis Rosea', 'MO', 'skin rash that usually begins as one large circular or oval spot on your chest, abdomen or back', 'SD', False, record)
                create_treatment(patient, 'Topical steroids', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Antihistamines', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Emollients', 1, 'cream', 'DA', diag_id)
            elif '3' in record.knee_and_elbow_involvement and '3' in record.scalp_involvement and '3' in record.melanin_incontinence:
                diag_id = create_diagnosis(patient, 'Severe Eczema', 'MO', 'condition causing skin areas to become inflamed, itchy, red, cracked, and rough', 'SD', False, record)
                create_treatment(patient, 'Topical corticosteroids', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Calcineurin inhibitors', 1, 'cream', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Systemic corticosteroids', 1, 'tablet', 'DA', diag_id)
            elif '3' in record.eosinophils_in_the_infiltrate and '3' in record.PNL_infiltrate:
                diag_id = create_diagnosis(patient, 'Severe Dermatitis', 'MO', 'inflammation of the skin', 'SD', False, record)
                create_treatment(patient, 'Hydrocortisone', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Tacrolimus', 1, 'ointment', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Crisaborole', 1, 'ointment', 'DA', diag_id)
            elif '2' in record.fibrosis_of_the_papillary_dermis and '2' in record.exocytosis and '2' in record.acanthosis:
                diag_id = create_diagnosis(patient, 'Moderate Psoriasis', 'MO', 'chronic skin condition causing red, itchy scaly patches', 'SD', False, record)
                create_treatment(patient, 'Methotrexate', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Cyclosporine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Acitretin', 1, 'tablet', 'DA', diag_id)
            elif '1' in record.hyperkeratosis and '1' in record.parakeratosis and '1' in record.clubbing_of_the_rete_ridges:
                diag_id = create_diagnosis(patient, 'Mild Ichthyosis', 'MO', 'family of genetic skin disorders characterized by dry, scaling skin that may be thickened or very thin', 'SD', False, record)
                create_treatment(patient, 'Lactic acid', 1, 'lotion', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Urea', 1, 'cream', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Tazarotene', 1, 'cream', 'DA', diag_id)
            elif '3' in record.elongation_of_the_rete_ridges and '3' in record.thinning_of_the_suprapapillary_epidermis and '3' in record.spongiform_pustule:
                diag_id = create_diagnosis(patient, 'Severe Lichen Planus', 'MO', 'condition that can cause swelling and irritation in the skin, hair, nails and mucous membranes', 'SD', False, record)
                create_treatment(patient, 'Corticosteroids', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Tacrolimus', 1, 'ointment', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Retinoids', 1, 'cream', 'DA', diag_id)
            elif '2' in record.munro_microabcess and '2' in record.focal_hypergranulosis:
                diag_id = create_diagnosis(patient, 'Moderate Psoriasis', 'MO', 'chronic skin condition causing red, itchy scaly patches', 'SD', False, record)
                create_treatment(patient, 'Methotrexate', 1, 'tablet', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Cyclosporine', 1, 'tablet', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Acitretin', 1, 'tablet', 'DA', diag_id)
            elif '3' in record.disappearance_of_the_granular_layer and '3' in record.vacuolisation_and_damage_of_basal_layer:
                diag_id = create_diagnosis(patient, 'Severe Eczema', 'MO', 'condition causing skin areas to become inflamed, itchy, red, cracked, and rough', 'SD', False, record)
                create_treatment(patient, 'Hydrocortisone', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Tacrolimus', 1, 'ointment', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Crisaborole', 1, 'ointment', 'DA', diag_id)
            elif '1' in record.spongiosis and '1' in record.saw_tooth_appearance_of_retes:
                diag_id = create_diagnosis(patient, 'Mild Dermatitis', 'MO', 'inflammation of the skin', 'SD', False, record)
                create_treatment(patient, 'Hydrocortisone', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Tacrolimus', 1, 'ointment', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Pimecrolimus', 1, 'cream', 'DA', diag_id)
            elif '2' in record.follicular_horn_plug and '2' in record.perifollicular_parakeratosis:
                diag_id = create_diagnosis(patient, 'Moderate Ichthyosis', 'MO', 'family of genetic skin disorders characterized by dry, scaling skin that may be thickened or very thin', 'SD', False, record)
                create_treatment(patient, 'Lactic acid', 1, 'lotion', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Urea', 1, 'cream', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Tazarotene', 1, 'cream', 'DA', diag_id)
            elif '3' in record.inflammatory_monoluclear_inflitrate and '3' in record.band_like_infiltrate:
                diag_id = create_diagnosis(patient, 'Severe Lichen Planus', 'MO', 'condition that can cause swelling and irritation in the skin, hair, nails and mucous membranes', 'SD', False, record)
                create_treatment(patient, 'Corticosteroids', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Tacrolimus', 1, 'ointment', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Retinoids', 1, 'cream', 'DA', diag_id)
            elif '1' in record.munro_microabcess and '1' in record.focal_hypergranulosis:
                diag_id = create_diagnosis(patient, 'Mild Psoriasis', 'MO', 'chronic skin condition causing red, itchy scaly patches', 'SD', False, record)
                create_treatment(patient, 'Calcipotriene', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Coal tar', 1, 'shampoo', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Salicylic acid', 1, 'ointment', 'DA', diag_id)
            elif '1' in record.disappearance_of_the_granular_layer and '1' in record.vacuolisation_and_damage_of_basal_layer:
                diag_id = create_diagnosis(patient, 'Mild Eczema', 'MO', 'condition causing skin areas to become inflamed, itchy, red, cracked, and rough', 'SD', False, record)
                create_treatment(patient, 'Hydrocortisone', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Pimecrolimus', 1, 'cream', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Emollient', 1, 'lotion', 'DA', diag_id)
            elif '1' in record.spongiosis and '1' in record.saw_tooth_appearance_of_retes:
                diag_id = create_diagnosis(patient, 'Mild Dermatitis', 'MO', 'inflammation of the skin', 'SD', False, record)
                create_treatment(patient, 'Hydrocortisone', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Calamine', 1, 'lotion', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Aloe vera', 1, 'gel', 'DA', diag_id)
            elif '1' in record.follicular_horn_plug and '1' in record.perifollicular_parakeratosis:
                diag_id = create_diagnosis(patient, 'Mild Ichthyosis', 'MO', 'family of genetic skin disorders characterized by dry, scaling skin that may be thickened or very thin', 'SD', False, record)
                create_treatment(patient, 'Lactic acid', 1, 'lotion', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Urea', 1, 'cream', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Glycerin', 1, 'lotion', 'DA', diag_id)
            elif '1' in record.inflammatory_monoluclear_inflitrate and '1' in record.band_like_infiltrate:
                diag_id = create_diagnosis(patient, 'Mild Lichen Planus', 'MO', 'condition that can cause swelling and irritation in the skin, hair, nails and mucous membranes', 'SD', False, record)
                create_treatment(patient, 'Hydrocortisone', 1, 'cream', 'DA', diag_id)
                if random.random() < 0.38:
                    create_treatment(patient, 'Tacrolimus', 1, 'ointment', 'DA', diag_id)
                    if random.random() < 0.31:
                        create_treatment(patient, 'Antihistamines', 1, 'tablet', 'DA', diag_id)


        self.stdout.write(self.style.SUCCESS('Successfully populated PatientDermatologyTest model.'))