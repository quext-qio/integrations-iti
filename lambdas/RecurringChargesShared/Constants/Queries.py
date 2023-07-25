recurringChangesNewcoQuery = """
    SELECT 
        ar_transaction_recurrings.amount, 
        charge_code_id, 
        'Lease' `chargeable_type`, 
        `Last Lease` `chargeable_id`, 
        NULL `due_date`,
        IF(is_debit = 1,'Charge','Credit') `type`,
        unit_leases.lease_start_date `lease_effective_date`,
        unit_leases.move_in_date `lease_move_in_date`,
        IF(resident_events.id_resident_events IS NULL, 'Current','Past') `resident-status`,
        starts_at,
        ends_at,
        next_run_date,
        frequency,
        ar_transaction_recurrings.notes,
        accounting_charge_codes.`name` `charge_code_desc`
    FROM ar_transaction_recurrings
    JOIN resident_ledgers 
    ON resident_ledger_id = resident_ledgers.id
    JOIN residents 
    ON resident_ledgers.resident_id = residents.id
    JOIN ( 
        SELECT a.resident_id, IF(`Lease Count` = `Current Lease Count`, `Last Lease`,`Current Last Lease`) `Last Lease`
        FROM ( 
            SELECT COUNT(id) `Lease Count`, MAX(id) `Last Lease`, resident_id 
            FROM unit_leases 
            GROUP BY  resident_id
        ) a
        LEFT JOIN ( 
            SELECT COUNT(id) `Current Lease Count`, MAX(id) `Current Last Lease`, resident_id 
            FROM unit_leases 
            WHERE unit_leases.lease_start_date < curdate()
            GROUP BY  resident_id 
        ) b 
        ON a.resident_id = b.resident_id
    ) c 
    ON c.resident_id = residents.id
    JOIN unit_leases 
    ON `Last Lease` = unit_leases.id
    LEFT JOIN resident_events 
    ON resident_events.resident_id = residents.id 
    AND resident_events.eventable_type = 'App\\MoveOutEvent' 
    AND resident_events.deleted_at IS NULL
    JOIN properties 
    ON ar_transaction_recurrings.property_id = properties.id
    JOIN accounting_charge_codes 
    ON charge_code_id = accounting_charge_codes.id
    WHERE residents.deleted_at IS NULL  
    AND ar_transaction_recurrings.deleted_at IS NULL
    AND properties.id = :newco_property_id    
"""