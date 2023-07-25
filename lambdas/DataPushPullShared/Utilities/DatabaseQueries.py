def getQuery(set_type: str):
    query = queries[set_type]['query']
    fields = queries[set_type]['headers']
    return query, fields


queries = {
    'community_details': {
        'headers': ['community_id', 'community_name', 'address', 'address2', 'city', 'state', 'zip', 'email',
                    'phone', 'fax', 'customer_alias_community_id', 'manager_name', 'community_website',
                    'uses_transunion',
                    'legal_name', 'shift4_auth_token', 'dwolla_account', 'nestio_id', 'valid_through',
                    'nestio_community_id', 'unit_count'],
        'query': """SELECT `properties`.`id` as `community_id`,
                        `properties`.`name`as `community_name`,
                        `properties`.`address`,
                        `properties`.`address2`,
                        `properties`.`city`,
                        `properties`.`state`,
                        `properties`.`postal` as `zip`,
                        `properties`.`email`,
                        `properties`.`phone`,
                        `properties`.`fax`,
                        `properties`.`acct` as `customer_alias_community_id`,
                        `properties`.`manager_name`,
                        `properties`.`url` as `community_website`,
                        `properties`.`uses_transunion`,
                        `properties`.`legal_name`,
                        `properties`.`shift4_auth_token`,
                        `properties`.`dwolla_account`,
                        `properties`.`nestio_id`,
                        `properties`.`disposition_date` as `valid_through`,
                        `properties`.`nestio_community_id`,
                        count(`v_hlpr_unit_w_property`.`id`) as `unit_count`
                    FROM `DATABASE_NAME`.`properties`, `DATABASE_NAME`.`v_hlpr_unit_w_property`
                    WHERE `DATABASE_NAME`.`properties`.`id` = `v_hlpr_unit_w_property`.`property_id`
                    GROUP BY `DATABASE_NAME`.`properties`.`id`
                    #WHERE `properties`.`status` = 'Active' and (disposition_date is null or disposition_date > date(now())); 		#all current communities
                    #WHERE `properties`.`status` = 'Active' and disposition_date <= date(now());									#all former communities
                    #WHERE `properties`.`status` = 'Active' and `properties`.`acct` = %(customer_alieas_community_id)s;				# a specific community by customer's external id
                    #WHERE `properties`.`status` = 'Active' and `properties`.`id` = %(community_id)s;								# a specific community by newco db id
                """
    },
    'community_details_after_deposition_date': {
        'headers': ['community_id', 'community_name', 'address', 'address2', 'city', 'state', 'zip', 'email',
                    'phone', 'fax', 'customer_alias_community_id', 'manager_name', 'community_website',
                    'uses_transunion',
                    'legal_name', 'shift4_auth_token', 'dwolla_account', 'nestio_id', 'valid_through',
                    'nestio_community_id', 'unit_count'],
        'query': """SELECT `properties`.`id` as `community_id`,
                        `properties`.`name`as `community_name`,
                        `properties`.`address`,
                        `properties`.`address2`,
                        `properties`.`city`,
                        `properties`.`state`,
                        `properties`.`postal` as `zip`,
                        `properties`.`email`,
                        `properties`.`phone`,
                        `properties`.`fax`,
                        `properties`.`acct` as `customer_alias_community_id`,
                        `properties`.`manager_name`,
                        `properties`.`url` as `community_website`,
                        `properties`.`uses_transunion`,
                        `properties`.`legal_name`,
                        `properties`.`shift4_auth_token`,
                        `properties`.`dwolla_account`,
                        `properties`.`nestio_id`,
                        `properties`.`disposition_date` as `valid_through`,
                        `properties`.`nestio_community_id`,
                        count(`v_hlpr_unit_w_property`.`id`) as `unit_count`
                    FROM `DATABASE_NAME`.`properties`, `DATABASE_NAME`.`v_hlpr_unit_w_property`
                    WHERE `DATABASE_NAME`.`properties`.`id` = `v_hlpr_unit_w_property`.`property_id` and `properties`.`status` = 'Active' and (disposition_date is null or disposition_date > date(now()))
                    GROUP BY `DATABASE_NAME`.`properties`.`id`
                """
    },
    'community_details_before_deposition_date': {
        'headers': ['community_id', 'community_name', 'address', 'address2', 'city', 'state', 'zip', 'email',
                    'phone', 'fax', 'customer_alias_community_id', 'manager_name', 'community_website',
                    'uses_transunion',
                    'legal_name', 'shift4_auth_token', 'dwolla_account', 'nestio_id', 'valid_through',
                    'nestio_community_id', 'unit_count'],
        'query': """SELECT `properties`.`id` as `community_id`,
                        `properties`.`name`as `community_name`,
                        `properties`.`address`,
                        `properties`.`address2`,
                        `properties`.`city`,
                        `properties`.`state`,
                        `properties`.`postal` as `zip`,
                        `properties`.`email`,
                        `properties`.`phone`,
                        `properties`.`fax`,
                        `properties`.`acct` as `customer_alias_community_id`,
                        `properties`.`manager_name`,
                        `properties`.`url` as `community_website`,
                        `properties`.`uses_transunion`,
                        `properties`.`legal_name`,
                        `properties`.`shift4_auth_token`,
                        `properties`.`dwolla_account`,
                        `properties`.`nestio_id`,
                        `properties`.`disposition_date` as `valid_through`,
                        `properties`.`nestio_community_id`,
                        count(`v_hlpr_unit_w_property`.`id`) as `unit_count`
                    FROM `DATABASE_NAME`.`properties`, `DATABASE_NAME`.`v_hlpr_unit_w_property`
                    WHERE `DATABASE_NAME`.`properties`.`id` = `v_hlpr_unit_w_property`.`property_id` and `properties`.`status` = 'Active' and disposition_date <= date(now())
                    GROUP BY `DATABASE_NAME`.`properties`.`id`
                """
    },
    'community_details_by_acct': {
        'headers': ['community_id', 'community_name', 'address', 'address2', 'city', 'state', 'zip', 'email',
                    'phone', 'fax', 'customer_alias_community_id', 'manager_name', 'community_website',
                    'uses_transunion',
                    'legal_name', 'shift4_auth_token', 'dwolla_account', 'nestio_id', 'valid_through',
                    'nestio_community_id', 'unit_count'],
        'query': """ SELECT `properties`.`id` as `community_id`,
                        `properties`.`name`as `community_name`,
                        `properties`.`address`,
                        `properties`.`address2`,
                        `properties`.`city`,
                        `properties`.`state`,
                        `properties`.`postal` as `zip`,
                        `properties`.`email`,
                        `properties`.`phone`,
                        `properties`.`fax`,
                        `properties`.`acct` as `customer_alias_community_id`,
                        `properties`.`manager_name`,
                        `properties`.`url` as `community_website`,
                        `properties`.`uses_transunion`,
                        `properties`.`legal_name`,
                        `properties`.`shift4_auth_token`,
                        `properties`.`dwolla_account`,
                        `properties`.`nestio_id`,
                        `properties`.`disposition_date` as `valid_through`,
                        `properties`.`nestio_community_id`,
                        count(`v_hlpr_unit_w_property`.`id`) as `unit_count`
                    FROM `DATABASE_NAME`.`properties`, `DATABASE_NAME`.`v_hlpr_unit_w_property`
                    WHERE `DATABASE_NAME`.`properties`.`id` = `v_hlpr_unit_w_property`.`property_id` and `properties`.`status` = 'Active' and `properties`.`acct` = %(customer_alias_community_id)s
                    GROUP BY `DATABASE_NAME`.`properties`.`id`
                """
    },
    'community_details_by_id': {
        'headers': ['community_id', 'community_name', 'address', 'address2', 'city', 'state', 'zip', 'email',
                    'phone', 'fax', 'customer_alias_community_id', 'manager_name', 'community_website',
                    'uses_transunion',
                    'legal_name', 'shift4_auth_token', 'dwolla_account', 'nestio_id', 'valid_through',
                    'nestio_community_id', 'availability_status', 'unit_count'],
        'query': """SELECT `properties`.`id` as `community_id`,
                        `properties`.`name`as `community_name`,
                        `properties`.`address`,
                        `properties`.`address2`,
                        `properties`.`city`,
                        `properties`.`state`,
                        `properties`.`postal` as `zip`,
                        `properties`.`email`,
                        `properties`.`phone`,
                        `properties`.`fax`,
                        `properties`.`acct` as `customer_alias_community_id`,
                        `properties`.`manager_name`,
                        `properties`.`url` as `community_website`,
                        `properties`.`uses_transunion`,
                        `properties`.`legal_name`,
                        `properties`.`shift4_auth_token`,
                        `properties`.`dwolla_account`,
                        `properties`.`nestio_id`,
                        `properties`.`disposition_date` as `valid_through`,
                        `properties`.`nestio_community_id`,
                        `properties`.`status` as `availability_status`,
                        count(`v_hlpr_unit_w_property`.`id`) as `unit_count`
                    FROM `DATABASE_NAME`.`properties`, `DATABASE_NAME`.`v_hlpr_unit_w_property`
                    WHERE `DATABASE_NAME`.`properties`.`id` = `v_hlpr_unit_w_property`.`property_id` and `properties`.`status` = 'Active' and `properties`.`id` = %(community_id)s
                    GROUP BY `DATABASE_NAME`.`properties`.`id`		
                """
    },
    'units': {
        'headers': ['community_name', 'community_id', 'unit_id', 'unit_name', 'unit_type_id', 'square_feet', 'floor',
                    'bedroom_count',
                    'bathroom_count', 'half_bath_count', 'building_id', 'market_rent_amount'],
        'query': """
            SELECT  `v_hlpr_unit_w_property`.`community` as `community_name`,
                `v_hlpr_unit_w_property`.`property_id` as `community_id`, 
                `v_hlpr_unit_w_property`.`id` as `unit_id`,
                `v_hlpr_unit_w_property`.`name` as `unit_name`, 
                `v_hlpr_unit_w_property`.`unit_type_id`,
                `v_hlpr_unit_w_property`.`square_feet`,
                if(left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1) regexp('[[:digit:]]'),left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1),null) as `floor`,
                floor(`v_hlpr_unit_w_property`.`bedrooms`) as `bedroom_count`,
                floor(`v_hlpr_unit_w_property`.`bathrooms`) as `bathroom_count`,
                ceiling(mod(`v_hlpr_unit_w_property`.`bathrooms`,1)) as `half_bath_count`,
                `v_hlpr_unit_w_property`.`building_id`,
                `v_hlpr_unit_w_property`.`market_rent_amount`
            FROM 	`DATABASE_NAME`.`v_hlpr_unit_w_property`
        """
    },
    'units_by_community': {
        'headers': ['community_name', 'community_id', 'unit_id', 'unit_name', 'unit_type_id', 'unit_type',
                    'square_feet', 'floor',
                    'bedroom_count', 'bathroom_count', 'half_bath_count', 'building_id', 'market_rent_amount',
                    'rent_amount', 'vacate_date', 'leasable', 'unit_status'],
        'query': """  
            SELECT 
                `v_hlpr_unit_w_property`.`community` as `community_name`,
                `v_hlpr_unit_w_property`.`property_id` as `community_id`,
                `v_hlpr_unit_w_property`.`id` as `unit_id`,
                `v_hlpr_unit_w_property`.`name` as `unit_name`, 
                `v_hlpr_unit_w_property`.`unit_type_id`,
                `unit_types`.`name`,
                `v_hlpr_unit_w_property`.`square_feet`,
                if(left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1) regexp('[[:digit:]]'),left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1),null) as `floor`,
                floor(`v_hlpr_unit_w_property`.`bedrooms`) as `bedroom_count`,
                floor(`v_hlpr_unit_w_property`.`bathrooms`) as `bathroom_count`,
                ceiling(mod(`v_hlpr_unit_w_property`.`bathrooms`,1)) as `half_bath_count`,
                `v_hlpr_unit_w_property`.`building_id`,
                `v_hlpr_unit_w_property`.`market_rent_amount`,
                `v_hlpr_unit_w_property`.`rent_amount`,
                `v_hlpr_unit_w_property`.`vacate_date`,
                `v_hlpr_unit_w_property`.`leasable`,
                `v_hlpr_unit_w_property`.`status` as `unit_status`
            FROM 	`DATABASE_NAME`.`v_hlpr_unit_w_property`
             JOIN `DATABASE_NAME`.unit_types ON v_hlpr_unit_w_property.unit_type_id = unit_types.id
            WHERE 	(ISNULL(`v_hlpr_unit_w_property`.`deleted_at`) AND
            (`v_hlpr_unit_w_property`.`property_id` = %(community_id)s))		
        """
    },
    'units_by_id': {
        'headers': ['community_name', 'community_id', 'unit_id', 'unit_name', 'unit_type_id', 'unit_type_name',
                    'square_feet', 'floor',
                    'bedroom_count',
                    'bathroom_count', 'half_bath_count', 'building_id', 'market_rent_amount'],
        'query': """
            SELECT  `v_hlpr_unit_w_property`.`community` as `community_name`,
                `v_hlpr_unit_w_property`.`property_id` as `community_id`, 
                `v_hlpr_unit_w_property`.`id` as `unit_id`,
                `v_hlpr_unit_w_property`.`name` as `unit_name`, 
                `v_hlpr_unit_w_property`.`unit_type_id`,
                `unit_types`.`name`,
                `v_hlpr_unit_w_property`.`square_feet`,
                if(left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1) regexp('[[:digit:]]'),left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1),null) as `floor`,
                floor(`v_hlpr_unit_w_property`.`bedrooms`) as `bedroom_count`,
                floor(`v_hlpr_unit_w_property`.`bathrooms`) as `bathroom_count`,
                ceiling(mod(`v_hlpr_unit_w_property`.`bathrooms`,1)) as `half_bath_count`,
                `v_hlpr_unit_w_property`.`building_id`,
                `v_hlpr_unit_w_property`.`market_rent_amount`
            FROM 	`DATABASE_NAME`.`v_hlpr_unit_w_property`
            JOIN `DATABASE_NAME`.unit_types ON v_hlpr_unit_w_property.unit_type_id = unit_types.id
            WHERE 	(ISNULL(`v_hlpr_unit_w_property`.`deleted_at`)  AND
            (`v_hlpr_unit_w_property`.`id` = %(unit_id)s))				
        """
    },
    'units_by_community_unitavailability': {
        'headers': ['community_name', 'community_id', 'address', 'address2', 'city', 'state', 'zip', 'email',
                    'phone', 'fax', 'speed_dial', 'unit_id', 'unit_name', 'unit_type', 'square_feet', 'floor',
                    'bedroom_count', 'bathroom_count', 'half_bath_count', 'building_id', 'market_rent_amount',
                    'rent_amount', 'vacate_date', 'available_date', 'valid_starting', 'unit_status', 'virtual_tour_url',
                    'image_url'],
        'query': """
            SELECT
                `v_hlpr_unit_w_property`.`community` as `community_name`,
                `v_hlpr_unit_w_property`.`property_id` as `community_id`,
                `properties`.`address`,
                `properties`.`address2`,
                `properties`.`city`,
                `properties`.`state`,
                `properties`.`postal` as `zip`,
                `properties`.`email`,
                `properties`.`phone`,
                `properties`.`fax`,
                `properties`.`speed_dial`,
                `v_hlpr_unit_w_property`.`id` as `unit_id`,
                `v_hlpr_unit_w_property`.`name` as `unit_name`,
                `unit_types`.`name`,
                `v_hlpr_unit_w_property`.`square_feet`,
                if(left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1) regexp('[[:digit:]]'),left(replace(replace(`v_hlpr_unit_w_property`.`floor`,'S','2'),'F','1'),1),null) as `floor`,
                floor(`v_hlpr_unit_w_property`.`bedrooms`) as `bedroom_count`,
                floor(`v_hlpr_unit_w_property`.`bathrooms`) as `bathroom_count`,
                ceiling(mod(`v_hlpr_unit_w_property`.`bathrooms`,1)) as `half_bath_count`,
                `v_hlpr_unit_w_property`.`building_id`,
                `v_hlpr_unit_w_property`.`market_rent_amount`,
                `v_hlpr_unit_w_property`.`rent_amount`,
                `v_hlpr_unit_w_property`.`vacate_date`,
                `units`.`available_date` as `available_date`,
                `units`.`created_at` as `valid_starting`,
                `v_hlpr_unit_w_property`.`status` as `unit_status`,
                `website_floorplans`.`virtual_tour_url`, 
                concat('https://madera-newco.s3.us-west-2.amazonaws.com/',`website_floorplans`.`image`) as `image_url`
            FROM 	`DATABASE_NAME`.`v_hlpr_unit_w_property`
                JOIN `DATABASE_NAME`.`unit_types` ON `v_hlpr_unit_w_property`.`unit_type_id` = `unit_types`.`id`
                JOIN `DATABASE_NAME`.`units` ON `v_hlpr_unit_w_property`.`id` = `units`.`id`
                JOIN `DATABASE_NAME`.`properties` ON `properties`.`id` = `v_hlpr_unit_w_property`.`property_id`
                LEFT JOIN `DATABASE_NAME`.`website_floorplans` on `website_floorplans`.`unit_type_id` = `v_hlpr_unit_w_property`.`unit_type_id`
             WHERE 	(ISNULL(`v_hlpr_unit_w_property`.`deleted_at`) AND
            (`v_hlpr_unit_w_property`.`property_id` = %(community_id)s))		
        """
    },
    'unit_amenities_by_community': {
        'headers': [
            'community_id', 'community_name', 'unit_id', 'unit_name', 'amenity_name', 'amenity_value'
        ],
        'query': """
            SELECT `v_hlpr_unit_amenities`.`community_id` as `community_id`,
            `properties`.`name` as `community_name`,
            `v_hlpr_unit_amenities`.`unit_id` as `unit_id`,
            `v_hlpr_unit_w_property`.`name` as `unit_name`,
            `v_hlpr_unit_amenities`.`amenity_name` as `amenity_name`,
            `v_hlpr_unit_amenities`.`amenity_value` as `amenity_value`
            from	`DATABASE_NAME`.`v_hlpr_unit_amenities`
            JOIN `DATABASE_NAME`.`properties` ON `v_hlpr_unit_amenities`.`community_id` = `properties`.`id`
            JOIN `DATABASE_NAME`.`v_hlpr_unit_w_property` ON `v_hlpr_unit_w_property`.`id` = `v_hlpr_unit_amenities`.`unit_id`		
            where community_id = %(community_id)s
        """
    },
    'unit_amenities_by_unit': {
        'headers': [
            'community_id', 'community_name', 'unit_id', 'unit_name', 'amenity_name', 'amenity_value'
        ],
        'query': """
            select	`v_hlpr_unit_amenities`.`community_id` as `community_id`,
            `v_hlpr_unit_amenities`.`unit_id` as `unit_id`,
            `v_hlpr_unit_amenities`.`amenity_name` as `amenity_name`,
            `v_hlpr_unit_amenities`.`amenity_value` as `amenity_value`
            from	`DATABASE_NAME`.`v_hlpr_unit_amenities`
            where unit_id = %(db_unit_id)s;
        """
    },
    'unit_amenities': {
        'headers': [
            'community_id', 'unit_id', 'amenity_name', 'amenity_value'],
        'query': """
            SELECT 
                `buildings`.`property_id` AS `community_id`,
                `units`.`id` AS `unit_id`,
                `amenities`.`name` AS `amenity_name`,
                `amenities_property`.`value` AS `amenity_value`
            FROM 
                ((((`units`
                JOIN `DATABASE_NAME`.`amenities_unit` ON ((`amenities_unit`.`unit_id` = `units`.`id`)))
                JOIN `DATABASE_NAME`.`amenities_property` ON ((`amenities_unit`.`amenities_property_id` = `amenities_property`.`id`)))
                JOIN `DATABASE_NAME`.`amenities` ON ((`amenities_property`.`amenities_id` = `amenities`.`id`)))
                JOIN `DATABASE_NAME`.`buildings` ON ((`buildings`.`id` = `units`.`building_id`)))
            WHERE
                (ISNULL(`units`.`deleted_at`)
                AND (`amenities_property`.`value` > 0)
                AND (`buildings`.`property_id` = %(db_community_id)s)); 
        """
    },
    'fetch_community_name': {
        'headers': ['community_name'],
        'query': """SELECT `properties`.`name`as `community_name`
                    FROM `DATABASE_NAME`.`properties`
                    WHERE `properties`.`id` = %(community_id)s;	
                """
    },
    'unit_name_by_unit_id': {
        'headers': ['unit_name'],
        'query': """
            SELECT
                `v_hlpr_unit_w_property`.`name` as `unit_name`     
            FROM 	`DATABASE_NAME`.`v_hlpr_unit_w_property`
            WHERE 	`deleted_at` is null and `id` = %(db_unit_id)s;		
        """
    },
    'units_count_by_community': {
        'headers': ['unit_count'],
        'query': """ 
            SELECT   
                count(`v_hlpr_unit_w_property`.`id`) as `unit_count`
            FROM 	`DATABASE_NAME`.`v_hlpr_unit_w_property`
            WHERE `property_id` = %(db_community_id)s;		
        """
    },
    'get_customer_events': {
        'headers': ['event_type', 'event_id', 'event_date', 'created_at', 'person_id', 'property_id'],
        'query': """
        select * from (select "move_in_events" `type`, concat("MIE",move_in_events.id_move_in_events) `id`, 
        move_in_events.movein_date `date`, move_in_events.created_at, residents.person_id `persons.id`, 
        residents.property_id from `DATABASE_NAME`.move_in_events JOIN `DATABASE_NAME`.resident_events on 
        move_in_events.id_move_in_events = resident_events.eventable_id and 
        resident_events.eventable_type = 'App\\\\MoveInEvent' JOIN `DATABASE_NAME`.residents on resident_events.resident_id = residents.id
        WHERE residents.deleted_at is null and resident_events.deleted_at is null and move_in_events.deleted_at is null
        UNION select "move_out_events" `type`, concat("MOE",move_out_events.id_move_out_events) `id`, 
        move_out_events.moveout_date `date`, move_out_events.created_at, residents.person_id `persons.id`, 
        residents.property_id from `DATABASE_NAME`.move_out_events JOIN `DATABASE_NAME`.resident_events on 
        move_out_events.id_move_out_events = resident_events.eventable_id and resident_events.eventable_type = 'App\\\\MoveOutEvent'
        JOIN `DATABASE_NAME`.residents on resident_events.resident_id = residents.id 
        WHERE residents.deleted_at is null and resident_events.deleted_at is null and move_out_events.deleted_at is null
        UNION select "notice_events" `type`, concat("NE",notice_events.id_notice_events) `id`, 
        notice_events.estimated_moveout_date `date`, notice_events.created_at, residents.person_id `persons.id`, 
        residents.property_id from `DATABASE_NAME`.notice_events JOIN `DATABASE_NAME`.resident_events on 
        notice_events.id_notice_events = resident_events.eventable_id and resident_events.eventable_type = 'App\\\\NoticeEvent'
        JOIN `DATABASE_NAME`.residents on resident_events.resident_id = residents.id WHERE residents.deleted_at is null and 
        resident_events.deleted_at is null and notice_events.deleted_at is null UNION select "unit_leases" `type`, 
        concat("UL",unit_leases.id) `id`, unit_leases.lease_start_date `date`, unit_leases.created_at, 
        residents.person_id `persons.id`, residents.property_id from `DATABASE_NAME`.unit_leases JOIN `DATABASE_NAME`.residents on 
        unit_leases.resident_id = residents.id WHERE residents.deleted_at is null UNION select "persons" `type`, 
        concat("PER",persons.id) `id`, null `date`, persons.created_at, id `persons.id`, persons.property_id from 
        `DATABASE_NAME`.persons WHERE persons.deleted_at is null UNION select "applicants" `type`, concat("APP",applicants.id) `id`, 
        null `date`, applicants.created_at, applicants.person_id `persons.id`, applicants.property_id from `DATABASE_NAME`.applicants
        WHERE applicants.deleted_at is null UNION select "residents" `type`, concat("RES",residents.id) `id`, 
        null `date`, residents.created_at, residents.person_id `persons.id`, residents.property_id from `DATABASE_NAME`.residents 
        WHERE residents.deleted_at is null)events WHERE events.property_id = %(community_id)s and 
        events.created_at BETWEEN %(start_date)s and %(end_date)s;
        """
    },

    'get_all_units': {
        'headers': ['community_id', 'unit_id', 'unit_type_id', 'square_feet', 'bedroom_count', 'bathroom_count',
                    'market_rent_amount', 'rent_amount', 'occupancy_status', 'lease_status', 'unit_name',
                    'is_active'],
        'query': """
        select units.property_id, max(units.id) `id`,max(units.unit_type_id) `unit_type_id`,max(units.square_feet) `square_feet`,
        max(units.bedrooms) `bedrooms`,max(units.bathrooms) `bathrooms`,max(units.market_rent_amount) `market_rent_amount`
        ,max(units.rent_amount) `rent_amount`
        ,if((max(per.first_name) is null and max(per.last_name) is null) or (max(units.status) in
         ("", "Down", "Shop", "Rehab", "Model")), "Vacant", "Occupied") `occupancy_status`,if(max(units.status) in 
         ("", "Down", "Shop", "Rehab", "Model"), max(units.status),if(max(futureMoveIn.move_in_resident) is not null, 
         "Reserved",if(max(res.move_out_date) is not null, "On Notice",if(max(per.first_name) is not null or 
         max(per.last_name) is not null, "Leased",if(max(units.ready_to_show) = 1, "Available",
         if(max(units.ready_to_show) = 0, "Not Ready", "")))))) `lease_status`,units.name `unit_name`,if(max(units.status) 
         in ("", "Down", "Shop", "Rehab", "Model"), 0, 1) `is_active` from (SELECT residents.id,transfer_resident,
         residents.person_id,(SELECT unit_id FROM `DATABASE_NAME`.unit_leases ul WHERE ul.resident_id = residents.id and 
         transfer_resident = 0 ORDER BY created_at desc LIMIT 1)last_lease_unit_id,IFNULL((SELECT 
         move_in_events.movein_date FROM `DATABASE_NAME`.resident_events LEFT JOIN `DATABASE_NAME`.move_in_events ON 
         resident_events.eventable_id = move_in_events.id_move_in_events WHERE resident_events.deleted_at IS NULL 
         AND resident_events.eventable_type = "App\\\\MoveInEvent" AND resident_events.resident_id = residents.id 
         AND move_in_events.deleted_at IS NULL ORDER BY resident_events.id_resident_events desc LIMIT 1),(SELECT 
         move_in_date FROM `DATABASE_NAME`.unit_leases ul WHERE ul.resident_id = residents.id ORDER BY created_at desc LIMIT
          1))move_in_date,(SELECT eventable_type FROM `DATABASE_NAME`.resident_events WHERE deleted_at IS NULL AND 
        resident_events.resident_id = residents.id ORDER BY id_resident_events DESC LIMIT 1)event_type,(SELECT id FROM 
        `DATABASE_NAME`.unit_leases WHERE unit_id = last_lease_unit_id AND transfer_resident = 1 LIMIT 1)from_transfer,(SELECT
        IF(move_out_events.moveout_date IS NOT NULL, move_out_events.moveout_date, notice_events.estimated_moveout_date)
        FROM `DATABASE_NAME`.resident_events JOIN (SELECT resident_id `resident_id`, MAX(id_resident_events) `id` FROM 
        `DATABASE_NAME`.resident_events WHERE deleted_at IS NULL GROUP BY resident_id) lastEvent ON 
        resident_events.id_resident_events = lastEvent.id LEFT JOIN `DATABASE_NAME`.move_out_events ON 
        resident_events.eventable_type = "App\\\\MoveOutEvent" AND 
        resident_events.eventable_id = move_out_events.id_move_out_events AND move_out_events.deleted_at IS NULL
        LEFT JOIN `DATABASE_NAME`.notice_events ON resident_events.eventable_type = "App\\\\NoticeEvent" AND 
        resident_events.eventable_id = notice_events.id_notice_events AND notice_events.deleted_at IS NULL
        WHERE resident_events.deleted_at IS NULL AND resident_events.resident_id = residents.id)move_out_date FROM 
        `DATABASE_NAME`.residents WHERE residents.deleted_at IS NULL HAVING move_in_date <= curdate() and 
        (move_out_date is null or event_type = "App\\\\NoticeEvent" or (event_type = "App\\\\MoveOutEvent" and 
        move_out_date > curdate())))res RIGHT JOIN `DATABASE_NAME`.units on res.last_lease_unit_id = units.id left join 
        `DATABASE_NAME`.applicants app on units.id = app.unit_id AND app.deleted_at is null AND app.status in 
        ("active","pending") left join  (SELECT move_in_events.movein_date ,unit_leases.unit_id,
        concat(persons.first_name, " ", persons.last_name) `move_in_resident`, unit_leases.actual_rent_amount FROM 
        `DATABASE_NAME`.move_in_events JOIN `DATABASE_NAME`.resident_events ON 
        resident_events.eventable_id = move_in_events.id_move_in_events AND eventable_type = "App\\\\MoveInEvent"	AND 
        resident_events.deleted_at IS NULL JOIN `DATABASE_NAME`.v_hlpr_residents res ON resident_events.resident_id = res.id
        AND res.deleted_at IS NULL JOIN `DATABASE_NAME`.unit_leases ON unit_leases.resident_id = res.id JOIN 
        `DATABASE_NAME`.persons on res.person_id = persons.id WHERE movein_date > curdate() AND move_in_events.deleted_at 
        IS NULL AND move_in_events.canceled_date IS NULL)futureMoveIn ON units.id = futureMoveIn.unit_id LEFT JOIN 
        `DATABASE_NAME`.unit_types on units.unit_type_id = unit_types.id and unit_types.deleted_at IS NULL LEFT JOIN 
        `DATABASE_NAME`.persons per ON res.person_id = per.id LEFT JOIN `DATABASE_NAME`.persons app_per ON 
        app.person_id = app_per.id WHERE units.deleted_at is null and app_per.deleted_at is null and 
        units.property_id = %(community_id)s GROUP BY units.name,units.property_id;
        """
    },
    'get_all_transactions': {
        'headers': ['transaction_id', 'transaction_posted_date', 'transaction_amount', 'transaction_type',
                    'transaction_notes', 'transaction_charge_code_id', 'transaction_charge_code_name', 'community_id'],
        'query': """
        select concat("T",trans.id) `id`, je.post_date, if(trans.has_override = 1, 
        if(is_credit = 1,trans.override_amount*-1,trans.override_amount), 
        if(is_credit = 1,trans.amount*-1,trans.amount)) `amount`,if(is_credit = 1, "credit", "debit") `transaction_type`,
         trans.notes, codes.id `charge_code_id`, codes.name `charge_code_name`, trans.property_id `community_id` FROM 
         `DATABASE_NAME`.ar_transactions trans JOIN `DATABASE_NAME`.resident_ledgers lgr ON 
         trans.resident_ledger_id = lgr.id JOIN `DATABASE_NAME`.journal_entries je on 
        trans.journal_entry_batches_id = je.journal_entry_batches_id JOIN `DATABASE_NAME`.accounting_charge_codes codes
        ON trans.charge_code_id = codes.id WHERE trans.property_id = %(community_id)s and 
        lgr.resident_id = %(resident_id)s and je.post_date BETWEEN %(start_date)s and %(end_date)s and 
        trans.deleted_at is null UNION select concat("P",pmts.id) `id`, je.post_date, pmts.amount*-1,"credit" 
        `transaction_type`, pmts.notes, null `charge_code_id`, null `charge_code_name`, pmts.property_id `community_id` 
        from `DATABASE_NAME`.ar_resident_payments pmts JOIN `DATABASE_NAME`.resident_ledgers lgr ON 
        pmts.resident_ledger_id = lgr.id JOIN `DATABASE_NAME`.journal_entries je on 
        pmts.journal_entry_batches_id = je.journal_entry_batches_id LEFT JOIN 
        `DATABASE_NAME`.ar_resident_payment_reversals pmt_rvs ON pmts.id = pmt_rvs.ar_resident_payment_id WHERE 
        pmts.property_id = %(community_id)s and lgr.resident_id = %(resident_id)s and je.post_date BETWEEN 
        %(start_date)s and %(end_date)s and pmts.deleted_at is null and pmt_rvs.id is null;	
        """

    },
    'get_charge_codes': {
        'headers': ['charge_code_id', 'charge_code_name', 'code_category', 'amount', 'community_id'],
        'query': """
        select codes.id, codes.name, code_cat.name `category`, if(code_prop.override_amount is not null,
         code_prop.override_amount, codes.amount) `amount`, code_prop.property_id from `DATABASE_NAME`.accounting_charge_codes codes 
         JOIN `DATABASE_NAME`.accounting_charge_code_property code_prop ON codes.id = code_prop.accounting_charge_code_id 
         JOIN `DATABASE_NAME`.accounting_charge_code_categories code_cat ON codes.accounting_charge_code_category_id = code_cat.id
         WHERE code_prop.property_id = %(community_id)s
        """
    },
    'get_properties': {
        'headers': ['property_id', 'property_name', 'address', 'city', 'state', 'zip', 'phone'],
        'query': """
        select id, name, address, city, state, postal, phone from `DATABASE_NAME`.properties where id = %(community_id)s
        """
    },
    'get_prospects': {
        'headers': ['prospect_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'postal',
                    'community_id',
                    'move_in_date', 'move_out_date', 'desired_bedrooms', 'additional_occupants', 'pets'],
        'query': """
            select prospects.id `prospect_id`, prospects.first_name, prospects.last_name, prospects.email, 
            prospects.phone, persons.address, persons.city, persons.state, persons.postal, 
            prospects.property_id,
            persons.move_in_date, persons.desired_move_date, persons.desired_bedrooms, persons.additional_occupants,
            persons.pets from `DATABASE_NAME`.prospects join `DATABASE_NAME`.persons on prospects.id = persons.prospect_id 
             WHERE prospects.property_id = %(community_id)s and prospects.created_at >= %(create_date)s
        """
    },

    'get_residents': {
        'headers': ['unit_name', 'unit_id', 'resident_id', 'prospect_id', 'first_name', 'last_name', 'ssn',
                    'date_of_birth', 'email', 'phone',
                    'address', 'city', 'state', 'postal', 'lease_start_date',
                    'lease_expiration_date', 'lease_id', 'is_active', 'move_in_date', 'move_out_date', 'community_id',
                    'resident_type'],
        'query': """
       select distinct units.name `unit_name`, units.id `unit_id`, res_and_co_res.resident_id, res_and_co_res.prospect_id, 
       res_and_co_res.first_name, res_and_co_res.last_name, res_and_co_res.ssn, res_and_co_res.dob, 
       res_and_co_res.email, res_and_co_res.phone, res_and_co_res.`address`, res_and_co_res.`city`, res_and_co_res.`state`, 
       res_and_co_res.`postal`, res_and_co_res.lease_start, res_and_co_res.lease_expire, res_and_co_res.lease_id, 
       res_and_co_res.is_active, res_and_co_res.move_in_date, res_and_co_res.move_out_date, res_and_co_res.property_id,
        res_and_co_res.res_type
       from (
       select res.id `resident_id`,persons.prospect_id,persons.first_name,persons.last_name,persons.ssn
       ,persons.dob,persons.email,persons.phone,if(persons.address = 'null',null,persons.address) `address`,
       if(persons.city = 'null',null,persons.city) `city`,if(persons.state = 'null',null,persons.state) `state`,
       if(persons.postal = 'null',null,persons.postal) `postal`,res.lease_start,res.lease_expire,res.lease_id,
       res.is_active,res.move_in_date,res.move_out_date,res.property_id,'Resident' `res_type` from(SELECT residents.id,
       residents.person_id,residents.property_id,IFNULL((
       SELECT move_in_events.movein_date FROM resident_events LEFT JOIN move_in_events ON 
       resident_events.eventable_id = move_in_events.id_move_in_events WHERE resident_events.deleted_at IS NULL AND 
       resident_events.eventable_type = 'App\\\\MoveInEvent' AND resident_events.resident_id = residents.id AND 
       move_in_events.deleted_at IS NULL ORDER BY resident_events.id_resident_events desc LIMIT 1),
       residents.move_in_date)move_in_date,
       (SELECT eventable_type FROM resident_events WHERE deleted_at IS NULL AND resident_events.resident_id = residents.id
       ORDER BY id_resident_events DESC LIMIT 1)event,
       (SELECT IF(move_out_events.moveout_date IS NOT NULL, move_out_events.moveout_date, 
       notice_events.estimated_moveout_date) FROM resident_events JOIN (
       SELECT resident_id `resident_id`, MAX(id_resident_events) `id` FROM resident_events WHERE deleted_at IS NULL
       GROUP BY resident_id) lastEvent ON resident_events.id_resident_events = lastEvent.id LEFT JOIN move_out_events ON 
       resident_events.eventable_type = 'App\\\\MoveOutEvent' AND 
       resident_events.eventable_id = move_out_events.id_move_out_events AND move_out_events.deleted_at IS NULL
       LEFT JOIN notice_events ON resident_events.eventable_type = 'App\\\\NoticeEvent' AND 
       resident_events.eventable_id = notice_events.id_notice_events AND notice_events.deleted_at IS NULL WHERE 
       resident_events.deleted_at IS NULL AND resident_events.resident_id = residents.id)move_out_date,
       (SELECT lease_start_date FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by is_active desc, 
       lease_expiration_date desc limit 1)lease_start,
       (SELECT lease_expiration_date FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by 
       is_active desc, lease_expiration_date desc limit 1)lease_expire,
       (SELECT unit_leases.id FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by 
       is_active desc, lease_expiration_date desc limit 1)lease_id,
       (SELECT unit_leases.is_active FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by is_active desc,
       lease_expiration_date desc limit 1)is_active FROM residents WHERE residents.deleted_at IS NULL)res join 
       persons on res.person_id = persons.id where persons.deleted_at is null and res.property_id = %(community_id)s
       AND res.move_in_date >= %(move_in_date)s and (res.move_out_date is null OR res.event = 'App\\\\NoticeEvent' 
       OR %(move_out_date)s is null OR res.move_out_date <= %(move_out_date)s)
       union all
       select res.id `resident_id`,null `prospect_id`,co_app.first_name,co_app.last_name,
       if(co_app.ssn like 'e%%', null, co_app.ssn),co_app.birth_date,co_app.email,co_app.phone
       ,null `address`,null `city`,null `state`,null `postal`,res.lease_start,res.lease_expire,res.lease_id,
       res.is_active,res.move_in_date,res.move_out_date,res.property_id,'Co-Resident' `res_type` from
       (SELECT residents.id,residents.person_id,residents.property_id,IFNULL((SELECT move_in_events.movein_date FROM 
       resident_events LEFT JOIN move_in_events ON resident_events.eventable_id = move_in_events.id_move_in_events
       WHERE resident_events.deleted_at IS NULL AND resident_events.eventable_type = 'App\\\\MoveInEvent' AND 
       resident_events.resident_id = residents.id AND move_in_events.deleted_at IS NULL ORDER BY 
       resident_events.id_resident_events desc LIMIT 1),residents.move_in_date)move_in_date,(SELECT eventable_type FROM 
       resident_events WHERE deleted_at IS NULL AND resident_events.resident_id = residents.id ORDER BY 
       id_resident_events DESC LIMIT 1)event,
       (SELECT IF(move_out_events.moveout_date IS NOT NULL, move_out_events.moveout_date, 
       notice_events.estimated_moveout_date)FROM resident_events JOIN 
       (SELECT resident_id `resident_id`, MAX(id_resident_events) `id` FROM resident_events WHERE deleted_at IS NULL 
       GROUP BY resident_id) lastEvent ON resident_events.id_resident_events = lastEvent.id LEFT JOIN move_out_events ON
       resident_events.eventable_type = 'App\\\\MoveOutEvent' AND 
       resident_events.eventable_id = move_out_events.id_move_out_events AND move_out_events.deleted_at IS NULL
       LEFT JOIN notice_events ON resident_events.eventable_type = 'App\\\\NoticeEvent' AND 
       resident_events.eventable_id = notice_events.id_notice_events AND notice_events.deleted_at IS NULL 
       WHERE resident_events.deleted_at IS NULL AND resident_events.resident_id = residents.id)move_out_date,
       (SELECT lease_start_date FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by is_active desc, 
       lease_expiration_date desc limit 1)lease_start,
       (SELECT lease_expiration_date FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by is_active 
       desc, lease_expiration_date desc limit 1)lease_expire,
       (SELECT unit_leases.id FROM unit_leases WHERE unit_leases.resident_id = residents.id ORDER by is_active desc, 
       lease_expiration_date desc limit 1)lease_id,(SELECT unit_leases.is_active FROM unit_leases WHERE 
       unit_leases.resident_id = residents.id ORDER by is_active desc, lease_expiration_date desc limit 1)is_active FROM
       residents WHERE residents.deleted_at IS NULL)res left JOIN co_applicant co_app on co_app.applicant_id = res.id
       where co_app.first_name is not null and co_app.deleted_at is null and res.property_id = %(community_id)s
        AND res.move_in_date >= %(move_in_date)s and (res.move_out_date is null OR res.event = 'App\\\\NoticeEvent' 
        OR %(move_out_date)s is null OR res.move_out_date <= %(move_out_date)s))res_and_co_res
        join
        unit_leases on unit_leases.resident_id = res_and_co_res.resident_id
        join
        units on unit_leases.unit_id = units.id
        WHERE units.deleted_at is null and `first_name` != 'iNCHNGzByPjhApvn7XBD'
    ORDER BY CAST(units.name as unsigned), units.name, `res_type` desc """
    }

}