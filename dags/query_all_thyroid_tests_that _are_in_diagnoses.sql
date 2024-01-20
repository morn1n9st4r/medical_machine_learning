select pbr.gender, (CURRENT_DATE - pbr.date_of_birth)/365 AS age, 'hypothyroid' as target,
    ptt.goitre,
    ptt.t4u,
    ptt.tt4,
    ptt.t3,
    ptt.tsh,
    ptt.fti
from main_patientthyroidtest ptt
join main_patientbaserecord pbr
on pbr.id = ptt.patient_id
where ptt.id in (
	select unnest(string_to_array(pd.examinations, ', '))::uuid AS parsed_uuid
	from main_patientdiagnosis pd
	where pd.tags = 'EN'
)