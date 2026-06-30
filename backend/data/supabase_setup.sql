-- ============================================================
-- CIVIC-SHIELD: Supabase Database Setup
-- Project: CS-LARP
-- Run this in Supabase SQL Editor
-- ============================================================

-- 1. CIVIC_INCIDENTS TABLE (core data store)
CREATE TABLE IF NOT EXISTS civic_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_type TEXT NOT NULL,
    district TEXT NOT NULL,
    taluk TEXT DEFAULT '',
    severity FLOAT DEFAULT 0.5 CHECK (severity >= 0 AND severity <= 1),
    law_matched TEXT DEFAULT '',
    pseudonym TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for fast district queries (heatmap)
CREATE INDEX IF NOT EXISTS idx_civic_incidents_district ON civic_incidents(district);
CREATE INDEX IF NOT EXISTS idx_civic_incidents_type ON civic_incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_civic_incidents_created ON civic_incidents(created_at DESC);

-- 2. ENABLE ROW LEVEL SECURITY (allow anonymous inserts for field reporting)
ALTER TABLE civic_incidents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous insert"
ON civic_incidents FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anonymous select"
ON civic_incidents FOR SELECT
TO anon
USING (true);

-- 3. DISTRICT SUMMARY FUNCTION (used by analytics + T-GAT)
CREATE OR REPLACE FUNCTION district_incident_summary()
RETURNS TABLE(district TEXT, count BIGINT, avg_severity FLOAT, latest TIMESTAMPTZ)
LANGUAGE sql
AS $$
    SELECT
        district,
        COUNT(*) as count,
        AVG(severity) as avg_severity,
        MAX(created_at) as latest
    FROM civic_incidents
    GROUP BY district
    ORDER BY count DESC;
$$;

-- 4. SEED SAMPLE DATA (for demo / dashboard testing)
INSERT INTO civic_incidents (incident_type, district, taluk, severity, law_matched, pseudonym) VALUES
('caste_discrimination', 'Belagavi', 'Bailhongal', 0.85, 'SC/ST Prevention of Atrocities Act', 'Citizen-A1B2'),
('domestic_violence', 'Mysuru', 'Nanjangud', 0.72, 'PWDV Act 2005', 'Citizen-C3D4'),
('wage_theft', 'Bengaluru Urban', 'Yelahanka', 0.60, 'Payment of Wages Act', 'Citizen-E5F6'),
('mnrega_denial', 'Kalaburagi', 'Aland', 0.65, 'MGNREGA 2005', 'Citizen-G7H8'),
('ration_denial', 'Bidar', 'Basavakalyan', 0.55, 'National Food Security Act', 'Citizen-I9J0'),
('healthcare_denial', 'Dakshina Kannada', 'Bantwal', 0.70, 'Ayushman Bharat PM-JAY', 'Citizen-K1L2'),
('caste_discrimination', 'Raichur', 'Sindhanur', 0.90, 'SC/ST Prevention of Atrocities Act', 'Citizen-M3N4'),
('domestic_violence', 'Dharwad', 'Hubli', 0.68, 'PWDV Act 2005', 'Citizen-O5P6'),
('child_labour', 'Vijayapura', 'Sindagi', 0.95, 'Child Labour Act 1986', 'Citizen-Q7R8'),
('land_encroachment', 'Shivamogga', 'Tirthahalli', 0.75, 'Forest Rights Act 2006', 'Citizen-S9T0');

-- Verify
SELECT COUNT(*) as total_incidents, COUNT(DISTINCT district) as districts FROM civic_incidents;
