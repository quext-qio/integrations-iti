select
  id,
  name,
  address,
  city,
  state,
  postal,
  phone
from
  properties
where
  properties.id = %(community_id)s