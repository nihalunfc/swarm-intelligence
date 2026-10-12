-- Reporting marts read by the dashboards.

-- Grain: one hotel for one night. Occupied = stayed or confirmed (no cancellations, no no-shows).
DROP TABLE IF EXISTS mart_daily_hotel;
CREATE TABLE mart_daily_hotel AS
WITH sold AS (
    SELECT hotel_id, stay_date,
           SUM(rooms)   AS rooms_sold,
           SUM(revenue) AS room_revenue
    FROM fact_stay_night
    WHERE status IN ('Checked out', 'Confirmed')
    GROUP BY hotel_id, stay_date
),
denied AS (
    SELECT hotel_id, stay_date, SUM(rooms) AS rooms_denied
    FROM fact_denied_night
    GROUP BY hotel_id, stay_date
)
SELECT d.date                                   AS stay_date,
       h.hotel_id,
       h.rooms                                  AS capacity,
       COALESCE(s.rooms_sold, 0)                AS rooms_sold,
       ROUND(COALESCE(s.room_revenue, 0), 2)    AS room_revenue,
       COALESCE(x.rooms_denied, 0)              AS rooms_denied,
       ROUND(1.0 * COALESCE(s.rooms_sold, 0) / h.rooms, 4)                         AS occupancy,
       ROUND(COALESCE(s.room_revenue, 0) / NULLIF(s.rooms_sold, 0), 2)             AS adr,
       ROUND(COALESCE(s.room_revenue, 0) / h.rooms, 2)                             AS revpar
FROM dim_date d
CROSS JOIN dim_hotel h
LEFT JOIN sold s   ON s.hotel_id = h.hotel_id AND s.stay_date = d.date
LEFT JOIN denied x ON x.hotel_id = h.hotel_id AND x.stay_date = d.date;

CREATE INDEX ix_mart_daily ON mart_daily_hotel (stay_date, hotel_id);

-- Grain: one hotel for one calendar month.
DROP VIEW IF EXISTS mart_monthly_hotel;
CREATE VIEW mart_monthly_hotel AS
SELECT hotel_id,
       substr(stay_date, 1, 7)                         AS month,
       SUM(rooms_sold)                                 AS rooms_sold,
       SUM(capacity)                                   AS rooms_available,
       ROUND(SUM(room_revenue), 2)                     AS room_revenue,
       ROUND(1.0 * SUM(rooms_sold) / SUM(capacity), 4) AS occupancy,
       ROUND(SUM(room_revenue) / NULLIF(SUM(rooms_sold), 0), 2) AS adr,
       ROUND(SUM(room_revenue) / SUM(capacity), 2)     AS revpar
FROM mart_daily_hotel
GROUP BY hotel_id, substr(stay_date, 1, 7);

-- Grain: one segment and channel for one month (net of acquisition cost).
DROP VIEW IF EXISTS mart_mix_monthly;
CREATE VIEW mart_mix_monthly AS
SELECT substr(s.stay_date, 1, 7) AS month,
       b.segment,
       b.channel,
       SUM(s.rooms)                                   AS room_nights,
       ROUND(SUM(s.revenue), 2)                       AS room_revenue,
       ROUND(SUM(s.revenue * (1 - c.acquisition_cost)), 2) AS net_revenue
FROM fact_stay_night s
JOIN fact_booking b ON b.booking_id = s.booking_id
JOIN dim_channel c  ON c.channel = b.channel
WHERE s.status IN ('Checked out', 'Confirmed')
GROUP BY 1, 2, 3;
