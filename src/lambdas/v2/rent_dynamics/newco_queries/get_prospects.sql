select
  prospects.id 'prospect_id',
  prospects.first_name,
  prospects.last_name,
  prospects.email,
  prospects.phone,
  persons.address,
  persons.city,
  persons.state,
  persons.postal,
  prospects.property_id,
  persons.move_in_date,
  persons.desired_move_date,
  persons.desired_bedrooms,
  persons.additional_occupants,
  persons.pets
from
  prospects
join
  persons on persons.prospect_id = prospects.id
where
  prospects.property_id = %(community_id)s
  and prospects.created_at >= %(create_date)s