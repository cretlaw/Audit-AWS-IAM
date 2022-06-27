import boto3
from botocore.exceptions import ClientError
import click
import xlsxwriter
import os


def user_has_console_access(client,username):
    '''if user has login profile i.e. the user has password enabled and console access
     return Yes else No.'''

    try:
        client.get_login_profile(UserName=username)
        return 'Yes'
    except ClientError:
        return 'No'

def user_has_mfa_enabled(client,username):
    '''If user has MFA enabled return Yes else No.'''

    mfa_devices = client.list_mfa_devices(UserName=username)
    if mfa_devices['MFADevices']:
        return 'Yes'
    else:
        return 'No'

    
def write_to_spreadsheet(account,users):
    '''Writes user data to excel spreadsheet and stores it in audit-aws/downloads path.'''
    worksheet_name = account

    workbook_path = os.getcwd() + "/downloads"

    # Excel doesn't support timezones in datetimes. Set the tzinfo in the datetime/time object to None or use the 'remove_timezone'
    wb = xlsxwriter.Workbook(f"{workbook_path}/{worksheet_name}.xlsx", {"remove_timezone": True})

    
    sheet = wb.add_worksheet(worksheet_name)

    # Specifying style and date format
    heading_style = wb.add_format({"bold": True})
    date_format = wb.add_format({"num_format": "mmm d yyyy hh:mm AM/PM"})
   
    #setting sheet headers
    sheet.write(0, 0, "User Name", heading_style)
    sheet.write(0, 1, "Console Access", heading_style)
    sheet.write(0, 2, "MFA Enabled", heading_style)
    sheet.write(0, 3, "User Id", heading_style)
    sheet.write(0, 4, "User ARN", heading_style)
    sheet.write(0, 5, "User Create Date", heading_style)
    sheet.write(0, 6, "Directly Attached Managed Policies", heading_style)
    sheet.write(0, 7, "Directly Attached Inline Policies", heading_style)

    sheet.write(0, 8, "Group Name", heading_style)
    sheet.write(0, 9, "Group Attached Managed Policies", heading_style)
    sheet.write(0, 10, "Group Attached Inline Policies", heading_style)

    # write all users info for all of the groups
    row = 1
    for user in users:
        for col, item in enumerate(user):
            if col == 5:
                sheet.write(row, col, item, date_format)
            else:
                sheet.write(row,col,item)

        row += 1

    # Close and save sheet 
    wb.close()

    

@click.command()
@click.option("--access_key",'-ac', prompt=True, hide_input=True, required=True, help='AWS access key.')
@click.option("--secret_key",'-sc', prompt=True, hide_input=True, required=True, help='AWS secret key.')
def gather_iam_data(access_key, secret_key):
    '''Gather IAM data for AWS account associated with credentials provided.'''

   
    # Open up read access to AWS account IAM service
    client = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    
    # Get AWS account name 
    account = client.list_account_aliases()['AccountAliases'][0]
    
    #Get all the IAM users in the account.
    users = client.list_users()['Users']

    users_info = []
    for user in users:
        
        user_name = user['UserName']
        # get all the groups the IAM user belongs to
        groups = [group.get('GroupName') for group in client.list_groups_for_user(UserName=user_name)['Groups']]
        inline_group_policies, attached_group_policies = [], [] 
        for group in groups:
            #get all inline policies for each group the user belongs to
            inline_group_policies +=  [policy for policy in client.list_group_policies(GroupName=group).get('PolicyNames')]

            #get all attached policies for each group the user belongs to
            attached_group_policies += [policy.get('PolicyName') for policy in client.list_attached_group_policies(GroupName=group).get('AttachedPolicies')]


        #get all the inline policies attached the IAM user directly
        inline_user_policies = [policy for policy in client.list_user_policies(UserName=user_name).get('PolicyNames')]

        #get all the managed policies attached to the IAM user for each group the user belongs to directly
        attached_user_policies = [policy.get('PolicyName') for policy in client.list_attached_user_policies(UserName=user['UserName']).get('AttachedPolicies')]
        
        #write IAM user access info to list
        users_info.append([
            user_name,
            user_has_console_access(client, user_name),
            user_has_mfa_enabled(client, user_name),
            user['UserId'],
            user['Arn'],
            user['CreateDate'],
            ', '.join(attached_user_policies),
            ', '.join(inline_user_policies),
            ', '.join(groups),
            ', '.join(attached_group_policies),
            ', '.join(inline_group_policies)
            ])
    

   
    # write IAM users access info to excel spreadsheet
    write_to_spreadsheet(account,users_info)


if __name__ == "__main__":
    gather_iam_data()
