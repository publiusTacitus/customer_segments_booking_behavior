
select
    coalesce(c.age_group, 'ALL AGES') as age_group,
    coalesce(c.gender, 'OVERALL') as gender,
    round(100.0 * count(case when b.class_id = '(01) Economy' then 1 end) / count(*), 2)
        as economy_class_share_pct,
    round(100.0 * count(case when b.class_id = '(02) Business' then 1 end)  / count(*), 2)
        as business_class_share_pct,
    round(100.0 * count(case when b.class_id = '(03) First' then 1 end)  / count(*), 2)
        as first_class_share_pct,
    round(100.0 * count(case when is_checked_in = TRUE and has_cancellation_refund = FALSE then 1 end)
            / count(*) filter (where has_cancellation_refund = FALSE), 2) as avg_check_in_rate_pct
from bookings b
join customers_view c using (customer_id)
group by grouping sets ((c.age_group, c.gender), c.gender, ())
order by 1, 2;