from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict 

from ...models import Rendered_Resource

class BucketCannedACL(str, Enum): 

    private = 'private'

    public_read = 'public-read'

    public_read_write = 'public-read-write'

    authenticated_read = 'authenticated-read'



class BucketLocationConstraint(str, Enum): 

    af_south_1 = 'af-south-1'

    ap_east_1 = 'ap-east-1'

    ap_northeast_1 = 'ap-northeast-1'

    ap_northeast_2 = 'ap-northeast-2'

    ap_northeast_3 = 'ap-northeast-3'

    ap_south_1 = 'ap-south-1'

    ap_southeast_1 = 'ap-southeast-1'

    ap_southeast_2 = 'ap-southeast-2'

    ca_central_1 = 'ca-central-1'

    cn_north_1 = 'cn-north-1'

    cn_northwest_1 = 'cn-northwest-1'

    EU = 'EU'

    eu_central_1 = 'eu-central-1'

    eu_north_1 = 'eu-north-1'

    eu_south_1 = 'eu-south-1'

    eu_west_1 = 'eu-west-1'

    eu_west_2 = 'eu-west-2'

    eu_west_3 = 'eu-west-3'

    me_south_1 = 'me-south-1'

    sa_east_1 = 'sa-east-1'

    us_east_2 = 'us-east-2'

    us_gov_east_1 = 'us-gov-east-1'

    us_gov_west_1 = 'us-gov-west-1'

    us_west_1 = 'us-west-1'

    us_west_2 = 'us-west-2'


class CreateBucketConfiguration(BaseModel):

    LocationConstraint: BucketLocationConstraint 









class EncodingType(str, Enum): 

    url = 'url'




class RequestPayer(str, Enum): 

    requester = 'requester'



class bucket_output(str, Enum):
    Location = "Location"


class bucket_model(Rendered_Resource):
    ACL: Optional[BucketCannedACL] 

    Bucket: str

    CreateBucketConfiguration: Optional[CreateBucketConfiguration] 

    GrantFullControl: Optional[str]

    GrantRead: Optional[str]

    GrantReadACP: Optional[str]

    GrantWrite: Optional[str]

    GrantWriteACP: Optional[str]

    ObjectLockEnabledForBucket: Optional[bool]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, Bucket: str, ACL: BucketCannedACL=None, CreateBucketConfiguration: CreateBucketConfiguration=None, GrantFullControl: str=None, GrantRead: str=None, GrantReadACP: str=None, GrantWrite: str=None, GrantWriteACP: str=None, ObjectLockEnabledForBucket: bool=None ) -> None:
        data = {
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "ACL": ACL,
            "Bucket": Bucket,
            "CreateBucketConfiguration": CreateBucketConfiguration,
            "GrantFullControl": GrantFullControl,
            "GrantRead": GrantRead,
            "GrantReadACP": GrantReadACP,
            "GrantWrite": GrantWrite,
            "GrantWriteACP": GrantWriteACP,
            "ObjectLockEnabledForBucket": ObjectLockEnabledForBucket,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        super().__init__(**filtered_data)

    class Config:
        extra='ignore'

