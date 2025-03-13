CREATE TYPE quality as ENUM ('Ótima','Boa','Regular','Ruim');

CREATE TABLE IF NOT EXISTS api_results (
    client VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    up BOOLEAN,
    bandwidth_use FLOAT,
    quality quality,
	avg_availability FLOAT,
	PRIMARY KEY (client,timestamp)
);
