# Newco base query
newco_units_base_query = """
WITH
/*
this is the base item that is most restrictive, id = a property_id value restricting all other queries to the one property being reported
*/
prop_select AS
(
       SELECT *
       FROM   properties
       WHERE  disposition_date IS NULL
       AND    `status` <> 'Archive'
       AND    properties.id = :newco_property_id )
/*
pricing_info gets market_rent value from the base_market_rent of the unit type and then adds in all of the costs of amenities for the particular unit.
*/

, pricing_info as 	(
              select
              unit_ids,
              o_val+market_rent_unit_type                                                  as unit_market_rent_old,
              a_val+market_rent_unit_type                                                  as unit_market_rent
              from
              (
              select
              units.id                                                                     as unit_ids,
              /* amenities.id                                                                 as amenities_id, */
              /* amenities_property.id                                                        as amenities_property_id, */
              coalesce(sum(coalesce(amenities_property.`value`, amenities.`value`)),0)     as a_val,
              coalesce(sum(amenities.`value`),0)                                           as o_val,
              unit_types.market_rent_unit_type
              from
              prop_select join units on units.property_id = prop_select.id and units.deleted_at is null 
              join unit_types on units.unit_type_id = unit_types.id and unit_types.deleted_at is null 
              /* and unit_types.property_id = prop_select.id */
              left join amenities_unit on units.id = amenities_unit.unit_id and amenities_unit.property_id = prop_select.id
              left join amenities on amenities_unit.amenities_id = amenities.id
              left join amenities_property on amenities_property.amenities_id = amenities.id and amenities_property.property_id = prop_select.id
              group by unit_ids,market_rent_unit_type
              )d)

/*
moving_info : for each unit in the selected property, moving_info gets event_notifications for three situations ... move in, move out (actual) and move out (notice to vacate)
note : be careful to either process this query as a literal string, or to further escape the double-slash characters found in three places within this query
*/
, moving_info AS
(
                SELECT DISTINCT re_in.resident_id ,
                                prop_select.id                           AS property_id ,
                                date(mie.movein_date)                       movein_date ,
                                date(move_out_info.moveout_date)            moveout_date ,
                                date(notice_info.estimated_moveout_date)    estimated_moveout_date ,
                                re_in.eventable_id                       AS in_event_id ,
                                move_out_info.eventable_id               AS out_event_id
                FROM            prop_select
                JOIN            resident_events re_in
                ON              prop_select.id = re_in.property_id
                AND             re_in.deleted_at IS NULL
                AND             re_in.eventable_type = 'App\\\\MoveInEvent'
                JOIN            move_in_events mie
                ON              re_in.eventable_id = mie.id_move_in_events
                AND             mie.canceled_date IS NULL
                AND             mie.deleted_at IS NULL
                AND             mie.movein_date IS NOT NULL
                LEFT JOIN
                                (
                                                SELECT DISTINCT re_out.*,
                                                                moe.moveout_date
                                                FROM            prop_select
                                                JOIN            resident_events re_out
                                                ON              prop_select.id = re_out.property_id
                                                AND             re_out.deleted_at IS NULL
                                                AND             re_out.eventable_type = 'App\\\\MoveOutEvent'
                                                JOIN            move_out_events moe
                                                ON              re_out.eventable_id = moe.id_move_out_events
                                                AND             moe.deleted_at IS NULL ) move_out_info
                ON              prop_select.id = move_out_info.property_id
                AND             re_in.resident_id = move_out_info.resident_id
                LEFT JOIN
                                (
                                                SELECT DISTINCT re.*,
                                                                ne.estimated_moveout_date
                                                FROM            prop_select
                                                JOIN            resident_events re
                                                ON              prop_select.id = re.property_id
                                                AND             re.deleted_at IS NULL
                                                AND             re.eventable_type = 'App\\\\NoticeEvent'
                                                JOIN            notice_events ne
                                                ON              re.eventable_id = ne.id_notice_events
                                                AND             ne.deleted_at IS NULL ) notice_info
                ON              prop_select.id = notice_info.property_id
                AND             re_in.resident_id = notice_info.resident_id )
/*
unit_move_info uses window function to consolidate information from move in, move out, and notice to vacate events (above) and report only most current value
*/
, unit_move_info AS
(
           SELECT     prop_select.id     AS prop_id ,
                      prop_select.`NAME` AS prop_name ,
                      unit_id ,
                      moving_info.resident_id ,
                      moving_info.movein_date ,
                      COALESCE(moving_info.moveout_date,moving_info.estimated_moveout_date)               AS moveout_date ,
                      lead (movein_date) OVER (partition BY prop_select.id, unit_id ORDER BY movein_date) AS next_movein_date
           FROM       prop_select
           INNER JOIN residents
           ON         residents.property_id = prop_select.id
           AND        residents.deleted_at IS NULL
           LEFT JOIN  moving_info
           ON         prop_select.id = moving_info.property_id
           AND        moving_info.resident_id = residents.id
           ORDER BY   movein_date DESC )
/*
unit_move_info_all restricts results to the first row of information
*/
, unit_move_info_all AS
(
         SELECT   prop_id,
                  prop_name ,
                  unit_id ,
                  unit_market_rent ,
                  resident_id ,
                  movein_date ,
                  moveout_date ,
                  CASE
                           WHEN next_movein_date = movein_date THEN NULL
                           ELSE next_movein_date
                  END                                                                         AS next_movein_date ,
                  row_number() OVER (partition BY prop_id, unit_id ORDER BY movein_date DESC) AS rn
         FROM     prop_select
         JOIN     unit_move_info umi
         ON       umi.prop_id = prop_select.id
         JOIN     pricing_info pi
         ON       pi.unit_ids = umi.unit_id -- and movein_date < curdate()
         WHERE    (
                           movein_date < moveout_date
                  OR       moveout_date IS NULL) )
/*
unit_move_info_calc considers the information provided from above and adds calculated 'available' value after removing ineligible units, preleased vacant units, and preleased occupied units
*/
, unit_move_info_calc AS
(
          SELECT    prop_select.id     AS prop_id,
                    prop_select.`NAME` AS prop_name,
                    units.`NAME`       AS unit_number,
                    units.`status`     AS unit_status,
                    units.id           AS unit_id,
                    resident_id,
                    umia.movein_date,
                    umia.moveout_date ,
                    umia.next_movein_date ,
                    CASE
                              WHEN units.`status` IN ('Vacant - Leased',
                                                      'Rented')
                              OR
                                        /* the unit has no moving info but someone resides there. */
                                        (
                                                  movein_date IS NULL
                                        AND       moveout_date IS NULL
                                        AND       next_movein_date IS NULL
                                        AND       resident_id IS NOT NULL)
                              OR
                                        /* they've moved in but haven't moved out yet (or given notice to vacate). */
                                        (
                                                  moveout_date IS NULL
                                        AND       movein_date IS NOT NULL )
                              OR
                                        /* the unit is a bad unit */
                                        (
                                                  units.status IS NOT NULL
                                        AND       units.`status` IN ('',
                                                                     'Inactive',
                                                                     'Demo',
                                                                     'Model',
                                                                     'Shop',
                                                                     'Down',
                                                                     'Rehab',
                                                                     'Pending Approval'))
                              OR
                                        /* the unit's available date has been manually set to sometime beyond 60 days */
                                        units.available_date > date_add(curdate(), interval 60 day)
                              OR        (
                                                  (
                                                            /* they've already moved out */
                                                            moveout_date < curdate()
                                                  OR
                                                            /* they will move out in less than 60 days */
                                                            date_add(curdate(), interval 60 day) > moveout_date )
                                        AND       (
                                                            /* someone is moving in and will do so anytime in the NEXT 365 days */
                                                            next_movein_date is not null and (next_movein_date <> move_out_date and next_movein_date < date_add(curdate(), interval 365 day)) ) ) THEN 0
                              ELSE 1
                    END AS available ,
                    `units`.`NAME`,
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
          FROM      prop_select
          JOIN      units
          ON        units.property_id = prop_select.id
          AND       units.deleted_at IS NULL
          LEFT JOIN unit_move_info_all umia
          ON        units.id = umia.unit_id
          AND       rn = 1
          AND       units.status NOT IN ('',
                                         'Inactive',
                                         'Demo',
                                         'Model',
                                         'Shop',
                                         'Down',
                                         'Rehab') )
/*
grabs applicant information to ensure that units in the process of being leased will not be included in availability (regardless of status updates) because Cat says we can't trust statuses.
*/
, applicant_info AS
(
         SELECT   prop_select.id AS prop_id,
                  umia.unit_id   AS app_unit,
                  1              AS applying
         FROM     prop_select
         JOIN     unit_move_info_all umia
         ON       umia.prop_id = prop_select.id
         JOIN     unit_leases
         ON       unit_leases.resident_id = umia.resident_id
         AND      unit_leases.unit_id = umia.unit_id
         JOIN     applicants
         ON       prop_select.id = applicants.property_id
         AND      applicants.unit_id = umia.unit_id
         AND      applicants.status IN( 'active',
                                       'moved in')
         AND      applicants.deleted_at IS NULL
         JOIN     persons
         ON       applicants.person_id = persons.id
         WHERE    applicants.id IS NOT NULL
         AND      (
                           applicants.status = 'active'
                  OR       (
                                    applicants.status = 'moved in'
                           AND      (
                                             persons.move_in_date >= curdate())
                           AND      (
                                             persons.move_in_date < date_add(curdate(), interval 60 day))))
         GROUP BY prop_id,
                  app_unit )
/*
unit_report_all gets information on all units of the property
*/
, unit_report_all AS
(
          SELECT    prop_select.id     AS prop_id,
                    prop_select.`NAME` AS prop_name,
                    umic.`NAME`        AS unit_number,
                    buildings.`NAME`   AS building,
                    `floor` ,
                    umic.available,
                    umic.unit_status
                    /* , case when available_date <= curdate() then curdate() else umic.available_date end as avldt */
                    ,
                    CASE
                              WHEN available = 1
                              AND       available_date <= curdate() THEN curdate()
                              WHEN available = 0
                              AND       available_date <= curdate() THEN NULL
                              WHEN unit_status = 'Pending Approval' THEN NULL
                              ELSE available_date
                    END            AS available_date ,
                    umic.bedrooms  AS beds,
                    umic.bathrooms AS baths,
                    umic.unit_id,
                    unit_types.`NAME` AS unit_type_name ,
                    umic.square_feet  AS sqft_actual ,
                    unit_market_rent ,
                    min(unit_market_rent) OVER (partition BY umic.prop_id, unit_types.`NAME`) AS unit_market_rent_all,
                    CASE
                              WHEN unit_types.`description` IS NULL THEN
                                        CASE
                                                  WHEN umic.bedrooms = 0 THEN 'Studio'
                                                  ELSE concat(trim(umic.bedrooms)+0,'x', trim(umic.bathrooms)+0)
                                        END
                              ELSE unit_types.`description`
                    END                                                                       AS unit_type_desc ,
                    min(umic.square_feet) OVER (partition BY umic.prop_id, unit_types.`NAME`) AS sqft_min_all,
                    max(umic.square_feet) OVER (partition BY umic.prop_id, unit_types.`NAME`) AS sqft_max_all,
                    trim(unit_types.square_feet)+0                                            AS sqft_model_base ,
                    CASE
                              WHEN NULLIF(website_floorplans.image, '') IS NOT NULL THEN concat('https://madera-newco.s3.us-west-2.amazonaws.com/',website_floorplans.image)
                              ELSE NULL
                    END AS `floorplan`,
                    websites.url `website`,
                    CASE
                              WHEN website_floorplans.virtual_tour_url NOT IN (NULL,
                                                                               'undefined') THEN website_floorplans.virtual_tour_url
                    END AS virtual_tour_url
          FROM      prop_select
          LEFT JOIN unit_move_info_calc umic
          ON        umic.prop_id= prop_select.id
          JOIN      unit_types
          ON        unit_types.id = umic.unit_type_id 
          /* and unit_types.property_id = prop_select.id */
          JOIN      pricing_info
          ON        pricing_info.unit_ids = umic.unit_id
          LEFT JOIN buildings
          ON        buildings.id = building_id
          LEFT JOIN website_floorplans
          ON        website_floorplans.unit_type_id = unit_types.id
          LEFT JOIN websites
          ON        websites.property_id = prop_select.id
          WHERE     prop_id IS NOT NULL )
/*
unit_report_avail gives us the squarefootage values with pricing information for the available units only, grouped by unit_type.
*/
, unit_report_avail AS
(
          SELECT    umic.prop_id,
                    umic.unit_id,
                    umic.`NAME`       AS unit_number,
                    unit_types.`NAME` AS unit_type_name,
                    available,
                    unit_status,
                    unit_market_rent,
                    min(unit_market_rent) OVER (partition BY prop_id, unit_types.`NAME`) AS unit_market_rent_avail,
                    trim(umic.bedrooms)+0                                                AS beds,
                    trim(umic.bathrooms)+0                                               AS baths,
                    min(umic.square_feet) OVER (partition BY prop_id, unit_types.`NAME`) AS sqft_min_avail,
                    max(umic.square_feet) OVER (partition BY prop_id, unit_types.`NAME`) AS sqft_max_avail
          FROM      prop_select
          JOIN      unit_move_info_calc umic
          ON        umic.prop_id= prop_select.id
          JOIN      unit_types
          ON        unit_types.property_id = prop_select.id
          AND       unit_types.id = umic.unit_type_id
          AND       umic.unit_status <> 'Pending Approval'
          JOIN      pricing_info
          ON        umic.unit_id = pricing_info.unit_ids
          LEFT JOIN applicant_info ai
          ON        ai.prop_id = prop_select.id
          AND       ai.app_unit = umic.unit_id
          WHERE     prop_select.id IS NOT NULL
          AND       available = 1
          AND       applying IS NULL )
/*
unit_report_consolidated joins unit_report_all and unit_report_avail to combine all the relevant information that will be needed for the grouping summary provided below.
unit_report_consolidated is the units_level report
*/
, unit_report_consolidated AS
(
          SELECT    ura1.prop_id,
                    ura1.prop_name,
                    ura1.unit_id,
                    ura1.`floor`,
                    ura1.building,
                    ura1.unit_number,
                    ura1.unit_status,
                    ura1.unit_type_name AS model_type,
                    ura1.unit_type_name,
                    ura1.unit_type_desc,
                    ura1.available,
                    ura1.available_date,
                    trim(ura1.beds)+0  AS beds,
                    trim(ura1.baths)+0 AS baths,
                    ura1.sqft_min_all ,
                    ura1.sqft_max_all,
                    ura1.sqft_model_base,
                    ura2.sqft_min_avail,
                    ura2.sqft_max_avail,
                    ura1.sqft_actual ,
                    ura1.unit_market_rent_all,
                    min(ura2.unit_market_rent) OVER (partition BY prop_id, ura1.unit_type_name) AS unit_market_rent_avail,
                    ura1.unit_market_rent ,
                    ura1.floorplan,
                    ura1.website,
                    ura1.virtual_tour_url
          FROM      unit_report_all ura1
          LEFT JOIN unit_report_avail ura2
          ON        ura1.prop_id = ura2.prop_id
          AND       ura1.unit_id = ura2.unit_id )
/*
unit_type_data_complete groups the unit information and produces the final model-level data.
*/
, unit_type_data_complete AS
(
         SELECT   prop_id                     AS prop_id2,
                  prop_name                   AS prop_name2,
                  unit_type_name              AS model_type,
                  unit_type_name              AS unit_type_name2,
                  count(unit_id)              AS total_units ,
                  sum(available)              AS available2,
                  min(available_date)         AS unit_type_first_avail ,
                  min(unit_market_rent_all)   AS unit_market_rent_all2,
                  min(unit_market_rent_avail) AS unit_market_rent_avail2,
                  sqft_model_base             AS sqft_model_base2 ,
                  min(sqft_min_all)           AS sqft_min_all2,
                  max(sqft_max_all)           AS sqft_max_all2 ,
                  min(sqft_min_avail)         AS sqft_min_avail2,
                  max(sqft_max_avail)         AS sqft_max_avail2 ,
                  unit_type_desc              AS unit_type_desc2 ,
                  floorplan                   AS floorplan2,
                  website                     AS website2,
                  virtual_tour_url            AS virtual_tour_url2,
                  beds                        AS beds2,
                  baths                       AS baths2
         FROM     unit_report_consolidated
         GROUP BY unit_report_consolidated.prop_id,
                  unit_report_consolidated.unit_type_name,
                  unit_report_consolidated.floorplan )
"""

