select 
  units.property_id, 
  max(units.id) `id`, 
  max(units.unit_type_id) `unit_type_id`, 
  max(units.square_feet) `square_feet`, 
  max(units.bedrooms) `bedrooms`, 
  max(units.bathrooms) `bathrooms`, 
  max(units.market_rent_amount) `market_rent_amount`, 
  max(units.rent_amount) `rent_amount`, 
  if(
    (
      max(per.first_name) is null 
      and max(per.last_name) is null
    ) 
    or (
      max(units.status) in (
        "", "Down", "Shop", "Rehab", "Model"
      )
    ), 
    "Vacant", 
    "Occupied"
  ) `occupancy_status`, 
  if(
    max(units.status) in (
      "", "Down", "Shop", "Rehab", "Model"
    ), 
    max(units.status), 
    if(
      max(futureMoveIn.move_in_resident) is not null, 
      "Reserved", 
      if(
        max(res.move_out_date) is not null, 
        "On Notice", 
        if(
          max(per.first_name) is not null 
          or max(per.last_name) is not null, 
          "Leased", 
          if(
            max(units.ready_to_show) = 1, 
            "Available", 
            if(
              max(units.ready_to_show) = 0, 
              "Not Ready", 
              ""
            )
          )
        )
      )
    )
  ) `lease_status`, 
  units.name `unit_name`, 
  if(
    max(units.status) in (
      "", "Down", "Shop", "Rehab", "Model"
    ), 
    0, 
    1
  ) `is_active` 
from 
  (
    SELECT 
      residents.id, 
      transfer_resident, 
      residents.person_id, 
      (
        SELECT 
          unit_id 
        FROM 
          unit_leases ul 
        WHERE 
          ul.resident_id = residents.id 
          and transfer_resident = 0 
        ORDER BY 
          created_at desc 
        LIMIT 
          1
      ) last_lease_unit_id, 
      IFNULL(
        (
          SELECT 
            move_in_events.movein_date 
          FROM 
            resident_events 
            LEFT JOIN move_in_events ON resident_events.eventable_id = move_in_events.id_move_in_events 
          WHERE 
            resident_events.deleted_at IS NULL 
            AND resident_events.eventable_type = "App\\\\MoveInEvent" 
            AND resident_events.resident_id = residents.id 
            AND move_in_events.deleted_at IS NULL 
          ORDER BY 
            resident_events.id_resident_events desc 
          LIMIT 
            1
        ),(
          SELECT 
            move_in_date 
          FROM 
            unit_leases ul 
          WHERE 
            ul.resident_id = residents.id 
          ORDER BY 
            created_at desc 
          LIMIT 
            1
        )
      ) move_in_date, 
      (
        SELECT 
          eventable_type 
        FROM 
          resident_events 
        WHERE 
          deleted_at IS NULL 
          AND resident_events.resident_id = residents.id 
        ORDER BY 
          id_resident_events DESC 
        LIMIT 
          1
      ) event_type, 
      (
        SELECT 
          id 
        FROM 
          unit_leases 
        WHERE 
          unit_id = last_lease_unit_id 
          AND transfer_resident = 1 
        LIMIT 
          1
      ) from_transfer, 
      (
        SELECT 
          IF(
            move_out_events.moveout_date IS NOT NULL, 
            move_out_events.moveout_date, notice_events.estimated_moveout_date
          ) 
        FROM 
          resident_events 
          JOIN (
            SELECT 
              resident_id `resident_id`, 
              MAX(id_resident_events) `id` 
            FROM 
              resident_events 
            WHERE 
              deleted_at IS NULL 
            GROUP BY 
              resident_id
          ) lastEvent ON resident_events.id_resident_events = lastEvent.id 
          LEFT JOIN move_out_events ON resident_events.eventable_type = "App\\\\MoveOutEvent" 
          AND resident_events.eventable_id = move_out_events.id_move_out_events 
          AND move_out_events.deleted_at IS NULL 
          LEFT JOIN notice_events ON resident_events.eventable_type = "App\\\\NoticeEvent" 
          AND resident_events.eventable_id = notice_events.id_notice_events 
          AND notice_events.deleted_at IS NULL 
        WHERE 
          resident_events.deleted_at IS NULL 
          AND resident_events.resident_id = residents.id
      ) move_out_date 
    FROM 
      residents 
    WHERE 
      residents.deleted_at IS NULL 
    HAVING 
      move_in_date <= curdate() 
      and (
        move_out_date is null 
        or event_type = "App\\\\NoticeEvent" 
        or (
          event_type = "App\\\\MoveOutEvent" 
          and move_out_date > curdate()
        )
      )
  ) res 
  RIGHT JOIN units on res.last_lease_unit_id = units.id 
  left join applicants app on units.id = app.unit_id 
  AND app.deleted_at is null 
  AND app.status in ("active", "pending") 
  left join (
    SELECT 
      move_in_events.movein_date, 
      unit_leases.unit_id, 
      concat(
        persons.first_name, " ", persons.last_name
      ) `move_in_resident`, 
      unit_leases.actual_rent_amount 
    FROM 
      move_in_events 
      JOIN resident_events ON resident_events.eventable_id = move_in_events.id_move_in_events 
      AND eventable_type = "App\\\\MoveInEvent" 
      AND resident_events.deleted_at IS NULL 
      JOIN v_hlpr_residents res ON resident_events.resident_id = res.id 
      AND res.deleted_at IS NULL 
      JOIN unit_leases ON unit_leases.resident_id = res.id 
      JOIN persons on res.person_id = persons.id 
    WHERE 
      movein_date > curdate() 
      AND move_in_events.deleted_at IS NULL 
      AND move_in_events.canceled_date IS NULL
  ) futureMoveIn ON units.id = futureMoveIn.unit_id 
  LEFT JOIN unit_types on units.unit_type_id = unit_types.id 
  and unit_types.deleted_at IS NULL 
  LEFT JOIN persons per ON res.person_id = per.id 
  LEFT JOIN persons app_per ON app.person_id = app_per.id 
WHERE 
  units.deleted_at is null 
  and app_per.deleted_at is null 
  and units.property_id = %(community_id)s 
GROUP BY 
  units.name, 
  units.property_id
