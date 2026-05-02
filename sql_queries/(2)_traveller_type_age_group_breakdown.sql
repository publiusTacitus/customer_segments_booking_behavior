with booking_stats as (
    select
        coalesce(traveller_type_id, 'ALL_TYPES') as traveller_type_id,
        coalesce(age_group, 'ALL_AGES') as age_group,
        round(100.0 * count(*) / (select count(*) from bookings), 2) as booking_share_pct,
        round(count(case when class_id != '(01) Economy' then 1 end) * 100.0 / count(*), 2) as premium_cabin_usage_pct,
        round(100.0 * count(case when is_checked_in = TRUE and has_cancellation_refund = FALSE then 1 end)
            / count(*) filter (where has_cancellation_refund = FALSE), 2) as avg_check_in_rate_pct,
        avg(flight_date::date - booking_time::date)::int as avg_bkg_lead_time_days,
        round(avg(price_paid / expd_avg_price), 2) as avg_final_to_base_price_ratio
    from bookings_view
    group by grouping sets ((traveller_type_id, age_group), age_group, ())
),

customer_stats as (
    select
        coalesce(traveller_type_id, 'ALL_TYPES') as traveller_type_id,
        coalesce(age_group, 'ALL_AGES') as age_group,
        round(100.0 * count(*) / (select count(*) from customers), 2) as customer_share_pct,
        round(100.0 * count(*) filter (where gender = 'Female') / count(*), 2) as female_ratio_pct,
        round(100.0 * count(*) filter (where gender = 'Male') / count(*), 2) as male_ratio_pct
    from customers_view
    group by grouping sets ((traveller_type_id, age_group), age_group, ())
)

select
    cs.traveller_type_id,
    cs.age_group,
    cs.customer_share_pct,
    cs.female_ratio_pct,
    cs.male_ratio_pct,
    bs.booking_share_pct,
    bs.premium_cabin_usage_pct,
    bs.avg_check_in_rate_pct,
    bs.avg_bkg_lead_time_days,
    bs.avg_final_to_base_price_ratio
from customer_stats cs
join booking_stats bs using (traveller_type_id, age_group)
order by 1, 2;