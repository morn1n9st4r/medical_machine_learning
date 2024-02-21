GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

SEVERITY_CHOICES = [
    ('NO', 'None'),
    ('MI', 'Mild'),
    ('MO', 'Moderate'),
    ('SE', 'Severe'),
    ('CR', 'Critical'),
]

DERMATOLOGY_CHOICES = [
    ('0', 'None'),
    ('1', 'Mild'),
    ('2', 'Moderate'),
    ('3', 'Severe'),
]

CHESTPAIN_CHOICES = [
    ('NP', 'No Pain'),
    ('TA', 'Typical Angina'),
    ('ATA', 'Atypical Angina'),
    ('NAP', 'Non-Anginal Pain'),
    ('ASY', 'Asymptomatic'),
]

MODELTYPE_CHOICES = [
    ('CLF', 'Classification'),
    ('REG', 'Regression'),
]

ECG_CHOICES = [
    ('Normal', 'Normal'),
    ('ST', 'ST-T wave abnormality'),
    ('LVH', 'Left ventricular hypertrophy'),
]

SLOPE_CHOICES = [
    ('Up', 'Upsloping'),
    ('Flat', 'Flat'),
    ('Down', 'Downsloping'),
]


TAGS_CHOICES = [
    ('AD', 'Autoimmune Disorder'),
    ('GD', 'Genetic Disorder'),
    ('ID', 'Infectious Disease'),
    ('MH', 'Mental Health'),
    ('CV', 'Cardiovascular'),
    ('EN', 'Endocrine'),
    ('RS', 'Respiratory'),
    ('NE', 'Neurological'),
    ('GI', 'Gastrointestinal'),
    ('MS', 'Musculoskeletal'),
    ('ON', 'Oncological'),
    ('PD', 'Pediatric'),
    ('AL', 'Allergic Condition'),
    ('ID', 'Inflammatory Disorder'),
    ('MD', 'Metabolic Disorder'),
    ('VD', 'Vascular Disorder'),
    ('TD', 'Traumatic Injury'),
    ('ND', 'Nutritional Disorder'),
    ('SD', 'Skin Disorder'),
    ('UD', 'Urological Disorder'),
    ('HD', 'Hepatological disorder ')
]

FORM_CHOICES = [
    ('PO', 'per os'),
    ('IM', 'intramuscularly'),
    ('Subq', 'subcutaneous'),
    ('Rectally', 'rectally'),
    ('IV', 'intravenously'),
    ('OD', 'in the right eye'),
    ('OS', 'in the left eye'),
    ('OU', 'in both eyes'),
    ('SL', 'sublingually'),
    ('ID', 'intradermally'),
    ('IH', 'inhalation'),
    ('TD', 'topical'),
    ('PR', 'per rectum'),
    ('NPO', 'nil per os'),
    ('NG', 'nasogastric'),
]

FREQUENCY_CHOICES = [
    ('DA', 'daily'),
    ('WE', 'weekly')
]
