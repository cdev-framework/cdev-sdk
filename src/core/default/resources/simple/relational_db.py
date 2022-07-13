"""Set of constructs for making Serverless based Relational DBs

"""

from enum import Enum
from typing import Any, Dict

from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    ResourceOutputs,
    update_hash,
    PermissionsAvailableMixin,
    TaggableMixin,
)
from core.constructs.cloud_output import Cloud_Output_Str, OutputType
from core.utils import hasher
from core.constructs.models import frozendict

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
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Access to the DB"""

        self.SECRET_ACCESS = PermissionArn(
            arn="arn:aws:iam::aws:policy/SecretsManagerReadWrite"
        )
        """Access to the generated Secret that contains the connection information"""


##############
##### Output
##############
class RelationalDBOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after a Relational DB has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def cluster_arn(self) -> Cloud_Output_Str:
        """The name of the generated db cluster"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="cluster_arn", type=self.OUTPUT_TYPE
        )

    @cluster_arn.setter
    def cluster_arn(self, value: Any) -> None:
        raise Exception

    @property
    def endpoint(self) -> Cloud_Output_Str:
        """The name of the generated db cluster"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="endpoint", type=self.OUTPUT_TYPE
        )

    @endpoint.setter
    def endpoint(self, value: Any):
        raise Exception

    @property
    def secret_arn(self) -> Cloud_Output_Str:
        """The arn of the secret value create that holds the password for the db"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="secret_arn", type=self.OUTPUT_TYPE
        )

    @secret_arn.setter
    def secret_arn(self, value: Any) -> None:
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


class simple_relational_db_model(TaggableResourceModel):
    """Model that represents a relation db"""

    Engine: db_engine
    """DB engine"""
    MasterUsername: str
    """Username used to connect to the DB"""
    MasterUserPassword: str
    """Username used to connect to the DB"""
    DatabaseName: str
    """Name for the main db"""
    EnableHttpEndpoint: bool
    """Allow connection via a generated HTTP endpoint"""
    MaxCapacity: int
    """Maximum amount of capacity to scale to"""
    MinCapacity: int
    """Amount of seconds to wait before scaling DB completely down."""
    SecondsToPause: int
    """Amount of seconds to wait before scaling DB completely down"""


class RelationalDB(PermissionsAvailableMixin, TaggableMixin, Resource):
    """Construct for creating a Serverless Relational DB"""

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
        nonce: str = "",
        tags: Dict[str, str] = None,
    ) -> None:
        """
        Args:
            cdev_name (str): Name of the resource
            engine (db_engine): DB engine
            username (str): Username used to connect to the DB
            password (str): Password used to connect to the DB
            database_name (str, optional): Name for the main db. Defaults to "".
            enable_http_endpoint (bool, optional): Allow connection via a generated HTTP endpoint. Defaults to True.
            max_capacity (int, optional): Maximum amount of capacity to scale to. Defaults to 64.
            min_capacity (int, optional): Minimum amount of capacity to scale to. Defaults to 2.
            seconds_to_pause (int, optional): Amount of seconds to wait before scaling DB completely down. Defaults to 300.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource
        """
        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        self._engine = engine.value
        self._master_username = username
        self._master_user_password = password
        self._database_name = database_name
        self._enable_http_endpoint = enable_http_endpoint
        self._max_capacity = max_capacity
        self._min_capacity = min_capacity
        self._seconds_to_pause = seconds_to_pause

        self.output: RelationalDBOutput = RelationalDBOutput(cdev_name)
        self.available_permissions: RelationalDBPermissions = RelationalDBPermissions(
            cdev_name
        )

    @property
    def seconds_to_pause(self) -> int:
        """Amount of seconds to wait before scaling DB completely down"""
        return self._seconds_to_pause

    @seconds_to_pause.setter
    @update_hash
    def seconds_to_pause(self, value: int) -> None:
        self._seconds_to_pause = value

    @property
    def min_capacity(self) -> int:
        """Amount of seconds to wait before scaling DB completely down."""
        return self._min_capacity

    @min_capacity.setter
    @update_hash
    def min_capacity(self, value: int) -> None:
        self._min_capacity = value

    @property
    def max_capacity(self) -> int:
        """Maximum amount of capacity to scale to"""
        return self._max_capacity

    @max_capacity.setter
    @update_hash
    def max_capacity(self, value: int) -> None:
        self._max_capacity = value

    @property
    def enable_http_endpoint(self):
        """Allow connection via a generated HTTP endpoint"""
        return self._enable_http_endpoint

    @enable_http_endpoint.setter
    @update_hash
    def enable_http_endpoint(self, value: bool) -> None:
        self._enable_http_endpoint = value

    @property
    def database_name(self) -> str:
        """Name for the main db"""
        return self._database_name

    @database_name.setter
    @update_hash
    def database_name(self, value: str) -> None:
        self._database_name = value

    @property
    def master_user_password(self) -> str:
        """Password used to connect to the DB"""
        return self._master_user_password

    @master_user_password.setter
    @update_hash
    def master_user_password(self, value: str) -> None:
        self._master_user_password = value

    @property
    def master_username(self) -> str:
        """Username used to connect to the DB"""
        return self._master_username

    @master_username.setter
    @update_hash
    def master_username(self, value: str) -> None:
        self._master_username = value

    @property
    def engine(self):
        """DB engine"""
        return self._engine

    @engine.setter
    @update_hash
    def engine(self, value: db_engine) -> None:
        self._engine = value

    def compute_hash(self) -> None:
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
                self.nonce,
                self._get_tags_hash(),
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
                "tags": frozendict(self.tags)
            }
        )
