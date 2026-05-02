with groups as (
    select
        coalesce(age_group, 'ALL AGES') as age_group,
        coalesce(gender, 'ALL') as gender,
        count(*) as customer_count,
        round(100.0 * count(*) / (select count(*) from customers_view), 2) as customer_share_pct
    from customers_view
    group by cube (age_group, gender)
)

select * from groups
where gender = 'ALL' or age_group = 'ALL AGES'
order by 1, 2 desc;