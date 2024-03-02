select pbr.gender, (CURRENT_DATE - pbr.date_of_birth)/365 AS age,
	case 
		when pui.disease_name like '%hypothyroid%' then 'hypothyroid'
		when pui.disease_name like '%hyperthyroid%' then 'hyperthyroid'
	end as target,
    ptt.goitre,
    ptt.t4u,
    ptt.tt4,
    ptt.t3,
    ptt.tsh,
    ptt.fti
from main_patientthyroidtest ptt
join main_patientbaserecord pbr
on pbr.id = ptt.patient_id
join (
	select unnest(string_to_array(pd.examinations, ', '))::bigint AS parsed_id, pd.disease_name
	from main_patientdiagnosis pd
	where pd.tags = 'EN'
) pui
on ptt.id = pui.parsed_id::bigint


