select 
  concat("T", trans.id) `id`, 
  je.post_date, 
  if(
    trans.has_override = 1, 
    if(
      is_credit = 1, trans.override_amount *-1, 
      trans.override_amount
    ), 
    if(
      is_credit = 1, trans.amount *-1, trans.amount
    )
  ) `amount`, 
  if(is_credit = 1, "credit", "debit") `transaction_type`, 
  trans.notes, 
  codes.id `charge_code_id`, 
  codes.name `charge_code_name`, 
  trans.property_id `community_id` 
FROM 
  ar_transactions trans 
  JOIN resident_ledgers lgr ON trans.resident_ledger_id = lgr.id 
  JOIN journal_entries je on trans.journal_entry_batches_id = je.journal_entry_batches_id 
  JOIN accounting_charge_codes codes ON trans.charge_code_id = codes.id 
WHERE 
  trans.property_id = %(community_id)s 
  and lgr.resident_id = %(resident_id)s 
  and je.post_date BETWEEN %(start_date)s 
  and %(end_date)s 
  and trans.deleted_at is null 
UNION 
select 
  concat("P", pmts.id) `id`, 
  je.post_date, 
  pmts.amount *-1, 
  "credit" `transaction_type`, 
  pmts.notes, 
  null `charge_code_id`, 
  null `charge_code_name`, 
  pmts.property_id `community_id` 
from 
  ar_resident_payments pmts 
  JOIN resident_ledgers lgr ON pmts.resident_ledger_id = lgr.id 
  JOIN journal_entries je on pmts.journal_entry_batches_id = je.journal_entry_batches_id 
  LEFT JOIN ar_resident_payment_reversals pmt_rvs ON pmts.id = pmt_rvs.ar_resident_payment_id 
WHERE 
  pmts.property_id = %(community_id)s 
  and lgr.resident_id = %(resident_id)s 
  and je.post_date BETWEEN %(start_date)s 
  and %(end_date)s 
  and pmts.deleted_at is null 
  and pmt_rvs.id is null;
