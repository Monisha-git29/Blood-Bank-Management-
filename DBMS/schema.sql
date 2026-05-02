-- LifeStream Blood Bank Management System Schema

-- Create Donors Table
CREATE TABLE IF NOT EXISTS Donors (
    donor_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    last_donation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Blood_Stock Table
CREATE TABLE IF NOT EXISTS Blood_Stock (
    stock_id SERIAL PRIMARY KEY,
    blood_group VARCHAR(5) UNIQUE NOT NULL,
    quantity_ml INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Requests Table
CREATE TABLE IF NOT EXISTS Requests (
    request_id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(150) NOT NULL,
    blood_group_required VARCHAR(5) NOT NULL,
    quantity_required_ml INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- Pending, Fulfilled, Cancelled
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize Blood Stock with 0 for all groups
INSERT INTO Blood_Stock (blood_group, quantity_ml) VALUES
('A+', 0), ('A-', 0), ('B+', 0), ('B-', 0), ('AB+', 0), ('AB-', 0), ('O+', 0), ('O-', 0)
ON CONFLICT (blood_group) DO NOTHING;
