
with nationalities as (
    select
        c.customer_id,
        (select count(distinct customer_id) from bookings) as total_customers_overall,
        count(*) over () as total_bookings_overall,
        c.nationality
    from bookings b
    join customers c using (customer_id)
),

daily_flights as (
    select distinct
        ap.country,
        (
            (sum(r.flights_per_day) filter (where r.departure_airport_code = ap.airport_code)
                over (partition by ap.country) +
             sum(r.flights_per_day) filter (where r.arrival_airport_code = ap.airport_code)
                over (partition by ap.country)) * 100.0 /
            (sum(r.flights_per_day) filter (where r.departure_airport_code = ap.airport_code) over () +
             sum(r.flights_per_day) filter (where r.arrival_airport_code = ap.airport_code) over ())
        )
          as daily_flights_pct
    from routes r
    join airports ap on r.departure_airport_code = ap.airport_code or r.arrival_airport_code = ap.airport_code
)
select
    coalesce(n.nationality, 'OVERALL') as country,
    count(distinct n.customer_id) as total_customers,
    round(100.0 * count(distinct n.customer_id) / nullif(max(n.total_customers_overall), 0), 2) as customer_share_pct,
    count(*) as total_bookings,
    round(100.0 * count(*) / nullif(max(n.total_bookings_overall), 0), 2) as booking_share_pct,
    case when grouping(n.nationality) = 0 then round(max(df.daily_flights_pct), 2) end
        as share_of_daily_flights_to_or_from_ctry_pct
from nationalities n
left join daily_flights df on n.nationality = df.country
group by cube(n.nationality)
order by n.nationality nulls last;