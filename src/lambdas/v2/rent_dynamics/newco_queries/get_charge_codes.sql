select 
  codes.id, 
  codes.name, 
  code_cat.name `category`, 
  if(
    code_prop.override_amount is not null, 
    code_prop.override_amount, codes.amount
  ) `amount`, 
  code_prop.property_id 
from 
  accounting_charge_codes codes 
  JOIN accounting_charge_code_property code_prop ON codes.id = code_prop.accounting_charge_code_id 
  JOIN accounting_charge_code_categories code_cat ON codes.accounting_charge_code_category_id = code_cat.id 
WHERE 
  code_prop.property_id = %s
