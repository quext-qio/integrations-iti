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
  id = %(community_id)s
