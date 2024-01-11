
-- Dropping redundant attributes
ALTER TABLE thyroidDF
DROP COLUMN IF EXISTS TSH_measured,
DROP COLUMN IF EXISTS T3_measured,
DROP COLUMN IF EXISTS TT4_measured,
DROP COLUMN IF EXISTS T4U_measured,
DROP COLUMN IF EXISTS FTI_measured,
DROP COLUMN IF EXISTS TBG_measured,
DROP COLUMN IF EXISTS patient_id,
DROP COLUMN IF EXISTS referral_source;

-- Re-mapping target values to diagnostic groups
UPDATE thyroidDF
SET target = CASE
    WHEN target = '-' THEN 'negative'
    WHEN target IN ('A', 'B', 'C', 'D') THEN 'hyperthyroid'
    WHEN target IN ('E', 'F', 'G', 'H') THEN 'hypothyroid'
END;

-- Dropping observations with 'target' null after re-mapping
DELETE FROM thyroidDF WHERE target IS NULL;

-- Changing age of observations with ('age' > 100) to null
UPDATE thyroidDF
SET age = NULL
WHERE age > 100;

-- Dropping the 'TBG' column
ALTER TABLE thyroidDF
DROP COLUMN IF EXISTS TBG;

-- Dropping observations with null 'age'
DELETE FROM thyroidDF WHERE age IS NULL;

-- Updating 'sex' column based on conditions
UPDATE thyroidDF
SET sex = CASE
    WHEN sex IS NULL AND pregnant = 't' THEN 'F'
    ELSE sex
END;

DELETE FROM thyroidDF
WHERE 
  (CASE WHEN T3 IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN TSH IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN FTI IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN T4U IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN TT4 IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN goitre IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN target IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN sex IS NULL THEN 1 ELSE 0 END) +
  (CASE WHEN age IS NULL THEN 1 ELSE 0 END) > 0;


-- Reordering and selecting specific columns
CREATE TABLE thyroidDF_temp AS
SELECT T3, TSH, FTI, T4U, TT4, goitre, target, sex, age
FROM thyroidDF;

-- Drop the original table
DROP TABLE thyroidDF;

-- Rename the temporary table to the original name
ALTER TABLE thyroidDF_temp
RENAME TO thyroidDF;

