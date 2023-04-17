SELECT 
  name, 
  address, 
  address2, 
  city, 
  state, 
  postal, 
  email, 
  phone, 
  speed_dial, 
  fax 
FROM 
  properties 
WHERE 
  id = :newco_property_id