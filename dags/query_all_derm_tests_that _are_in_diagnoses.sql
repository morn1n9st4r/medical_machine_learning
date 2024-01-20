select pbr.gender, (CURRENT_DATE - pbr.date_of_birth)/365 AS age, '1' as class,
    pdt.erythema,
    pdt.scaling,
    pdt.definite_borders,
    pdt.itching,
    pdt.koebner_phenomenon,
    pdt.polygonal_papules,
    pdt.follicular_papules,
    pdt.oral_mucosal_involvement,
    pdt.knee_and_elbow_involvement,
    pdt.scalp_involvement,
    pdt.family_history,
    pdt.melanin_incontinence,
    pdt.eosinophils_in_the_infiltrate ,
    pdt."PNL_infiltrate",
    pdt.fibrosis_of_the_papillary_dermis ,
    pdt.exocytosis,
    pdt.acanthosis,
    pdt.hyperkeratosis,
    pdt.parakeratosis,
    pdt.clubbing_of_the_rete_ridges,
    pdt.elongation_of_the_rete_ridges,
    pdt.thinning_of_the_suprapapillary_epidermis,
    pdt.spongiform_pustule,
    pdt.munro_microabcess,
    pdt.focal_hypergranulosis,
    pdt.disappearance_of_the_granular_layer,
    pdt.vacuolisation_and_damage_of_basal_layer,
    pdt.spongiosis,
    pdt.saw_tooth_appearance_of_retes,
    pdt.follicular_horn_plug,
    pdt.perifollicular_parakeratosis,
    pdt.inflammatory_monoluclear_inflitrate,
    pdt.band_like_infiltrate
from main_patientdermatologytest pdt
join main_patientbaserecord pbr
on pbr.id = pdt.patient_id
where pdt.id in (
	select unnest(string_to_array(pd.examinations, ', '))::uuid AS parsed_uuid
	from main_patientdiagnosis pd
	where pd.tags = 'SD'
)