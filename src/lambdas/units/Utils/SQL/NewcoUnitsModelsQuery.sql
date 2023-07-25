/*
Final select statement for unit_level (model) type reports.
*/
, 
report_final_unit_type as (
  select 
    prop_id2 as property_id, 
    prop_name2 as property_name, 
    unit_type_name2 as model_type, 
    unit_type_name2 as unit_type_name, 
    unit_type_desc2 as unit_type_desc, 
    trim(beds2)+ 0 as beds, 
    trim(baths2)+ 0 as baths, 
    total_units, 
    CONVERT (available2, UNSIGNED) as available, 
    unit_type_first_avail, 
    unit_market_rent_all2 as unit_market_rent_all, 
    unit_market_rent_avail2 as unit_market_rent_avail, 
    coalesce(
      unit_market_rent_avail2, unit_market_rent_all2
    ) as market_rent, 
    convert (sqft_model_base2, UNSIGNED) as sqft_model_base, 
    convert (sqft_model_base2, UNSIGNED) as sqft, 
    convert (sqft_min_all2, UNSIGNED) as sqft_min_all, 
    convert (
      max(sqft_max_all2), 
      UNSIGNED
    ) as sqft_max_all, 
    convert (sqft_min_avail2, UNSIGNED) as sqft_min_avail, 
    convert (sqft_max_avail2, UNSIGNED) as sqft_max_avail, 
    convert (
      coalesce(sqft_min_avail2, sqft_min_all2), 
      UNSIGNED
    ) as sqft_min_report, 
    convert (
      coalesce(sqft_max_avail2, sqft_max_all2), 
      UNSIGNED
    ) as sqft_max_report, 
    case when coalesce(sqft_min_avail2, sqft_min_all2) <> coalesce(sqft_max_avail2, sqft_max_all2) then concat(
      coalesce(sqft_min_avail2, sqft_min_all2), 
      '-', 
      coalesce(sqft_max_avail2, sqft_max_all2)
    ) else coalesce(sqft_min_avail2, sqft_min_all2) end as sqft_range, 
    website2 as website, 
    virtual_tour_url2 as virtual_tour_url, 
    virtual_tour_url2 as virtual_tour, 
    floorplan2 as floorplan, 
    case when floorplan2 is not null then concat(
      'Scaled diagram of floor plan depicting the typical ', 
      unit_type_name2, 
      ' (', 
      unit_type_desc2, 
      ') unit at ', 
      prop_name2, 
      ' community, as viewed from above. Image provides the layout of ', 
      case when beds2 is null 
      or beds2 = 0 then '' else concat(
        trim(beds2)+ 0, 
        ' bedroom', 
        case when beds2 > 1 then 's' else '' end, 
        ' and '
      ) end, 
      trim(baths2)+ 0, 
      ' bathroom', 
      case when baths2 > 1 then 's' else '' end, 
      ' relative to walls, doors, windows, and other substantial fixed features in approximately ', 
      coalesce(sqft_min_avail2, sqft_min_all2), 
      '-', 
      coalesce(sqft_max_avail2, sqft_max_all2), 
      ' square feet (', 
      round(
        coalesce(sqft_min_avail2, sqft_min_all2)/ 10.764, 
        1
      ), 
      '-', 
      round(
        coalesce(sqft_max_avail2, sqft_max_all2)/ 10.764, 
        1
      ), 
      ' square meters) of total living space.'
    ) else null end as floorplan_alt_text 
  from 
    unit_type_data_complete 
  group by 
    unit_type_data_complete.prop_id2, 
    unit_type_data_complete.unit_type_name2, 
    unit_type_data_complete.floorplan2
) 
select 
  * 
from 
  report_final_unit_type
