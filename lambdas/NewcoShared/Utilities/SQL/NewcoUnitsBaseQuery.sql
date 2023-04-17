with  
  /*
  this is the base item that is most restrictive, id = a property_id value restricting all other queries to the one property being reported
  */
prop_select as (
select
  *
from
  properties
where
  disposition_date is null
  and `status` <> 'Archive'
  and properties.id = :newco_property_id
  ),
  /*
  pricing_info gets market_rent value from the base_market_rent of the unit type and then adds in all of the costs of amenities for the particular unit.
  */
pricing_info as (
select
  unit_ids,
  o_val + market_rent_unit_type as unit_market_rent_old,
  a_val + market_rent_unit_type as unit_market_rent
from
  (
  select
   units.id unit_ids,
  /* amenities.id as amenities_id, amenities_property.id as amenities_property_id, */
   coalesce(sum(coalesce(amenities_property.`value`, amenities.`value`)), 0) as a_val,
   coalesce(sum(amenities.`value`), 0) as o_val,
   unit_types.market_rent_unit_type
  from
   prop_select
  join units on
   units.property_id = prop_select.id
   and units.deleted_at is null
  join unit_types on
   units.unit_type_id = unit_types.id
   and unit_types.deleted_at is null 
  /* and unit_types.property_id = prop_select.id */
  left join amenities_unit on
   units.id = amenities_unit.unit_id
   and amenities_unit.property_id = prop_select.id
  left join amenities on
   amenities_unit.amenities_id = amenities.id
  left join amenities_property on
   amenities_property.amenities_id = amenities.id
   and amenities_property.property_id = prop_select.id
  group by
   unit_ids,
   market_rent_unit_type
  )d
  )
  /*
  moving_info : for each unit in the selected property, moving_info gets event_notifications for three situations ... move in, move out (actual) and move out (notice to vacate)
  note : be careful to either process this query as a literal string, or to further escape the double-slash characters found in three places within this query
  */,
moving_info as (
select
   distinct
   re_in.resident_id,
   prop_select.id as property_id,
   date(mie.movein_date) movein_date,
   date(move_out_info.moveout_date) moveout_date,
   date(notice_info.estimated_moveout_date) estimated_moveout_date,
   re_in.eventable_id as in_event_id,
   move_out_info.eventable_id as out_event_id
from
   prop_select
join resident_events re_in on
   prop_select.id = re_in.property_id
   and re_in.deleted_at is null
   and re_in.eventable_type = 'App\\\\MoveInEvent'
join move_in_events mie 
   on re_in.eventable_id = mie.id_move_in_events
   and mie.canceled_date is null
   and mie.deleted_at is null
   and mie.movein_date is not null
left join 
  (
  select
    distinct
    re_out.*,
    moe.moveout_date
  from
    prop_select
  join resident_events re_out 
    on prop_select.id = re_out.property_id
    and re_out.deleted_at is null
    and re_out.eventable_type = 'App\\\\MoveOutEvent'
  join move_out_events moe on
    re_out.eventable_id = moe.id_move_out_events
    and moe.deleted_at is null
  ) move_out_info on
    prop_select.id = move_out_info.property_id
    and re_in.resident_id = move_out_info.resident_id
left join 
  (select
   distinct
    re.*,
   ne.estimated_moveout_date
  from
   prop_select
  join resident_events re 
   on prop_select.id = re.property_id
   and re.deleted_at is null
   and re.eventable_type = 'App\\\\NoticeEvent'
  join notice_events ne on
   re.eventable_id = ne.id_notice_events
   and ne.deleted_at is null
  ) notice_info on
   prop_select.id = notice_info.property_id
   and re_in.resident_id = notice_info.resident_id 
  )
  /*
  unit_move_info uses window function to consolidate information from move in, move out, and notice to vacate events (above) and report only most current value
  */,
unit_move_info as (
select
   prop_select.id as prop_id,
   prop_select.`name` as prop_name,
   unit_id ,
   moving_info.resident_id,
   moving_info.movein_date,
   coalesce(moving_info.moveout_date, moving_info.estimated_moveout_date) as moveout_date,
   lead (movein_date) over (partition by prop_select.id,
   unit_id
order by
   movein_date) as next_movein_date
from
   prop_select
inner join residents on
   residents.property_id = prop_select.id
   and residents.deleted_at is null
left join moving_info on
   prop_select.id = moving_info.property_id
   and moving_info.resident_id = residents.id
order by
   movein_date desc
  )
  /*
  unit_move_info_all restricts results to the first row of information
  */,
unit_move_info_all as (
select
   prop_id,
   prop_name,
   unit_id ,
   unit_market_rent,
   resident_id,
   movein_date,
   moveout_date,
  case
   when next_movein_date = movein_date then null
   else next_movein_date
   end as next_movein_date,
row_number() over (partition by prop_id,
   unit_id
order by
   movein_date desc) as rn
from
   prop_select
join unit_move_info umi on
   umi.prop_id = prop_select.id
join pricing_info pi on
   pi.unit_ids = umi.unit_id 
  /* and movein_date < curdate() */
where
  (movein_date < moveout_date
  or moveout_date is null)
  )
  /*
  unit_move_info_calc considers the information provided from above and adds calculated 'available' value after removing ineligible units, preleased vacant units, and preleased occupied units
  */,
