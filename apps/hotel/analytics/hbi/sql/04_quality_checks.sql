-- Each check returns one row: check name and number of failing records.
-- A non-zero count stops the build.

SELECT 'Duplicate booking ids' AS check_name,
       COUNT(*) - COUNT(DISTINCT booking_id) AS failures
FROM fact_booking
UNION ALL
SELECT 'Room nights not equal to nights x rooms',
       COUNT(*) FROM fact_booking WHERE room_nights <> nights * rooms
UNION ALL
SELECT 'Revenue not equal to rate x room nights (beyond 1 cent)',
       COUNT(*) FROM fact_booking WHERE ABS(room_revenue - rate * room_nights) > 0.01 * room_nights
UNION ALL
SELECT 'Unknown segment codes',
       COUNT(*) FROM fact_booking b LEFT JOIN dim_segment s USING (segment) WHERE s.segment IS NULL
UNION ALL
SELECT 'Unknown channel codes',
       COUNT(*) FROM fact_booking b LEFT JOIN dim_channel c USING (channel) WHERE c.channel IS NULL
UNION ALL
SELECT 'Stay-night rows not matching booking nights',
       ABS((SELECT SUM(nights) FROM fact_booking) - (SELECT COUNT(*) FROM fact_stay_night))
UNION ALL
SELECT 'Stay-night revenue not tying to booking revenue (dollars)',
       CAST(ABS((SELECT SUM(rate * room_nights) FROM fact_booking)
              - (SELECT SUM(revenue) FROM fact_stay_night)) > 1.0 AS INTEGER)
UNION ALL
SELECT 'Nights sold above capacity',
       COUNT(*) FROM mart_daily_hotel WHERE rooms_sold > capacity
UNION ALL
SELECT 'Cancelled bookings without a cancel date',
       COUNT(*) FROM fact_booking WHERE status = 'Cancelled' AND cancel_date IS NULL
UNION ALL
SELECT 'Bookings made after arrival',
       COUNT(*) FROM fact_booking WHERE booking_date > arrival_date;
