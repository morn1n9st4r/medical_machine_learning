select pbr.gender, (CURRENT_DATE - pbr.date_of_birth)/365 AS age, 1 as target,
    pbt.alb,
    pbt.alp,
    pbt.alt,
    pbt.ast,
    pbt.bil,
    pbt.che,
    pbt.chol,
    pbt.crea,
    pbt.gct,
    pbt.prot
from main_patientbloodtest pbt
join main_patientbaserecord pbr
on pbr.id = pbt.patient_id
where pbt.id in (
	select unnest(string_to_array(pd.examinations, ', '))::uuid AS parsed_uuid
	from main_patientdiagnosis pd
	where pd.tags = 'HD'
)