unit_move_info_calc as (
select
   prop_select.id as prop_id,
   prop_select.`name` as prop_name,
   units.`name` as unit_number,
   units.`status` as unit_status,
   units.id as unit_id,
   resident_id,
   umia.movein_date,
   umia.moveout_date  ,
   umia.next_movein_date,
  case
  when units.`status` in ('Vacant - Leased', 'Rented')
  or
  /* the unit has no moving info but someone resides there. */
   (movein_date is null
   and moveout_date is null
   and next_movein_date is null
   and resident_id is not null)
  or
  /* they've moved in but haven't moved out yet (or given notice to vacate). */
  (
  moveout_date is null
  and movein_date is not null
  )
  or 
  /* the unit is a bad unit */
  (units.status is not null
  and units.`status` in ('', 'Inactive', 'Demo', 'Model', 'Shop', 'Down', 'Rehab', 'Pending Approval'))
  or 
  /* the unit's available date has been manually set to sometime beyond 60 days */
  units.available_date > date_add(curdate(), interval 60 day)
    or
  (
  (
  /* they've already moved out */
    moveout_date < curdate()
    or 
  /* they will move out in less than 60 days */
    date_add(curdate(), interval 60 day) > moveout_date
  )
    and (
  /* someone is moving in and will do so anytime in the NEXT 365 days */
    next_movein_date is not null
    and (next_movein_date <> move_out_date
    and next_movein_date < date_add(curdate(), interval 365 day))
  ) 
  )
  then 0
    else 1
  end as available,
  `units`.`name`,
  `units`.`unit_type_id`,
  `units`.`unit_label`,
  `units`.`square_feet`,
  `units`.`floor`,
  `units`.`bedrooms`,
  `units`.`bathrooms`,
  `units`.`building_id`,
  `units`.`amenity_group`,
  `units`.`rent_amount`,
  `units`.`notes`,
  `units`.`created_at`,
  `units`.`updated_at`,
  `units`.`deleted_at`,
  `units`.`market_rent_amount`,
  `units`.`leasable`,
  `units`.`ready_to_show`,
  `units`.`move_in_date`,
  `units`.`move_out_date`,
  `units`.`available_date`,
  `units`.`vacate_date`,
  `units`.`verified_date`,
  `units`.`verified_by`
  from
   prop_select
  join units on
   units.property_id = prop_select.id
   and units.deleted_at is null
  left join unit_move_info_all umia on
   units.id = umia.unit_id
   and rn = 1
   and units.status not in ('', 'Inactive', 'Demo', 'Model', 'Shop', 'Down', 'Rehab') 
  )
  /*
  grabs applicant information to ensure that units in the process of being leased will not be included in availability (regardless of status updates) because Cat says we can't trust statuses.
  */,
applicant_info as (
select
   prop_select.id as prop_id,
   umia.unit_id as app_unit,
   1 as applying
from
   prop_select
join unit_move_info_all umia on
   umia.prop_id = prop_select.id
join unit_leases on
   unit_leases.resident_id = umia.resident_id
   and unit_leases.unit_id = umia.unit_id
join applicants on
   prop_select.id = applicants.property_id
   and applicants.unit_id = umia.unit_id
   and applicants.status in( 'active', 'moved in')
   and applicants.deleted_at is null
join persons on
  applicants.person_id = persons.id
  where
   applicants.id is not null
   and (applicants.status = 'active'
   or (applicants.status = 'moved in'
   and (persons.move_in_date >= curdate())
    and (persons.move_in_date < date_add(curdate(), interval 60 day))))
  group by
   prop_id,
   app_unit
  )
  /*
  unit_report_all gets information on all units of the property
  */,
