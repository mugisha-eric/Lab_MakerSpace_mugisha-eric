PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT INTO Member (name, email, phone, active)
SELECT 'Alice Niyonizigiye', 'alice.n@example.com', '+230 5251 1020', 1
WHERE NOT EXISTS (SELECT 1 FROM Member WHERE email = 'alice.n@example.com');

INSERT INTO Member (name, email, phone, active)
SELECT 'Brian Mutesi', 'brian.m@example.com', '+230 5251 1021', 1
WHERE NOT EXISTS (SELECT 1 FROM Member WHERE email = 'brian.m@example.com');

INSERT INTO Member (name, email, phone, active)
SELECT 'Chantal Uwase', 'chantal.u@example.com', NULL, 1
WHERE NOT EXISTS (SELECT 1 FROM Member WHERE email = 'chantal.u@example.com');

INSERT INTO Equipment (name, category, description, available)
SELECT 'Canon EOS R50', 'Camera', 'Mirrorless camera with 18–45mm lens', 0
WHERE NOT EXISTS (SELECT 1 FROM Equipment WHERE name = 'Canon EOS R50');

INSERT INTO Equipment (name, category, description, available)
SELECT 'Arduino Uno R3', 'Electronics', 'Microcontroller development board', 1
WHERE NOT EXISTS (SELECT 1 FROM Equipment WHERE name = 'Arduino Uno R3');

INSERT INTO Equipment (name, category, description, available)
SELECT 'Prusa MINI+', '3D Printing', 'Compact FDM 3D printer', 0
WHERE NOT EXISTS (SELECT 1 FROM Equipment WHERE name = 'Prusa MINI+');

INSERT INTO Equipment (name, category, description, available)
SELECT 'Blue Yeti Microphone', 'Audio', 'USB condenser microphone', 0
WHERE NOT EXISTS (SELECT 1 FROM Equipment WHERE name = 'Blue Yeti Microphone');

INSERT INTO Loans (token, member_id, equipment_id, loan_data, due_date, return_date)
SELECT
  'LOAN-2026-001',
  (SELECT id FROM Member WHERE email = 'alice.n@example.com'),
  (SELECT id FROM Equipment WHERE name = 'Canon EOS R50'),
  '2026-09-18', '2026-09-25', NULL
WHERE NOT EXISTS (SELECT 1 FROM Loans WHERE token = 'LOAN-2026-001');

INSERT INTO Loans (token, member_id, equipment_id, loan_data, due_date, return_date)
SELECT
  'LOAN-2026-002',
  (SELECT id FROM Member WHERE email = 'brian.m@example.com'),
  (SELECT id FROM Equipment WHERE name = 'Prusa MINI+'),
  '2026-09-20', '2026-09-27', NULL
WHERE NOT EXISTS (SELECT 1 FROM Loans WHERE token = 'LOAN-2026-002');

COMMIT;