-- Create and populate the thyroidDF table
CREATE TABLE IF NOT EXISTS thyroidDF  (
    age INTEGER,
    sex VARCHAR(20),
    on_thyroxine VARCHAR(20),
    query_on_thyroxine VARCHAR(20),
    on_antithyroid_meds VARCHAR(20),
    sick VARCHAR(20),
    pregnant VARCHAR(20),
    thyroid_surgery VARCHAR(20),
    I20320_treatment VARCHAR(20),
    query_hypothyroid VARCHAR(20),
    query_hyperthyroid VARCHAR(20),
    lithium VARCHAR(20),
    goitre VARCHAR(20),
    tumor VARCHAR(20),
    hypopituitary VARCHAR(20),
    psych VARCHAR(20),
    TSH_measured VARCHAR(20),
    TSH DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    T3_measured VARCHAR(20),
    T3 DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    TT4_measured VARCHAR(20),
    TT4 DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    T4U_measured VARCHAR(20),
    T4U DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    FTI_measured VARCHAR(20),
    FTI DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    TBG_measured VARCHAR(20),
    TBG DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    referral_source VARCHAR(255),
    target VARCHAR(255),
    patient_id VARCHAR(255)
);