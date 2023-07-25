, 
report_unit as (
  select 
    urc1.*, 
    unit_type_first_avail 
  from 
    unit_report_consolidated urc1 
    left join unit_type_data_complete urc2 on urc1.unit_type_name = urc2.unit_type_name2 
    and urc1.prop_id = urc2.prop_id2
), 
report_final_unit as (
  select 
    prop_id as property_id, 
    prop_name as property_name, 
    building, 
    `floor`, 
    unit_id, 
    unit_number, 
    case when available = 0 then 'false' when available = 1 then 'true' else null end as available_boolean, 
    CONVERT (available, UNSIGNED) as is_available, 
    1 * available as available, 
    available_date, 
    unit_status, 
    model_type, 
    unit_type_name, 
    unit_type_desc, 
    beds, 
    baths, 
    unit_market_rent as market_rent, 
    unit_market_rent as market_rent_amount, 
    CONVERT (sqft_actual, UNSIGNED) as sqft 
  from 
    report_unit
) 
select 
  * 
from 
  report_final_unit
