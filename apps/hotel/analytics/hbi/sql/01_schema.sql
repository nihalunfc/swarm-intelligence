-- Star schema for the sample portfolio (SQLite dialect).
-- Grain is stated for every fact table; grains are never mixed.

DROP TABLE IF EXISTS dim_hotel;
CREATE TABLE dim_hotel (
    hotel_id      INTEGER PRIMARY KEY,
    hotel_name    TEXT NOT NULL,
    style         TEXT NOT NULL,
    rooms         INTEGER NOT NULL CHECK (rooms > 0),
    base_rate     REAL NOT NULL
);

DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_key          INTEGER PRIMARY KEY,      -- yyyymmdd
    date              TEXT NOT NULL UNIQUE,     -- ISO yyyy-mm-dd
    year              INTEGER NOT NULL,
    month             INTEGER NOT NULL,
    day_of_week       INTEGER NOT NULL,         -- Monday = 0
    day_name          TEXT NOT NULL,
    season            TEXT NOT NULL,
    is_weekend_night  INTEGER NOT NULL,         -- Friday and Saturday nights
    holiday_ca        TEXT,
    holiday_us        TEXT,
    long_weekend      INTEGER NOT NULL,
    event             TEXT,
    event_type        TEXT
);

DROP TABLE IF EXISTS dim_segment;
CREATE TABLE dim_segment (segment TEXT PRIMARY KEY, segment_name TEXT NOT NULL);

DROP TABLE IF EXISTS dim_channel;
CREATE TABLE dim_channel (
    channel           TEXT PRIMARY KEY,
    channel_name      TEXT NOT NULL,
    acquisition_cost  REAL NOT NULL             -- share of room revenue
);

-- Grain: one booking, latest known state as of the extract date.
DROP TABLE IF EXISTS fact_booking;
CREATE TABLE fact_booking (
    booking_id        INTEGER PRIMARY KEY,
    hotel_id          INTEGER NOT NULL REFERENCES dim_hotel(hotel_id),
    booking_date      TEXT NOT NULL,
    arrival_date      TEXT NOT NULL,
    departure_date    TEXT NOT NULL,
    lead_days         INTEGER NOT NULL,
    nights            INTEGER NOT NULL,
    rooms             INTEGER NOT NULL,
    room_nights       INTEGER NOT NULL,
    segment           TEXT NOT NULL REFERENCES dim_segment(segment),
    channel           TEXT NOT NULL REFERENCES dim_channel(channel),
    rate              REAL NOT NULL,
    room_revenue      REAL NOT NULL,
    revenue_imputed   INTEGER NOT NULL,         -- 1 when revenue was missing at source
    status            TEXT NOT NULL,
    cancel_date       TEXT
);

-- Grain: one booking for one stay night (all statuses, so pace can be rebuilt).
DROP TABLE IF EXISTS fact_stay_night;
CREATE TABLE fact_stay_night (
    booking_id        INTEGER NOT NULL REFERENCES fact_booking(booking_id),
    stay_date         TEXT NOT NULL,
    hotel_id          INTEGER NOT NULL,
    rooms             INTEGER NOT NULL,
    revenue           REAL NOT NULL,
    status            TEXT NOT NULL,
    booking_date      TEXT NOT NULL,
    cancel_date       TEXT,
    PRIMARY KEY (booking_id, stay_date)
);

-- Grain: one denied request for one requested night.
DROP TABLE IF EXISTS fact_denied_night;
CREATE TABLE fact_denied_night (
    request_id        INTEGER NOT NULL,
    stay_date         TEXT NOT NULL,
    hotel_id          INTEGER NOT NULL,
    rooms             INTEGER NOT NULL,
    quoted_rate       REAL NOT NULL,
    PRIMARY KEY (request_id, stay_date)
);
