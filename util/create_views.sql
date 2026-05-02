create view customers_view as (

    with reference_date as (
        select least(max(booking_time), current_date) as ref_date
        from bookings
    ),

    ages as (
    select *,
           date_part('year', age(ref_date, date_of_birth))::int as age_canonical
    from customers
    cross join reference_date ry
    )

    select *,
           case
               when age_canonical < 18 then 'Age <18'
               when age_canonical < 25 then 'Age 18–24'
               when age_canonical < 35 then 'Age 25–34'
               when age_canonical < 45 then 'Age 35–44'
               when age_canonical < 61 then 'Age 45–60'
               else 'Age 61+'
           end as age_group
    from ages

);


create view bookings_view as (

    with add_columns as (
        select
            b.booking_id,
            count(*) over (partition by customer_id) as bookings_per_customer,
            c.traveller_type_id,
            c.age_group,
            case
                when b.class_id = '(02) Business' then r.expd_avg_price_business
                when b.class_id = '(03) First' then r.expd_avg_price_first
                else r.expd_avg_price_economy
            end as expd_avg_price
        from bookings b
        join customers_view c using (customer_id)
        join flights f using (flight_number)
        join routes r using (line_number)
    )

    select * from bookings join add_columns using (booking_id)

);
