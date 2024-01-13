INSERT INTO heartDF (Age, Sex, Chest_pain_type, BP, FBS_over_120, Cholesterol, EKG_results, Max_HR, Exercise_angina, ST_depression, Slope_of_ST, Number_of_vessels_fluro, Heart_Disease)
SELECT Age, Sex, Chest_pain_type, BP, FBS_over_120, Cholesterol, EKG_results, Max_HR, Exercise_angina, ST_depression, Slope_of_ST, Number_of_vessels_fluro, Heart_Disease
FROM heartDF_temp;

DROP TABLE IF EXISTS heartDF_temp;