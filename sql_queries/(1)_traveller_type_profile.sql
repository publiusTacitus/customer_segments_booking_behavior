with booking_stats as (
    select
        coalesce(traveller_type_id, 'OVERALL') as traveller_type_id,
        round(100.0 * count(*) / (select count(*) from bookings), 2) as booking_share_pct,
        round(avg(bookings_per_customer) / ((max(flight_date) - min(flight_date)) / 365.25), 2)
            as avg_yrly_bkgs_per_cust,
        round(count(case when class_id != '(01) Economy' then 1 end) * 100.0 / count(*), 2) as premium_cabin_usage_pct,
        round(100.0 * count(case when is_checked_in = TRUE and has_cancellation_refund = FALSE then 1 end)
            / count(*) filter (where has_cancellation_refund = FALSE), 2) as avg_check_in_rate_pct,
        avg(flight_date::date - booking_time::date)::int as avg_bkg_lead_time_days,
        round(avg(price_paid / expd_avg_price), 2) as avg_final_to_base_price_ratio
    from bookings_view
    group by cube (traveller_type_id)
),

status_counts as (
    select
        coalesce(traveller_type_id, 'OVERALL') as traveller_type_id,
        frequent_flyer_status_id,
        count(*) as cnt
    from customers
    group by grouping sets ((traveller_type_id, frequent_flyer_status_id), (frequent_flyer_status_id))
),

status_dist as (
    select
        *,
        row_number() over (partition by traveller_type_id order by cnt desc) as rn
    from status_counts
),

status_summary as (
    select
        traveller_type_id,
        max(frequent_flyer_status_id) filter (where rn = 1) as dominant_loyalty_status,
        max(frequent_flyer_status_id) filter (where rn = 2) as secondary_loyalty_status
    from status_dist
    group by 1
),

customer_stats as (
    select
        coalesce(c.traveller_type_id, 'OVERALL') as traveller_type_id,
        round(100.0 * count(*) / (select count(*) from customers), 2) as customer_share_pct,
        round(100.0 * count(*) filter (where gender = 'Female') / count(*), 2) as female_ratio_pct,
        percentile_cont(0.5) within group (order by c.age_canonical) as median_age
    from customers_view c
    group by cube (c.traveller_type_id)
)

select
    cs.traveller_type_id,
    ss.dominant_loyalty_status,
    ss.secondary_loyalty_status,
    cs.customer_share_pct,
    cs.female_ratio_pct,
    bs.booking_share_pct,
    bs.avg_yrly_bkgs_per_cust,
    cs.median_age,
    bs.premium_cabin_usage_pct,
    bs.avg_check_in_rate_pct,
    bs.avg_bkg_lead_time_days,
    bs.avg_final_to_base_price_ratio
from customer_stats cs
join booking_stats bs using (traveller_type_id)
join status_summary ss using (traveller_type_id)
order by 1;