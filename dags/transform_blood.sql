---- Update values in the 'target' column
UPDATE bloodDF SET target = '0' WHERE target = '"0=Blood Donor"';
UPDATE bloodDF SET target = '0' WHERE target = '"0s=suspect Blood Donor"';
UPDATE bloodDF SET target = '1' WHERE target = '"1=Hepatitis"';
UPDATE bloodDF SET target = '2' WHERE target = '"2=Fibrosis"';
UPDATE bloodDF SET target = '3' WHERE target = '"3=Cirrhosis"';
--
---- Drop the first column
ALTER TABLE bloodDF DROP COLUMN IF EXISTS id;
--
---- Update values in the 'Sex' column
UPDATE bloodDF SET sex = '1' WHERE sex = '"m"';
UPDATE bloodDF SET sex = '0' WHERE sex = '"f"';
--
---- Convert all columns to numeric
UPDATE bloodDF SET target = target::NUMERIC;
UPDATE bloodDF SET sex = sex::NUMERIC;
---- Repeat the above line for other columns as needed
