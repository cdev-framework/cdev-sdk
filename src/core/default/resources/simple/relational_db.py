"""Set of constructs for making Serverless based Relational DBs

"""

from enum import Enum
from typing import Any

from core.constructs.resource import Resource, ResourceModel, ResourceOutputs, update_hash, PermissionsAvailableMixin
from core.constructs.cloud_output import  Cloud_Output_Str, OutputType
from core.utils import hasher

from core.default.resources.simple.iam import Permission, PermissionArn


RUUID = "cdev::simple::relationaldb"


#####################
###### Permission
######################
class RelationalDBPermissions:    
    def __init__(self, resource_name: str) -> None:
        

        self.DATABASE_ACCESS = Permission(
            actions=[
                "rds-data:BatchExecuteStatement",
                "rds-data:BeginTransaction",
                "rds-data:CommitTransaction",
                "rds-data:ExecuteStatement",
                "rds-data:RollbackTransaction",
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )

        self.SECRET_ACCESS = PermissionArn(
            arn="arn:aws:iam::aws:policy/SecretsManagerReadWrite"
        )


##############
##### Output
##############
class RelationalDBOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def cluster_name(self) -> Cloud_Output_Str:
        """The name of the generated db cluster"""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='cluster_name',
            type=self.OUTPUT_TYPE
        )

    @cluster_name.setter
    def cluster_name(self, value: Any):
        raise Exception

    @property
    def endpoint(self) -> Cloud_Output_Str:
        """The name of the generated db cluster"""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='endpoint',
            type=self.OUTPUT_TYPE
        )

    @endpoint.setter
    def endpoint(self, value: Any):
        raise Exception

    @property
    def secret_arn(self) -> Cloud_Output_Str:
        """The arn of the secret value create that holds the password for the db"""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='secret_arn',
            type=self.OUTPUT_TYPE
        )

    @secret_arn.setter
    def secret_arn(self, value: Any):
        raise Exception


###############
##### RelationalDB
###############
class db_engine(str, Enum):
    aurora = "aurora"
    """MySQL 5.6-compatible Aurora"""

    aurora_mysql = "aurora-mysql"
    """MySQL 5.7-compatible Aurora"""

    aurora_postgresql = "aurora-postgresql"
    """Postgres 10.4-compatible Aurora"""



class simple_relational_db_model(ResourceModel):
    Engine: db_engine
    """Some Interruption"""
    MasterUsername: str
    """Replacement"""
    MasterUserPassword: str
    """No Interruption"""
    DatabaseName: str
    """Replacement"""
    EnableHttpEndpoint: bool
    """No Interruption"""
    MaxCapacity: int
    """No Interruption"""
    MinCapacity: int
    """No Interruption"""
    SecondsToPause: int
    """No Interruption"""


class RelationalDB(PermissionsAvailableMixin, Resource):
    
    @update_hash
    def __init__(
        self,
        cdev_name: str,
        engine: db_engine,
        username: str,
        password: str,
        database_name: str = "",
        enable_http_endpoint: bool = True,
        max_capacity: int = 64,
        min_capacity: int = 2,
        seconds_to_pause: int = 300,
        nonce: str = ""
    ) -> None:
        """[summary]

        Args:
            cdev_name (str): [description]
            engine (db_engine): [description]
            username (str): [description]
            password (str): [description]
            database_name (str, optional): [description]. Defaults to "".
            enable_http_endpoint (bool, optional): [description]. Defaults to True.
            max_capacity (int, optional): [description]. Defaults to 64.
            min_capacity (int, optional): [description]. Defaults to 2.
            seconds_to_pause (int, optional): [description]. Defaults to 300.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self._engine = engine.value
        self._master_username = username
        self._master_user_password = password
        self._database_name = database_name
        self._enable_http_endpoint = enable_http_endpoint
        self._max_capacity = max_capacity
        self._min_capacity = min_capacity
        self._seconds_to_pause = seconds_to_pause

        self.output = RelationalDBOutput(cdev_name)
        self.available_permissions = RelationalDBPermissions(cdev_name)

    @property
    def seconds_to_pause(self):
        return self._seconds_to_pause

    @seconds_to_pause.setter
    @update_hash
    def seconds_to_pause(self, value: int):
        self._seconds_to_pause = value

    @property
    def min_capacity(self):
        return self._min_capacity

    @min_capacity.setter
    @update_hash
    def min_capacity(self, value: int):
        self._min_capacity = value

    @property
    def max_capacity(self):
        return self._max_capacity

    @max_capacity.setter
    @update_hash
    def max_capacity(self, value: int):
        self._max_capacity = value

    @property
    def enable_http_endpoint(self):
        return self._enable_http_endpoint

    @enable_http_endpoint.setter
    @update_hash
    def enable_http_endpoint(self, value: bool):
        self._enable_http_endpoint = value

    @property
    def database_name(self):
        return self._database_name

    @database_name.setter
    @update_hash
    def database_name(self, value: str):
        self._database_name = value

    @property
    def master_user_password(self):
        return self._master_user_password

    @master_user_password.setter
    @update_hash
    def master_user_password(self, value: str):
        self._master_user_password = value

    @property
    def master_username(self):
        return self._master_username

    @master_username.setter
    @update_hash
    def master_username(self, value: str):
        self._master_username = value

    @property
    def engine(self):
        return self._engine

    @engine.setter
    @update_hash
    def engine(self, value: db_engine):
        self._engine = value

    def compute_hash(self):
        self._hash = hasher.hash_list(
            [
                self.engine,
                self.master_username,
                self.master_user_password,
                self.database_name,
                self.enable_http_endpoint,
                self.max_capacity,
                self.min_capacity,
                self.seconds_to_pause,
                self.nonce
            ]
        )

    def render(self) -> simple_relational_db_model:
        return simple_relational_db_model(
            **{
                "ruuid": self.ruuid,
                "name": self.name,
                "hash": self.hash,
                "Engine": self.engine,
                "MasterUsername": self.master_username,
                "MasterUserPassword": self.master_user_password,
                "DatabaseName": self.database_name,
                "EnableHttpEndpoint": self.enable_http_endpoint,
                "MaxCapacity": self.max_capacity,
                "MinCapacity": self.min_capacity,
                "SecondsToPause": self.seconds_to_pause,
            }
        )

