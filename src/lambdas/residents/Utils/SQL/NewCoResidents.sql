SELECT DISTINCT b.*
                           FROM ( 
                                      SELECT propertyId,
                                             unitId,
                                             personId,
                                             firstName,
                                             lastName,
                                             DOB,
                                             SSN,
                                             emailAddress,
                                             phone,
                                             address,
                                             apt,
                                             city,
                                             state,
                                             zip,
                                             leaseStartDate,
                                             leaseEndDate,
                                             leaseId,
                                             moveInDate,
                                             DATE_FORMAT(moveOutDate, '%Y-%m-%d') moveOutDate,
                                             IF(zzz > CURDATE(),'future resident','resident') partyType,
                                             residentId
                                        FROM (
                                              SELECT DISTINCT persons.id personId,
                                                              persons.first_name firstName,
                                                              persons.last_name lastName,
                                                              persons.dob DOB,
                                                              persons.ssn SSN,
                                                              persons.email emailAddress,
                                                              persons.phone,
                                                              units.id unitId,
                                                              properties.address,
                                                              units.name apt,
                                                              properties.city,
                                                              properties.state,
                                                              properties.postal zip,
                                                              unit_leases.lease_start_date leaseStartDate,
                                                              unit_leases.lease_expiration_date leaseEndDate,
                                                              unit_leases.id leaseId,
                                                              unit_leases.move_in_date moveInDate,
                                                              MAX(estimated_moveout_date) moveOutDate,
                                                              MAX(move_out_events.id_move_out_events) `Move Out ID`,
                                                              MAX(movein_date) zzz,
                                                              properties.id propertyId,
                                                              residents.Id residentId
                                                         FROM residents
                                                         JOIN unit_leases ON unit_leases.resident_id = residents.id
                                                         JOIN units ON unit_leases.unit_id = units.id
                                                         JOIN properties ON units.property_id = properties.id
                                                         JOIN persons ON residents.person_id = persons.id
                                                         JOIN buildings ON units.building_id = buildings.id
                                                         JOIN unit_types ON units.unit_type_id = unit_types.id
                                                    LEFT JOIN co_applicant ON co_applicant.person_id = persons.id
                                                         JOIN resident_events ON resident_events.resident_id = residents.id 
                                                          AND resident_events.deleted_at IS NULL
                                                    LEFT JOIN move_out_events ON eventable_type = 'App\\\\MoveOutEvent' 
                                                          AND resident_events.eventable_id = move_out_events.id_move_out_events 
                                                          AND move_out_events.deleted_at IS NULL
                                                    LEFT JOIN move_in_events ON eventable_type = 'App\\\\MoveInEvent' 
                                                          AND resident_events.eventable_id = move_in_events.id_move_in_events 
                                                          AND move_in_events.deleted_at IS NULL
                                                    LEFT JOIN notice_events ON eventable_type = 'App\\\\NoticeEvent' 
                                                          AND resident_events.eventable_id = notice_events.id_notice_events 
                                                          AND notice_events.deleted_at IS NULL
                                                        WHERE residents.deleted_at IS NULL AND units.deleted_at IS NULL 
                                                          AND properties.disposition_date IS NULL 
                                                          AND properties.id = %s
                                                          AND unit_leases.is_active = 1
                                                     GROUP BY properties.name, persons.first_name, persons.last_name, persons.email
                                                       HAVING `Move Out ID` IS NULL
                                             ) a
                                UNION
                                      SELECT properties.id propertyId,
                                             units.id unitId,
                                             co_applicant.id personId,
                                             co_applicant.first_name firstName,
                                             co_applicant.last_name lastName,
                                             co_applicant.birth_date DOB,
                                             co_applicant.ssn SSN,
                                             co_applicant.email emailAddress,
                                             co_applicant.phone,
                                             properties.address,
                                             units.name apt,
                                             properties.city,
                                             properties.state,
                                             properties.postal,
                                             unit_leases.lease_start_date leaseStartDate,
                                             unit_leases.lease_expiration_date leaseEndDate,
                                             unit_leases.id leaseId,
                                             unit_leases.move_in_date moveInDate,
                                             DATE_FORMAT(estimated_moveout_date, '%Y-%m-%d') moveOutDate,
                                             'coresident',
                                             residents.Id residentId
                                        FROM co_applicant
                                        JOIN persons ON co_applicant.person_id = persons.id
                                        JOIN properties ON persons.property_id = properties.id
                                        JOIN residents ON residents.person_id = persons.id
                                        JOIN unit_leases ON unit_leases.resident_id = residents.id
                                        JOIN units ON unit_leases.unit_id = units.id
                                        JOIN resident_events ON resident_events.resident_id = residents.id 
                                         AND resident_events.deleted_at IS NULL
                                   LEFT JOIN notice_events ON eventable_type = 'App\\\\NoticeEvent' 
                                         AND resident_events.eventable_id = notice_events.id_notice_events 
                                         AND notice_events.deleted_at IS NULL
                                       WHERE applicant_type = 'App\\\\API\\\\Resident' AND co_applicant.deleted_at IS NULL
                                         AND unit_leases.is_active = 1
                                UNION
                                      SELECT properties.id propertyId,
                                             units.id unitId,
                                             associatedoccupant.id personId,
                                             associatedoccupant.first_name firstName,
                                             associatedoccupant.last_name lastName,
                                             associatedoccupant.dob DOB,
                                             associatedoccupant.ssn SSN,
                                             associatedoccupant.email emailAddress,
                                             associatedoccupant.phone,
                                             properties.address,
                                             units.name apt,
                                             properties.city,
                                             properties.state,
                                             properties.postal,
                                             unit_leases.lease_start_date leaseStartDate,
                                             unit_leases.lease_expiration_date leaseEndDate,
                                             unit_leases.id leaseId,
                                             unit_leases.move_in_date moveInDate,
                                             DATE_FORMAT(estimated_moveout_date, '%Y-%m-%d') moveOutDate,
                                             'occupant',
                                             residents.Id residentId
                                        FROM associated_occupants
                                        JOIN persons primaryresident ON applicant_id = primaryresident.id
                                        JOIN persons associatedoccupant ON person_id = associatedoccupant.id
                                        JOIN properties ON primaryresident.property_id = properties.id
                                        JOIN residents ON residents.person_id = applicant_id
                                        JOIN unit_leases ON unit_leases.resident_id = residents.id
                                        JOIN units ON unit_leases.unit_id = units.id
                                        JOIN resident_events ON resident_events.resident_id = residents.id 
                                         AND resident_events.deleted_at IS NULL
                                   LEFT JOIN notice_events ON eventable_type = 'App\\\\NoticeEvent' 
                                         AND resident_events.eventable_id = notice_events.id_notice_events 
                                         AND notice_events.deleted_at IS NULL
                                       WHERE associated_occupants.deleted_at IS NULL
                                         AND unit_leases.is_active = 1
                                ) b
                           JOIN properties ON propertyId = properties.id
                          WHERE properties.disposition_date IS NULL 
                            AND properties.id = %s