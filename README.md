# Audit AWS
Audits IAM accounts. An excel file will be produced with IAM users and policies attached to them in that particular account.

## Instructions
1. `pip install -r requirements.txt`
2.  Run audit report for particular account for example, `python iam_audit.py`
3.  The script will ask for AWS access and secret key as a password prompt.


## For more info
```
$ python iam_audit.py --help                                                   *[v2]
Usage: iam_audit.py [OPTIONS]

  Gather IAM data for AWS account associated with credentials provided.

Options:
  -ac, --access_key TEXT  AWS access key.  [required]
  -sc, --secret_key TEXT  AWS secret key.  [required]
  --help                  Show this message and exit.
  ```
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#client

https://click.palletsprojects.com/en/8.1.x/options/#password-prompts
  
Author: Walter Carbajal
written in python3