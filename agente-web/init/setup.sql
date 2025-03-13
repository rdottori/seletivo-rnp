CREATE TABLE IF NOT EXISTS ping_results (
    host VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rtt_min FLOAT,
    rtt_avg FLOAT,
    rtt_max FLOAT,
    rtt_mdev FLOAT,
    packet_loss FLOAT,
	PRIMARY KEY (host,timestamp)
);

CREATE TABLE IF NOT EXISTS track_results (
    host VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    loading_time FLOAT,
    status_code INT,
	PRIMARY KEY (host,timestamp)
);
