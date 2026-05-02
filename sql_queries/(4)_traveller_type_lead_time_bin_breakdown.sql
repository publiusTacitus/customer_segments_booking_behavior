
with lead_time_bins as (
    select
        traveller_type_id,
        (flight_date::date - booking_time::date) as booking_lead_time_days,
        case
            when (flight_date::date - booking_time::date) <= 3 then '(1) <= 3 days'
            when (flight_date::date - booking_time::date) <= 7 then '(2) <= 7 days'
            when (flight_date::date - booking_time::date) <= 14 then '(3) <= 14 days'
            when (flight_date::date - booking_time::date) <= 30 then '(4) <= 30 days'
            when (flight_date::date - booking_time::date) <= 60 then '(5) <= 60 days'
            else '(6) > 60 days'
        end as lead_time_bin,
        count(*) over () as total_bookings,
        case when class_id != '(01) Economy' then 1 end as premium_cabin,
        price_paid / expd_avg_price as final_to_base_price_ratio,
        case when price_paid > expd_avg_price then 1 end as above_base_price,
        case when price_paid < expd_avg_price then 1 end as below_base_price
    from bookings_view
)

select
    coalesce(traveller_type_id, 'ALL_TYPES') as traveller_type_id,
    coalesce(lead_time_bin, 'ALL_BINS') as lead_time_bin,
    round(100.0 * count(*) / max(total_bookings), 3) as booking_share_pct,
    round(100.0 * count(premium_cabin) / count(*), 2) as premium_cabin_usage_pct,
    avg(booking_lead_time_days)::int as avg_bkg_lead_time_days,
    round(avg(final_to_base_price_ratio), 2) as avg_final_to_base_price_ratio,
    round(percentile_cont(0.5) within group (order by final_to_base_price_ratio)::decimal, 2)
        as median_final_to_base_price_ratio,
    round(100.0 * count(above_base_price) / count(*), 2) as share_above_base_price_pct,
    round(100.0 * count(below_base_price) / count(*), 2) as share_below_base_price_pct
from lead_time_bins
group by grouping sets ((traveller_type_id, lead_time_bin), lead_time_bin, ())
order by 1, 2;