unit_report_all as (
select
   prop_select.id as prop_id,
   prop_select.`name` as prop_name,
   umic.`name` as unit_number,
   buildings.`name` as building,
   `floor`,
   umic.available,
   umic.unit_status
  /* , case when available_date <= curdate() then curdate() else umic.available_date end as avldt */
  ,
  case
  when available = 1
   and available_date <= curdate() then curdate()
  when available = 0
   and available_date <= curdate() then null
  when unit_status = 'Pending Approval' then null
  else available_date
  end as available_date,
   umic.bedrooms as beds,
   umic.bathrooms as baths,
   umic.unit_id,
   unit_types.`name` as unit_type_name ,
   umic.square_feet as sqft_actual,
   unit_market_rent,
   min(unit_market_rent) over (partition by umic.prop_id,
   unit_types.`name`) as unit_market_rent_all,
  case
  when unit_types.`description` is null then case
  when umic.bedrooms = 0 then 'Studio'
  else concat(trim(umic.bedrooms)+ 0, 'x', trim(umic.bathrooms)+ 0)
  end
  else unit_types.`description`
  end as unit_type_desc,
   min(umic.square_feet) over (partition by umic.prop_id,
   unit_types.`name`) as sqft_min_all,
   max(umic.square_feet) over (partition by umic.prop_id,
   unit_types.`name`) as sqft_max_all,
   trim(unit_types.square_feet)+ 0 as sqft_model_base,
  case
  when nullif(website_floorplans.image, '') is not null then concat('https://madera-newco.s3.us-west-2.amazonaws.com/', website_floorplans.image)
  else null
  end as `floorplan`,
   websites.url `website`,
  case
  when website_floorplans.virtual_tour_url not in (null,
  'undefined') then website_floorplans.virtual_tour_url
  end as virtual_tour_url
  from
   prop_select
  left join unit_move_info_calc umic on
   umic.prop_id = prop_select.id
  join unit_types on
   unit_types.id = umic.unit_type_id 
  /* and unit_types.property_id = prop_select.id */
  join pricing_info on
   pricing_info.unit_ids = umic.unit_id
  left join buildings on
   buildings.id = building_id
  left join website_floorplans on
   website_floorplans.unit_type_id = unit_types.id
  left join websites on
   websites.property_id = prop_select.id
  where
   prop_id is not null 
  )
  /*
  unit_report_avail gives us the squarefootage values with pricing information for the available units only, grouped by unit_type.
  */,
unit_report_avail as (
select
   umic.prop_id,
   umic.unit_id,
   umic.`name` as unit_number,
   unit_types.`name` as unit_type_name,
   available,
   unit_status,
   unit_market_rent,
   min(unit_market_rent) over (partition by prop_id,
   unit_types.`name`) as unit_market_rent_avail,
   trim(umic.bedrooms)+ 0 as beds,
   trim(umic.bathrooms)+ 0 as baths,
   min(umic.square_feet) over (partition by prop_id,
   unit_types.`name`) as sqft_min_avail,
   max(umic.square_feet) over (partition by prop_id,
   unit_types.`name`) as sqft_max_avail
from
   prop_select
join unit_move_info_calc umic on
   umic.prop_id = prop_select.id
join unit_types on
   unit_types.property_id = prop_select.id
   and unit_types.id = umic.unit_type_id
   and umic.unit_status <> 'Pending Approval'
join pricing_info on
   umic.unit_id = pricing_info.unit_ids
left join applicant_info ai on
   ai.prop_id = prop_select.id
   and ai.app_unit = umic.unit_id
where
   prop_select.id is not null
   and available = 1
   and applying is null
  )
  /*
  unit_report_consolidated joins unit_report_all and unit_report_avail to combine all the relevant information that will be needed for the grouping summary provided below.
  unit_report_consolidated is the units_level report
  */,
unit_report_consolidated as (
select
   ura1.prop_id,
   ura1.prop_name,
   ura1.unit_id,
   ura1.`floor`,
   ura1.building,
   ura1.unit_number,
   ura1.unit_status,
   ura1.unit_type_name as model_type,
   ura1.unit_type_name,
   ura1.unit_type_desc,
   ura1.available,
   ura1.available_date,
   trim(ura1.beds)+ 0 as beds,
   trim(ura1.baths)+ 0 as baths,
   ura1.sqft_min_all,
   ura1.sqft_max_all,
   ura1.sqft_model_base,
   ura2.sqft_min_avail,
   ura2.sqft_max_avail,
   ura1.sqft_actual,
   ura1.unit_market_rent_all,
   min(ura2.unit_market_rent) over (partition by prop_id,
   ura1.unit_type_name) as unit_market_rent_avail,
   ura1.unit_market_rent,
   ura1.floorplan,
   ura1.website,
   ura1.virtual_tour_url
from
   unit_report_all ura1
left join unit_report_avail ura2 
  on
   ura1.prop_id = ura2.prop_id
   and ura1.unit_id = ura2.unit_id
  )
  /*
  unit_type_data_complete groups the unit information and produces the final model-level data.
  */,
unit_type_data_complete as (
select
   prop_id as prop_id2,
   prop_name as prop_name2,
   unit_type_name as model_type,
   unit_type_name as unit_type_name2,
   count(unit_id) as total_units,
   sum(available) as available2,
   min(available_date) as unit_type_first_avail,
   min(unit_market_rent_all) as unit_market_rent_all2,
   min(unit_market_rent_avail) as unit_market_rent_avail2,
   sqft_model_base as sqft_model_base2,
   min(sqft_min_all) as sqft_min_all2,
   max(sqft_max_all) as sqft_max_all2,
   min(sqft_min_avail) as sqft_min_avail2,
   max(sqft_max_avail) as sqft_max_avail2,
   unit_type_desc as unit_type_desc2,
   floorplan as floorplan2,
   website as website2,
   virtual_tour_url as virtual_tour_url2,
   beds as beds2,
   baths as baths2
from
   unit_report_consolidated
group by
   unit_report_consolidated.prop_id,
   unit_report_consolidated.unit_type_name,
   unit_report_consolidated.floorplan
)
