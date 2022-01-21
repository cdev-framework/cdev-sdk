from enum import Enum

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher

from .iam import Permission, PermissionArn


class db_engine(str, Enum):
    aurora = "aurora"
    """MySQL 5.6-compatible Aurora"""

    aurora_mysql = "aurora-mysql"
    """MySQL 5.7-compatible Aurora"""

    aurora_postgresql = "aurora-postgresql"
    """Postgres 10.4-compatible Aurora"""


class simple_relational_db_model(ResourceModel):
    DatabaseName: str
    """Replacement"""
    EnableHttpEndpoint: bool
    """No Interruption"""
    Engine: db_engine
    """Some Interruption"""
    MasterUsername: str
    """Replacement"""
    MasterUserPassword: str
    """No Interruption"""
    MaxCapacity: int
    """No Interruption"""
    MinCapacity: int
    """No Interruption"""
    SecondsToPause: int
    """No Interruption"""


class simple_relational_db_output(str, Enum):
    endpoint = "cloud_id"
    secret_arn = "secret_arn"


class RelationalDBPermissions:
    RUUID = "cdev::simple::relationaldb"
    
    
    def __init__(self, resource_name) -> None:
        

        self.DATABASE_ACCESS = Permission(
            actions=[
                "rds-data:BatchExecuteStatement",
                "rds-data:BeginTransaction",
                "rds-data:CommitTransaction",
                "rds-data:ExecuteStatement",
                "rds-data:RollbackTransaction",
            ],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.SECRET_ACCESS = PermissionArn(
            arn="arn:aws:iam::aws:policy/SecretsManagerReadWrite"
        )


class RelationalDB(Resource):
    RUUID = "cdev::simple::relationaldb"

    def __init__(
        self,
        cdev_name: str,
        engine: db_engine,
        username: str,
        password: str,
        httpendpoint: bool = True,
        database_name: str = "",
        max_capacity: int = 64,
        min_capacity: int = 2,
        seconds_to_pause: int = 300,
        _nonce: str = ""
    ) -> None:

        super().__init__(cdev_name)

        self.Engine = engine.value
        self.MasterUsername = username
        self.MasterUserPassword = password

        self._nonce = _nonce

        self.DatabaseName = database_name
        self.EnableHttpEndpoint = httpendpoint

        self.MaxCapacity = max_capacity
        self.MinCapacity = min_capacity
        self.SecondsToPause = seconds_to_pause

        self.permissions = RelationalDBPermissions(cdev_name)

        self.hash = hasher.hash_list(
            [
                self.Engine,
                self.MasterUsername,
                self.MasterUserPassword,
                self.DatabaseName,
                self.EnableHttpEndpoint,
                self.MaxCapacity,
                self.MinCapacity,
                self.SecondsToPause,
                self._nonce
            ]
        )

    def render(self) -> simple_relational_db_model:
        return simple_relational_db_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "DatabaseName": self.DatabaseName,
                "EnableHttpEndpoint": self.EnableHttpEndpoint,
                "Engine": self.Engine,
                "MasterUsername": self.MasterUsername,
                "MasterUserPassword": self.MasterUserPassword,
                "MaxCapacity": self.MaxCapacity,
                "MinCapacity": self.MinCapacity,
                "SecondsToPause": self.SecondsToPause,
            }
        )

    def from_output(self, key: simple_relational_db_output) -> Cloud_Output:
        return super().from_output(key)
