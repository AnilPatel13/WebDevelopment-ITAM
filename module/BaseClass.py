from helper.MysqlClient import *


class BaseClass:
    __conn = None

    def __init__(self):
        conn = MysqlClient()
        self.__conn = conn

    def check_user_exist(self, data_list):
        sql_query = "select * from user where first_name = %s and middle_name = %s and last_name = %s and" \
                    " email_address = %s and birthdate = %s"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        if len(account) > 0:
            return True
        return False

    def check_email_exist(self, data_list):
        sql_query = "select * from user where lower(email_address) = %s"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        if len(account) > 0:
            return True
        return False

    def insert_new_user(self, data_list):
        sql_query = """INSERT INTO itam.user (first_name, middle_name, last_name, email_address, contact_no,
         birthdate, password, otp_encoder, qr_code, role, status, creation_date, updated_date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s,
        %s,'view', 'approved', current_timestamp(),current_timestamp())"""
        row_inserted = self.__conn.execute_insert(sql_query, data_list, raise_no_data_error=False)
        if row_inserted > 0:
            return True
        return False

    def get_login_data(self, data_list):
        sql_query = "select * from user where email_address = %s and password = %s"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return account

    def update_password(self, data_list):
        sql_query = "update itam.user set password = %s, updated_date=current_timestamp() where email_address = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def get_user_data(self, data_list):
        sql_query = "select * from user where first_name = %s and employee_id = %s"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return account

    def get_Security_control(self, data_list):
        sql_query = "select * from itam.stockroom_security_type"
        security_control = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return security_control

    def add_new_stockroom_entry(self, data_list):
        sql_query = """INSERT INTO itam.stockroom_management (building, room_number, address, security_control,
                 stockroom_manager, security_control_id, creation_date, updated_date) VALUES(%s, %s, %s, %s, %s, %s,
                 current_timestamp(),current_timestamp())"""
        row_inserted = self.__conn.execute_insert(sql_query, data_list, raise_no_data_error=False)
        if row_inserted > 0:
            return True
        return False

    def get_Stockroom_data(self, data_list):
        sql_query = "select * from itam.stockroom_management"
        stockroom_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return stockroom_data

    def update_stockroom(self, data_dict, security_control):
        sql_query = "update itam.stockroom_management set "
        data = []
        security_control_id = None
        if len(data_dict) > 1:
            for key, value in data_dict.items():
                if value not in (None, "") and key not in ("stockroom_id"):
                    sql_query = sql_query + key + "= %s,"
                    data.append(value)

        for item in security_control:
            if item['security_control_type'] == data_dict['security_control']:
                security_control_id = item['stockroom_security_type_id']

        sql_query = sql_query + "security_control_id = %s, updated_date = current_timestamp() where stockroom_id = %s"
        data.append(security_control_id)
        data.append(data_dict['stockroom_id'])

        row_updated = self.__conn.execute_update(sql_query, data, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def get_asset_state(self, data_list):
        sql_query = "select * from itam.asset_state"
        asset_state = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_state

    def get_asset_condition(self, data_list):
        sql_query = "select * from itam.asset_condition"
        asset_condition = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_condition

    def get_stockroom(self, data_list):
        sql_query = "select * from itam.stockroom_management"
        stockroom_mgmt = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return stockroom_mgmt

    def get_employee_data(self, data_list):
        sql_query = "select distinct employee_id from itam.user"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return account

    def get_asset_state_id(self, data_list):
        sql_query = "select * from itam.asset_state where asset_state = %s"
        asset_state = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_state

    def get_stockroom_details(self, data_list):
        sql_query = "select * from itam.stockroom_management where 	building = %s and room_number = %s"
        stockroom_detail = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return stockroom_detail

    def get_asset_condition_by_id(self, data_list):
        sql_query = "select * from itam.asset_condition where condition_state = %s"
        asset_condition = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_condition

    def get_employee_data_id(self, data_list):
        sql_query = "select * from itam.user where employee_id = %s"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return account

    def add_new_asset_entry(self, data_list):
        sql_query = """
        INSERT INTO itam.Asset (`serial_no`, `asset_state_id`, `asset_tag`, `asset_state`, `asset_location`,
         `asset_room_no`, `stockroom_id`, `asset_condition`, `asset_condition_id`, `asset_model`, `assigned_to`,
          `employee_id`, `creation_date`, `update_date`) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s,
                 current_timestamp(),current_timestamp())
        """
        row_inserted = self.__conn.execute_insert(sql_query, data_list, raise_no_data_error=False)
        if row_inserted > 0:
            return True
        return False

    def get_asset_data(self, data_list):
        sql_query = "select * from itam.Asset"
        asset_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_data

    def get_asset_data_by_srn_tag(self, data_list):
        sql_query = "select * from itam.Asset where serial_no = %s and asset_tag = %s and asset_model = %s and " \
                    " asset_location = %s"
        asset_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_data

    def asset_retirement_insert_delete(self, data_dict):
        query_sql = {"query1": """
        INSERT INTO itam.asset_retirement (`serial_no`, `asset_tag`, `asset_model`,
         `is_warehouse_disposal`, `stockroom_id`, `disposal_date`, `creation_date`, `update_date`)
          VALUES (%s, %s, %s, %s,%s, %s, current_timestamp(), current_timestamp())
        """,
                     "query2": """
                delete from itam.Asset where serial_no = %s and asset_tag = %s and asset_model = %s and
                stockroom_id = %s and asset_location = %s
                """}

        query_dict = {}

        for key, data in data_dict.items():
            query_dict[query_sql[key]] = data
        try:
            status = self.__conn.execute_transaction(query_dict=query_dict)
            return status
        except Exception as ex:
            pass

    def get_request_priority(self, data_list):
        sql_query = "select * from itam.priority"
        request_priority = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return request_priority

    def get_asset_request(self, data_list):
        sql_query = "select * from itam.Asset where asset_state = 'instock' and assigned_to is null" \
                    " and employee_id is null"
        asset_details = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_details

    def get_request_priority_id(self, data_list):
        sql_query = "select * from itam.priority where priority_type = %s"
        request_priority = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return request_priority

    def get_asset_data_by_srn_tag_model(self, data_list):
        sql_query = "select * from itam.Asset where serial_no = %s and asset_tag = %s and asset_model = %s"
        asset_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_data

    def get_max_ticket_no(self, data_list):
        sql_query = "select max(ticket_no) + 1 from itam.asset_request"
        ticket_no = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return ticket_no

    def get_max_support_ticket_no(self, data_list):
        sql_query = "select max(support_ticket_no) + 1 from itam.support"
        ticket_no = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return ticket_no

    def asset_request_fulfillment(self, data_dict):
        query_sql = {"query1": """
        INSERT INTO itam.asset_request (`ticket_no`, `employee_name`, `employee_id`, `priority_id`,
         `request_priority`, `asset_id`, `asset_model`, `asset_tag`, `asset_serial_no`, `number_of_units`,
          `additional_comments`, `creation_date`, `update_date`) VALUES
           ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp(), current_timestamp())
        """,
                     "query2": """
        INSERT INTO itam.request_fulfillment (`ticket_no`, `employee_id`, `employee_name`,
         `request_priority`, `asset_id`, `asset_model`, `asset_tag`, `asset_serial_no`, `no_of_units`, `service_request_type`,
          `support_service`, `additional_comments`, `status`, `creation_date`, `update_date`) VALUES
           (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp(), current_timestamp())
        """}

        query_dict = {}

        for key, data in data_dict.items():
            query_dict[query_sql[key]] = data
        try:
            status = self.__conn.execute_transaction(query_dict=query_dict)
            return status
        except Exception as ex:
            pass

    def get_asset_request_all(self, data_list):
        sql_query = "select * from itam.Asset"
        asset_details = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_details

    def asset_support_fulfillment(self, data_dict):

        query_sql = {"query1": """
        
        INSERT INTO itam.support (`support_ticket_no`, `employee_id`, `employee_name`, `request_priority`,
         `request_id`, `asset_id`, `asset_model`, `asset_tag`, `asset_serial_no`, `support_type`,
          `additional_comments`, `creation_date`, `update_date`)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp(), current_timestamp())
        """,
                     "query2": """
        INSERT INTO itam.request_fulfillment (`ticket_no`, `employee_id`, `employee_name`,
         `request_priority`, `asset_id`, `asset_model`, `asset_tag`, `asset_serial_no`, `no_of_units`, `service_request_type`,
          `support_service`, `additional_comments`, `status`, `creation_date`, `update_date`) VALUES
           (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp(), current_timestamp())
        """}
        query_dict = {}

        for key, data in data_dict.items():
            query_dict[query_sql[key]] = data
        try:
            status = self.__conn.execute_transaction(query_dict=query_dict)
            return status
        except Exception as ex:
            pass

    def get_request_fulfillment_data(self, data_list):
        sql_query = "select * from itam.request_fulfillment"
        request_fulfillment_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return request_fulfillment_data

    def get_request_fulfillment_by_ticketno(self, data_list):
        sql_query = "select * from itam.request_fulfillment where ticket_no = %s"
        request_fulfillment_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return request_fulfillment_data

    def update_asset_fulfillment(self, data_dict):

        query_sql = {"query1": """

        update itam.asset set assigned_to = %s, employee_id = %s, update_date=current_timestamp() where asset_id = %s
        """,
                     "query2": """
        update itam.request_fulfillment set status = %s, update_date=current_timestamp() where ticket_no = %s
        """}
        query_dict = {}

        for key, data in data_dict.items():
            query_dict[query_sql[key]] = data
        try:
            status = self.__conn.execute_transaction(query_dict=query_dict)
            return status
        except Exception as ex:
            pass


    def update_asset_fulfillment_process(self, data_list):
        sql_query = "update itam.request_fulfillment set status = %s, update_date=current_timestamp() where ticket_no = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def get_all_asset_count(self, data_list):
        sql_query = "select COUNT(1) from itam.Asset"
        asset_count = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return asset_count

    def get_all_asset_retired_count(self, data_list):
        sql_query = "select COUNT(1) from itam.asset_retirement"
        asset_retirement_count = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return asset_retirement_count

    def get_all_asset_request_count(self, data_list):
        sql_query = "select COUNT(1) from itam.asset_request"
        asset_request_count = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return asset_request_count

    def get_all_support_count(self, data_list):
        sql_query = "select COUNT(1) from itam.support"
        support_ticket_count = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return support_ticket_count

    def get_all_request_fulfillment_count(self, data_list):
        sql_query = "select COUNT(1) from itam.request_fulfillment"
        request_fulfillment_count = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return request_fulfillment_count

    def get_all_stockroom_count(self, data_list):
        sql_query = "select COUNT(1) from itam.stockroom_management"
        stockroom_count = self.__conn.execute_fetch_scalar(sql_query, data_list, raise_no_data_error=False)
        return stockroom_count

    def get_all_asset_details_7days(self, data_list):
        sql_query = """
                SELECT DATE_FORMAT(dummy.creation_date, '%%Y-%%m-%%d') as creation_date, IFNULL(summary.`count`,0) `count`
           FROM (
                SELECT DATE(NOW())-INTERVAL seq.seq DAY creation_date   
                  FROM (
                           SELECT 0 AS seq 
                             UNION ALL SELECT 1  UNION ALL SELECT 2 
                             UNION ALL SELECT 3  UNION ALL SELECT 4
                             UNION ALL SELECT 5  UNION ALL SELECT 6
                        ) seq 
                  ) dummy
           LEFT JOIN (
                SELECT DATE(i.creation_date) creation_date,
                       COUNT(*) `count`
                  FROM itam.Asset i
                  where DATE(i.creation_date) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                 GROUP BY DATE(i.creation_date)
               ) summary USING (creation_date)
           ORDER BY dummy.creation_date
                """
        asset_7days_details = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_7days_details

    def get_all_asset_request_fulfillment_365days(self, data_list):
        sql_query = """
        SELECT DATE_FORMAT(rf.creation_date,'%%b') as month ,count(rf.fulfillment_id) `count`
        FROM itam.request_fulfillment rf  
        WHERE DATE(rf.creation_date) > curdate() - interval 365 day 
        GROUP BY MONTH(rf.creation_date)
        order by MONTH(rf.creation_date) 
        """
        request_fulfillment_365days_details = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return request_fulfillment_365days_details

    def get_all_stockroom_counts(self, data_list):
        sql_query = """
        select sm.building,count(sm.building) `count`
        from itam.stockroom_management sm
        GROUP BY sm.building
        """
        stockroom_detail_count = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return stockroom_detail_count

    def get_all_support_request_count(self, data_list):
        sql_query = """
        SELECT DATE_FORMAT(rf.creation_date,'%%b') as month ,count(rf.service_request_type) `count`
        FROM itam.request_fulfillment rf  
        WHERE DATE(rf.creation_date) > curdate() - interval 365 day and rf.service_request_type = "Support_Request"
        GROUP BY MONTH(rf.creation_date)
        order by MONTH(rf.creation_date)
        """
        support_request_count_all = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return support_request_count_all


    def get_all_asset_request_ful_count(self, data_list):
        sql_query = """
        SELECT DATE_FORMAT(rm.creation_date,'%%b') as month ,count(rm.service_request_type) `count`
        FROM itam.request_fulfillment rm  
        WHERE DATE(rm.creation_date) > curdate() - interval 365 day and rm.service_request_type = "Asset_Request"
        GROUP BY MONTH(rm.creation_date)
        order by MONTH(rm.creation_date)
        """
        asset_request_ful_count_all = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return asset_request_ful_count_all

    def update_firstname(self, data_list):
        sql_query = "update itam.user set first_name = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def update_middlename(self, data_list):
        sql_query = "update itam.user set middle_name = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def update_lastname(self, data_list):
        sql_query = "update itam.user set last_name = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def change_birthdate(self, data_list):
        sql_query = "update itam.user set birthdate = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def change_email_address(self, data_list):
        sql_query = "update itam.user set email_address = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def change_contact_number(self, data_list):
        sql_query = "update itam.user set contact_no = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def get_user_roles_data(self, data_list):
        sql_query = "select * from itam.user where role='admin' and status='pending'"
        account = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return account

    def update_user_roles(self, data_list):
        sql_query = "update itam.user set role = 'admin', status = %s, updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def change_user_role(self, data_list):
        sql_query = "update itam.user set role = %s, status='pending', updated_date=current_timestamp() where employee_id = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False

    def change_user_qr_code(self, data_list):
        sql_query = "update itam.user set otp_encoder = %s, qr_code = %s, updated_date=current_timestamp()" \
                    " where employee_id = %s and email_address = %s"
        row_updated = self.__conn.execute_update(sql_query, data_list, raise_no_affected_row_error=False)
        if row_updated > 0:
            return True
        return False


    def get_request_fulfillment_data_by_employee_id(self, data_list):
        sql_query = "select * from itam.request_fulfillment where employee_id = %s and employee_name = %s"
        request_fulfillment_data = self.__conn.execute_fetch_all_dict(sql_query, data_list, raise_no_data_error=False)
        return request_fulfillment_data
