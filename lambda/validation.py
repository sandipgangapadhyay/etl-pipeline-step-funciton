import json
import numpy
import pandas as pd
from cerberus import  Validator
from datetime import datetime
import boto3
import os
            
        
def lambda_handler(event, context):
    result={}
    s3_resource = boto3.resource('s3')
    to_date = lambda s: datetime.strptime(s, '%m/%d/%Y')
    bucket_name = event['bucket_name']
    key_name=event['key_name']
    source_file_name = event['file_name']
    source_file_name_to_copy = bucket_name + "/" + key_name
    error_file_name="error/" + source_file_name
    
    schema = {
        'Date': {'type': 'datetime','coerce': to_date},
        'Description': {'type': 'string'},
        'Deposits': {'type': 'float'},
        'Withdrawls': {'type': 'float'},
        'Balance': {'type': 'float'}
        }
    
    v = Validator(schema)
    v.allow_unknown = False
    v.require_all = True
    source_file_path = "s3://" + bucket_name + "/" + key_name
    try: 
        df = pd.read_csv(source_file_path)
        print("Successfuly read : " + source_file_path)
    except:
        result['Validation'] = "FAILURE"
        result['Reason'] = "Errro while reading csv"
        result['Location'] = "source"
        print("Error while reading csv")
        return(result)
        
    result['Validation'] = "SUCCESS"
    result['Location'] = "source"
    df_dict = df.to_dict(orient='records')
    transformed_file_name="s3://" + bucket_name + "/" + str(os.environ['STAGE_FOLDER']) + "/" + source_file_name

    if len(df_dict) == 0:
        result['Validation'] = "FAILURE"
        result['Reason'] = "NO RECORD FOUND"
        result['Location'] = "source"
        print("Moving file to error folder")
        return(result)
    for idx, record in enumerate(df_dict):
        if not v.validate(record):
            result['Validation'] = "FAILURE"
            result['Reason'] = str(v.errors) + " in record number " + str(idx)
            result['Location'] = "source"
            print("Moving file to error folder")
            return(result)
            break;
            #os.environ['STAGE_FOLDER']
    df['Month'] = df['Date'].astype(str).str[0:2]
    df['Day'] = df['Date'].astype(str).str[3:5]
    df['Year'] = df['Date'].astype(str).str[6:10]
    #transformed_file_name="s3://" + bucket_name + "/" + str(os.environ['STAGE_FOLDER']) + "/"  + source_file_name
    df.to_csv(transformed_file_name, index=False)
    s3_resource.Object(bucket_name, key_name).delete()
    print("Successfuly moved file to  : " + transformed_file_name)
    return(result)