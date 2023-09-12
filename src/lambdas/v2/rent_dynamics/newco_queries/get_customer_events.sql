select 
  * 
from 
  (
    select 
      "move_in_events" `type`, 
      concat(
        "MIE", move_in_events.id_move_in_events
      ) `id`, 
      move_in_events.movein_date `date`, 
      move_in_events.created_at, 
      residents.person_id `persons.id`, 
      residents.property_id 
    from 
      move_in_events 
      JOIN resident_events on move_in_events.id_move_in_events = resident_events.eventable_id 
      and resident_events.eventable_type = 'App\\\\MoveInEvent' 
      JOIN residents on resident_events.resident_id = residents.id 
    WHERE 
      residents.deleted_at is null 
      and resident_events.deleted_at is null 
      and move_in_events.deleted_at is null 
    UNION 
    select 
      "move_out_events" `type`, 
      concat(
        "MOE", move_out_events.id_move_out_events
      ) `id`, 
      move_out_events.moveout_date `date`, 
      move_out_events.created_at, 
      residents.person_id `persons.id`, 
      residents.property_id 
    from 
      move_out_events 
      JOIN resident_events on move_out_events.id_move_out_events = resident_events.eventable_id 
      and resident_events.eventable_type = 'App\\\\MoveOutEvent' 
      JOIN residents on resident_events.resident_id = residents.id 
    WHERE 
      residents.deleted_at is null 
      and resident_events.deleted_at is null 
      and move_out_events.deleted_at is null 
    UNION 
    select 
      "notice_events" `type`, 
      concat(
        "NE", notice_events.id_notice_events
      ) `id`, 
      notice_events.estimated_moveout_date `date`, 
      notice_events.created_at, 
      residents.person_id `persons.id`, 
      residents.property_id 
    from 
      notice_events 
      JOIN resident_events on notice_events.id_notice_events = resident_events.eventable_id 
      and resident_events.eventable_type = 'App\\\\NoticeEvent' 
      JOIN residents on resident_events.resident_id = residents.id 
    WHERE 
      residents.deleted_at is null 
      and resident_events.deleted_at is null 
      and notice_events.deleted_at is null 
    UNION 
    select 
      "unit_leases" `type`, 
      concat("UL", unit_leases.id) `id`, 
      unit_leases.lease_start_date `date`, 
      unit_leases.created_at, 
      residents.person_id `persons.id`, 
      residents.property_id 
    from 
      unit_leases 
      JOIN residents on unit_leases.resident_id = residents.id 
    WHERE 
      residents.deleted_at is null 
    UNION 
    select 
      "persons" `type`, 
      concat("PER", persons.id) `id`, 
      null `date`, 
      persons.created_at, 
      id `persons.id`, 
      persons.property_id 
    from 
      persons 
    WHERE 
      persons.deleted_at is null 
    UNION 
    select 
      "applicants" `type`, 
      concat("APP", applicants.id) `id`, 
      null `date`, 
      applicants.created_at, 
      applicants.person_id `persons.id`, 
      applicants.property_id 
    from 
      applicants 
    WHERE 
      applicants.deleted_at is null 
    UNION 
    select 
      "residents" `type`, 
      concat("RES", residents.id) `id`, 
      null `date`, 
      residents.created_at, 
      residents.person_id `persons.id`, 
      residents.property_id 
    from 
      residents 
    WHERE 
      residents.deleted_at is null
  ) events 
WHERE 
  events.property_id = %(community_id)s 
  and events.created_at BETWEEN %(start_date)s 
  and %(end_date)s
