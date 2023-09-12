select 
  distinct units.name `unit_name`, 
  units.id `unit_id`, 
  res_and_co_res.resident_id, 
  res_and_co_res.prospect_id, 
  res_and_co_res.first_name, 
  res_and_co_res.last_name, 
  res_and_co_res.ssn, 
  res_and_co_res.dob, 
  res_and_co_res.email, 
  res_and_co_res.phone, 
  res_and_co_res.`address`, 
  res_and_co_res.`city`, 
  res_and_co_res.`state`, 
  res_and_co_res.`postal`, 
  res_and_co_res.lease_start, 
  res_and_co_res.lease_expire, 
  res_and_co_res.lease_id, 
  res_and_co_res.is_active, 
  res_and_co_res.move_in_date, 
  res_and_co_res.move_out_date, 
  res_and_co_res.property_id, 
  res_and_co_res.res_type 
from 
  (
    select 
      res.id `resident_id`, 
      persons.prospect_id, 
      persons.first_name, 
      persons.last_name, 
      persons.ssn, 
      persons.dob, 
      persons.email, 
      persons.phone, 
      if(
        persons.address = 'null', null, persons.address
      ) `address`, 
      if(
        persons.city = 'null', null, persons.city
      ) `city`, 
      if(
        persons.state = 'null', null, persons.state
      ) `state`, 
      if(
        persons.postal = 'null', null, persons.postal
      ) `postal`, 
      res.lease_start, 
      res.lease_expire, 
      res.lease_id, 
      res.is_active, 
      res.move_in_date, 
      res.move_out_date, 
      res.property_id, 
      'Resident' `res_type` 
    from 
      (
        SELECT 
          residents.id, 
          residents.person_id, 
          residents.property_id, 
          IFNULL(
            (
              SELECT 
                move_in_events.movein_date 
              FROM 
                resident_events 
                LEFT JOIN move_in_events ON resident_events.eventable_id = move_in_events.id_move_in_events 
              WHERE 
                resident_events.deleted_at IS NULL 
                AND resident_events.eventable_type = 'App\\\\MoveInEvent' 
                AND resident_events.resident_id = residents.id 
                AND move_in_events.deleted_at IS NULL 
              ORDER BY 
                resident_events.id_resident_events desc 
              LIMIT 
                1
            ), residents.move_in_date
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
          ) event, 
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
              LEFT JOIN move_out_events ON resident_events.eventable_type = 'App\\\\MoveOutEvent' 
              AND resident_events.eventable_id = move_out_events.id_move_out_events 
              AND move_out_events.deleted_at IS NULL 
              LEFT JOIN notice_events ON resident_events.eventable_type = 'App\\\\NoticeEvent' 
              AND resident_events.eventable_id = notice_events.id_notice_events 
              AND notice_events.deleted_at IS NULL 
            WHERE 
              resident_events.deleted_at IS NULL 
              AND resident_events.resident_id = residents.id
          ) move_out_date, 
          (
            SELECT 
              lease_start_date 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) lease_start, 
          (
            SELECT 
              lease_expiration_date 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) lease_expire, 
          (
            SELECT 
              unit_leases.id 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) lease_id, 
          (
            SELECT 
              unit_leases.is_active 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) is_active 
        FROM 
          residents 
        WHERE 
          residents.deleted_at IS NULL
      ) res 
      join persons on res.person_id = persons.id 
    where 
      persons.deleted_at is null 
      and res.property_id = %(community_id)s 
      AND res.move_in_date >= %(move_in_date)s 
      and (
        res.move_out_date is null 
        OR res.event = 'App\\\\NoticeEvent' 
        OR %(move_out_date)s is null 
        OR res.move_out_date <= %(move_out_date)s
      ) 
    union all 
    select 
      res.id `resident_id`, 
      null `prospect_id`, 
      co_app.first_name, 
      co_app.last_name, 
      if(
        co_app.ssn like 'e%%', null, co_app.ssn
      ), 
      co_app.birth_date, 
      co_app.email, 
      co_app.phone, 
      null `address`, 
      null `city`, 
      null `state`, 
      null `postal`, 
      res.lease_start, 
      res.lease_expire, 
      res.lease_id, 
      res.is_active, 
      res.move_in_date, 
      res.move_out_date, 
      res.property_id, 
      'Co-Resident' `res_type` 
    from 
      (
        SELECT 
          residents.id, 
          residents.person_id, 
          residents.property_id, 
          IFNULL(
            (
              SELECT 
                move_in_events.movein_date 
              FROM 
                resident_events 
                LEFT JOIN move_in_events ON resident_events.eventable_id = move_in_events.id_move_in_events 
              WHERE 
                resident_events.deleted_at IS NULL 
                AND resident_events.eventable_type = 'App\\\\MoveInEvent' 
                AND resident_events.resident_id = residents.id 
                AND move_in_events.deleted_at IS NULL 
              ORDER BY 
                resident_events.id_resident_events desc 
              LIMIT 
                1
            ), residents.move_in_date
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
          ) event, 
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
              LEFT JOIN move_out_events ON resident_events.eventable_type = 'App\\\\MoveOutEvent' 
              AND resident_events.eventable_id = move_out_events.id_move_out_events 
              AND move_out_events.deleted_at IS NULL 
              LEFT JOIN notice_events ON resident_events.eventable_type = 'App\\\\NoticeEvent' 
              AND resident_events.eventable_id = notice_events.id_notice_events 
              AND notice_events.deleted_at IS NULL 
            WHERE 
              resident_events.deleted_at IS NULL 
              AND resident_events.resident_id = residents.id
          ) move_out_date, 
          (
            SELECT 
              lease_start_date 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) lease_start, 
          (
            SELECT 
              lease_expiration_date 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) lease_expire, 
          (
            SELECT 
              unit_leases.id 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) lease_id, 
          (
            SELECT 
              unit_leases.is_active 
            FROM 
              unit_leases 
            WHERE 
              unit_leases.resident_id = residents.id 
            ORDER by 
              is_active desc, 
              lease_expiration_date desc 
            limit 
              1
          ) is_active 
        FROM 
          residents 
        WHERE 
          residents.deleted_at IS NULL
      ) res 
      left JOIN co_applicant co_app on co_app.applicant_id = res.id 
    where 
      co_app.first_name is not null 
      and co_app.deleted_at is null 
      and res.property_id = %(community_id)s 
      AND res.move_in_date >= %(move_in_date)s 
      and (
        res.move_out_date is null 
        OR res.event = 'App\\\\NoticeEvent' 
        OR %(move_out_date)s is null 
        OR res.move_out_date <= %(move_out_date)s
      )
  ) res_and_co_res 
  join unit_leases on unit_leases.resident_id = res_and_co_res.resident_id 
  join units on unit_leases.unit_id = units.id 
WHERE 
  units.deleted_at is null 
  and `first_name` != 'iNCHNGzByPjhApvn7XBD' 
ORDER BY 
  CAST(units.name as unsigned), 
  units.name, 
  `res_type` desc
