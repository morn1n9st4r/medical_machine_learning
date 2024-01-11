-- Drop the 'Original' column
ALTER TABLE bodyfatDF DROP COLUMN IF EXISTS Original;

-- Replace 'M' with 'Male' and 'F' with 'Female' in the 'Sex' column
UPDATE bodyfatDF SET Sex = CASE WHEN Sex = 'M' THEN 'Male' WHEN Sex = 'F' THEN 'Female' ELSE Sex END;

-- Replace 'Male' with 1 and 'Female' with 0 in the 'Sex' column
UPDATE bodyfatDF SET Sex = CASE WHEN Sex = 'Male' THEN 1::VARCHAR WHEN Sex = 'Female' THEN 0::VARCHAR ELSE Sex END;

-- Display NaN values (NULL in PostgreSQL)