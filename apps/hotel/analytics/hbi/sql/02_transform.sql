-- Clean staging data into the star schema.

INSERT INTO dim_hotel SELECT hotel_id, hotel_name, style, rooms, base_rate FROM stg_hotels;
INSERT INTO dim_segment SELECT segment, segment_name FROM stg_segments;
INSERT INTO dim_channel SELECT channel, channel_name, acquisition_cost FROM stg_channels;

INSERT INTO dim_date
SELECT date_key, date, year, month, day_of_week, day_name, season, is_weekend_night,
       NULLIF(holiday_ca, ''), NULLIF(holiday_us, ''), long_weekend,
       NULLIF(event, ''), NULLIF(event_type, '')
FROM stg_dates;

-- Missing revenue is rebuilt from rate x room nights and flagged, never silently filled.
INSERT INTO fact_booking
SELECT booking_id,
       hotel_id,
       date(booking_date),
       date(arrival_date),
       date(arrival_date, '+' || nights || ' days'),
       CAST(julianday(arrival_date) - julianday(date(booking_date)) AS INTEGER),
       nights,
       rooms,
       room_nights,
       segment,
       channel,
       rate,
       COALESCE(room_revenue, ROUND(rate * room_nights, 2)),
       CASE WHEN room_revenue IS NULL THEN 1 ELSE 0 END,
       status,
       date(cancel_date)
FROM stg_bookings;

-- Expand each booking into its stay nights with a recursive CTE.
INSERT INTO fact_stay_night
WITH RECURSIVE n(booking_id, k) AS (
    SELECT booking_id, 0 FROM fact_booking
    UNION ALL
    SELECT n.booking_id, n.k + 1
    FROM n JOIN fact_booking b ON b.booking_id = n.booking_id
    WHERE n.k + 1 < b.nights
)
SELECT b.booking_id,
       date(b.arrival_date, '+' || n.k || ' days'),
       b.hotel_id,
       b.rooms,
       ROUND(b.rate * b.rooms, 2),
       b.status,
       b.booking_date,
       b.cancel_date
FROM n JOIN fact_booking b ON b.booking_id = n.booking_id;

INSERT INTO fact_denied_night
WITH RECURSIVE n(request_id, k) AS (
    SELECT request_id, 0 FROM stg_denials
    UNION ALL
    SELECT n.request_id, n.k + 1
    FROM n JOIN stg_denials d ON d.request_id = n.request_id
    WHERE n.k + 1 < d.nights
)
SELECT d.request_id,
       date(d.arrival_date, '+' || n.k || ' days'),
       d.hotel_id,
       d.rooms,
       d.quoted_rate
FROM n JOIN stg_denials d ON d.request_id = n.request_id;

CREATE INDEX ix_stay_hotel_date ON fact_stay_night (hotel_id, stay_date);
CREATE INDEX ix_denied_hotel_date ON fact_denied_night (hotel_id, stay_date);
CREATE INDEX ix_booking_arrival ON fact_booking (hotel_id, arrival_date);