last_query = """
/*
Final select statement for unit_level (model) type reports.
*/
,report_final_unit_type AS
(
         SELECT   prop_id2        AS property_id ,
                  prop_name2      AS property_name ,
                  unit_type_name2 AS model_type ,
                  unit_type_name2 AS unit_type_name ,
                  unit_type_desc2 AS unit_type_desc ,
                  trim(beds2)+0   AS beds ,
                  trim(baths2)+0  AS baths ,
                  total_units ,
                  CONVERT (available2, unsigned) AS available ,
                  unit_type_first_avail ,
                  unit_market_rent_all2                                        AS unit_market_rent_all ,
                  unit_market_rent_avail2                                      AS unit_market_rent_avail ,
                  COALESCE(unit_market_rent_avail2, unit_market_rent_all2)     AS market_rent ,
                  CONVERT (sqft_model_base2, unsigned)                         AS sqft_model_base ,
                  CONVERT (sqft_model_base2, unsigned)                         AS sqft ,
                  CONVERT (sqft_min_all2, unsigned)                            AS sqft_min_all ,
                  CONVERT (max(sqft_max_all2), unsigned)                       AS sqft_max_all ,
                  CONVERT (sqft_min_avail2, unsigned)                          AS sqft_min_avail ,
                  CONVERT (sqft_max_avail2, unsigned)                          AS sqft_max_avail ,
                  CONVERT (COALESCE(sqft_min_avail2, sqft_min_all2), unsigned) AS sqft_min_report ,
                  CONVERT (COALESCE(sqft_max_avail2, sqft_max_all2), unsigned) AS sqft_max_report ,
                  CASE
                           WHEN COALESCE(sqft_min_avail2, sqft_min_all2) <> COALESCE(sqft_max_avail2, sqft_max_all2) THEN concat(COALESCE(sqft_min_avail2, sqft_min_all2),'-',COALESCE(sqft_max_avail2, sqft_max_all2))
                           ELSE COALESCE(sqft_min_avail2, sqft_min_all2)
                  END               AS sqft_range ,
                  website2          AS website,
                  virtual_tour_url2 AS virtual_tour_url ,
                  virtual_tour_url2 AS virtual_tour ,
                  floorplan2        AS floorplan ,
                  CASE
                           WHEN floorplan2 IS NOT NULL THEN concat('Scaled diagram of floor plan depicting the typical ',unit_type_name2,' (',unit_type_desc2,') unit at ',prop_name2,' community, as viewed from above. Image provides the layout of ',
                                    CASE
                                             WHEN beds2 IS NULL
                                             OR       beds2 = 0 THEN ''
                                             ELSE concat(trim(beds2)+0,' bedroom',
                                                      CASE
                                                               WHEN beds2 >1 THEN 's'
                                                               ELSE ''
                                                      END ,' and ')
                                    END, trim(baths2)+0,' bathroom',
                                    CASE
                                             WHEN baths2 >1 THEN 's'
                                             ELSE ''
                                    END ,' relative to walls, doors, windows, and other substantial fixed features in approximately ', COALESCE(sqft_min_avail2, sqft_min_all2),'-',COALESCE(sqft_max_avail2, sqft_max_all2),' square feet (',round(COALESCE(sqft_min_avail2, sqft_min_all2)/10.764,1),'-',round(COALESCE(sqft_max_avail2, sqft_max_all2)/10.764,1) ,' square meters) of total living space.')
                           ELSE NULL
                  END AS floorplan_alt_text
         FROM     unit_type_data_complete
         GROUP BY unit_type_data_complete.prop_id2,
                  unit_type_data_complete.unit_type_name2,
                  unit_type_data_complete.floorplan2 ) , report_unit AS
(
          SELECT    urc1.*,
                    unit_type_first_avail
          FROM      unit_report_consolidated urc1
          LEFT JOIN unit_type_data_complete urc2
          ON        urc1.unit_type_name = urc2.unit_type_name2
          AND       urc1.prop_id = urc2.prop_id2 ) , report_final_unit AS
(
       SELECT prop_id   AS property_id ,
              prop_name AS property_name ,
              building ,
              `floor` ,
              unit_id ,
              unit_number ,
              CASE
                     WHEN available = 0 THEN 'false'
                     WHEN available = 1 THEN 'true'
                     ELSE NULL
              END                           AS available_boolean ,
              CONVERT (available, unsigned) AS is_available ,
              1*available                   AS available ,
              available_date ,
              unit_status ,
              model_type ,
              unit_type_name ,
              unit_type_desc ,
              beds ,
              baths ,
              unit_market_rent               AS market_rent_amount ,
              unit_market_rent               AS market_rent ,
              CONVERT(sqft_actual, unsigned) AS sqft
       FROM   report_unit )
SELECT    rfu.unit_number,
          rfu.unit_id            AS provider_id,
          rfu.market_rent_amount AS price,
          NULL                   AS lease_term,
          rfu.available_date     AS available_on,
          NULL                   AS lease_starts_on,
          rfu.model_type,
          rfut.floorplan
FROM      report_final_unit rfu
LEFT JOIN report_final_unit_type rfut
ON        rfut.property_id = rfu.property_id
AND       rfut.model_type = rfu.model_type
WHERE     rfu.available= 1;  
"""

engrain_push_newco_query = newco_units_base_query + last_query
