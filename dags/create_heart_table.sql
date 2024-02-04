CREATE TABLE IF NOT EXISTS heartDF_temp (
    idx INT,
    Age INT,
    Sex INT,
    Chest_pain_type INT,
    BP INT,
    Cholesterol INT,
    FBS_over_120 INT,
    EKG_results INT,
    Max_HR INT,
    Exercise_angina INT,
    ST_depression FLOAT,
    Slope_of_ST INT,
    Number_of_vessels_fluro INT,
    Thallium INT,
    Heart_Disease VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS heartDF (
    Age INT,
    Sex INT,
    Chest_pain_type INT,
    BP INT,
    FBS_over_120 INT,
    Cholesterol INT,
    EKG_results INT,
    Max_HR INT,
    Exercise_angina INT,
    ST_depression FLOAT,
    Slope_of_ST INT,
    Number_of_vessels_fluro INT,
    Heart_Disease VARCHAR(10)
);