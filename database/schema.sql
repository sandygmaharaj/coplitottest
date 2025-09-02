-- Company information database schema
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ticker_symbol VARCHAR(10) UNIQUE,
    industry VARCHAR(100),
    sector VARCHAR(100),
    market_cap BIGINT,
    employees INTEGER,
    founded_year INTEGER,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker_symbol);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);

-- Sample data
INSERT INTO companies (name, ticker_symbol, industry, sector, market_cap, employees, founded_year, headquarters, website, description) VALUES
('Apple Inc.', 'AAPL', 'Consumer Electronics', 'Technology', 3000000000000, 164000, 1976, 'Cupertino, CA', 'https://www.apple.com', 'Apple Inc. is an American multinational technology company specializing in consumer electronics, software, and online services.'),
('Microsoft Corporation', 'MSFT', 'Software', 'Technology', 2800000000000, 221000, 1975, 'Redmond, WA', 'https://www.microsoft.com', 'Microsoft Corporation is an American multinational technology corporation that develops and sells computer software, consumer electronics, personal computers, and related services.'),
('Amazon.com Inc.', 'AMZN', 'E-commerce', 'Consumer Discretionary', 1500000000000, 1500000, 1994, 'Seattle, WA', 'https://www.amazon.com', 'Amazon.com, Inc. is an American multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence.'),
('Alphabet Inc.', 'GOOGL', 'Internet Services', 'Technology', 1700000000000, 174000, 1998, 'Mountain View, CA', 'https://www.google.com', 'Alphabet Inc. is an American multinational technology conglomerate holding company headquartered in Mountain View, California.'),
('Tesla Inc.', 'TSLA', 'Electric Vehicles', 'Consumer Discretionary', 800000000000, 140000, 2003, 'Austin, TX', 'https://www.tesla.com', 'Tesla, Inc. is an American electric vehicle and clean energy company based in Austin, Texas.')
ON CONFLICT (ticker_symbol) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();