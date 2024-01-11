-- Create and populate the thyroidDF table
CREATE TABLE IF NOT EXISTS thyroidDF  (
    age INTEGER,
    sex VARCHAR(1),
    on_thyroxine VARCHAR(1),
    query_on_thyroxine VARCHAR(1),
    on_antithyroid_meds VARCHAR(1),
    sick VARCHAR(1),
    pregnant VARCHAR(1),
    thyroid_surgery VARCHAR(1),
    I131_treatment VARCHAR(1),
    query_hypothyroid VARCHAR(1),
    query_hyperthyroid VARCHAR(1),
    lithium VARCHAR(1),
    goitre VARCHAR(1),
    tumor VARCHAR(1),
    hypopituitary VARCHAR(1),
    psych VARCHAR(1),
    TSH_measured VARCHAR(1),
    TSH DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    T3_measured VARCHAR(1),
    T3 DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    TT4_measured VARCHAR(1),
    TT4 DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    T4U_measured VARCHAR(1),
    T4U DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    FTI_measured VARCHAR(1),
    FTI DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    TBG_measured VARCHAR(1),
    TBG DOUBLE PRECISION NULL,  -- Modified to allow NULL values
    referral_source VARCHAR(255),
    target VARCHAR(255),
    patient_id VARCHAR(255)
);