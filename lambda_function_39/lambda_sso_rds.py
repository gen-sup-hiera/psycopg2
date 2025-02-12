'''
Triggered by SQS with message from IAM Identity Center
'''

import json
import os
import sys
import boto3
import logging
import psycopg2
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_roles_map = json.loads(os.environ['db_roles_map'])


def connect_rds(db_host, db_password, db_username, db_port, db_name, username, db_action, db_role):
    role = db_roles_map.get(db_role)
    logger.info("Connecting to RDS instance " + db_host)
    try:
        rds_connection = psycopg2.connect(
            host = db_host,
            port = db_port,
            user = db_username,
            password = db_password,
            dbname=db_name
        )
        cursor = rds_connection.cursor()
        logger.info("Executing SQL scripts")
        check_user_cmd = ("SELECT COUNT(*) as NUM_ROWS FROM pg_roles WHERE rolname = '%s'" % (username))
        create_user_cmd=(f'CREATE USER "{username}" WITH LOGIN')
        grant_roles_cmd=(f'GRANT rds_iam, {role} TO "{username}"')
        revoke_role_cmd=(f'REVOKE {role} FROM "{username}"')
        delete_user_cmd=(f'DROP USER IF EXISTS "{username}"')
        roles_count_query = (f'''
                             SELECT COUNT(*)
                             FROM pg_auth_members
                             INNER JOIN pg_roles ON pg_roles.oid = pg_auth_members.member
                             WHERE rolname = '{username}'
                            ''')
        cursor.execute(check_user_cmd)
        result = cursor.fetchone()[0]

        if result == 0 and db_action == 'add':
            print(f'User {username} will be created in RDS DB instance')
            try: 
                cursor.execute(create_user_cmd)
                cursor.execute(grant_roles_cmd)
                rds_connection.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(f'An error occured: {error}')
                raise error
        
        if result == 1 and db_action == 'remove':
            try:
                logger.info("Revoking user roles")
                cursor.execute(revoke_role_cmd)
                cursor.execute(roles_count_query)
                remaining_roles = cursor.fetchone()
                rds_connection.commit()
                if remaining_roles[0] == 1:
                    print(f'User {username} will be deleted from RDS DB instance')
                    cursor.execute(delete_user_cmd)
                    rds_connection.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(f'An error occured: {error}')
                raise error
        
        if result == 1 and db_action == 'add':
            try:
                cursor.execute(grant_roles_cmd)
                rds_connection.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(f'An error occured: {error}')
                raise error

    except psycopg2.Error as e:
        logger.error(e)
        sys.exit()
    cursor.close()
    rds_connection.close()


def get_db_creds(secret_name):
    logger.info("Retrieving master password to RDS from AWS Secrets Manager")
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )
    try:
        secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logger.error("Failed to get RDS secrets")
        logger.error(e)

    if 'SecretString' in secret_value_response:
        global db_password
        db_password = secret_value_response['SecretString']
    else:
        logger.info("No database credentials found")
        return None


def lambda_handler(event, context):
    message_attributes = event['Records'][0]['messageAttributes']
    environment = message_attributes['environment']['stringValue']
    username = message_attributes['username']['stringValue']
    db_action = message_attributes['db_action']['stringValue']
    db_role = message_attributes['db_role']['stringValue']
    # Database connection parameters
    db_username = "lims"
    db_host = "lims-db." + environment
    db_port = "5432"
    db_name = "lims"
    secret_name = "/" + environment + "/live/lims-db-root-pass"
    logger.info("RDS DB instance is " + db_host)
    # Run secret_name and connect_rds functions
    get_db_creds(secret_name)
    connect_rds(db_host, db_password, db_username, db_port, db_name, username, db_action, db_role)
