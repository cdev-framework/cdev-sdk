from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Callable, Any


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .apigateway_models import *


class RestApi(Cdev_Resource):
    """
    Creates a new RestApi resource.


    """

    def __init__(self, cdev_name: str, name: str, description: str=None, version: str=None, cloneFrom: str=None, binaryMediaTypes: List[str]=None, minimumCompressionSize: int=None, apiKeySource: ApiKeySourceType=None, endpointConfiguration: EndpointConfiguration=None, policy: str=None, tags: Dict[str, str]=None, disableExecuteApiEndpoint: bool=None):
        ""
        super().__init__(cdev_name)

        self.name = name
        """
        A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
        """

        self.description = description
        """
        A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
        """

        self.version = version
        """
        A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
        """

        self.cloneFrom = cloneFrom
        """
        A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
        """

        self.binaryMediaTypes = binaryMediaTypes
        """
        The ID of the RestApi that you want to clone from.


        """

        self.minimumCompressionSize = minimumCompressionSize
        """
        A nullable integer that is used to enable compression (with non-negative between 0 and 10485760 (10M) bytes, inclusive) or disable compression (with a null value) on an API. When compression is enabled, compression or decompression is not applied on the payload if the payload size is smaller than this value. Setting it to zero allows compression for any payload size.


        """

        self.apiKeySource = apiKeySource
        """
        The source of the API key for metering requests according to a usage plan. Valid values are: * `HEADER` to read the API key from the `X-API-Key` header of a request.
* `AUTHORIZER` to read the API key from the `UsageIdentifierKey` from a custom authorizer.



        """

        self.endpointConfiguration = endpointConfiguration
        """
        The endpoint configuration of this RestApi showing the endpoint types of the API.


        """

        self.policy = policy
        """
        A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
        """

        self.tags = tags
        """
        The key-value map of strings. The valid character set is [a-zA-Z+-=.\_:/]. The tag key can be up to 128 characters and must not start with `aws:`. The tag value can be up to 256 characters.


        """

        self.disableExecuteApiEndpoint = disableExecuteApiEndpoint
        """
        Specifies whether clients can invoke your API by using the default `execute-api` endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.


        """

        self.hash = hasher.hash_list([self.name, self.description, self.version, self.cloneFrom, self.binaryMediaTypes, self.minimumCompressionSize, self.apiKeySource, self.endpointConfiguration, self.policy, self.tags, self.disableExecuteApiEndpoint])

    def render(self) -> restapi_model:
        data = {
            "ruuid": "cdev::aws::apigateway::restapi",
            "name": self.name,
            "hash": self.hash,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "cloneFrom": self.cloneFrom,
            "binaryMediaTypes": self.binaryMediaTypes,
            "minimumCompressionSize": self.minimumCompressionSize,
            "apiKeySource": self.apiKeySource,
            "endpointConfiguration": self.endpointConfiguration,
            "policy": self.policy,
            "tags": self.tags,
            "disableExecuteApiEndpoint": self.disableExecuteApiEndpoint,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return restapi_model(**filtered_data)

    def from_output(self, key: restapi_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::restapi::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::restapi::{self.hash}", "key": key, "type": "cdev_output"})


class Resource(Cdev_Resource):
    """
    Changes information about a Resource resource.


    """

    def __init__(self, cdev_name: str, restApiId: str, parentId: str, pathPart: str):
        ""
        super().__init__(cdev_name)

        self.restApiId = restApiId
        """
        The last path segment for this resource.


        """

        self.parentId = parentId
        """
        The last path segment for this resource.


        """

        self.pathPart = pathPart
        """
        The last path segment for this resource.


        """

        self.hash = hasher.hash_list([self.restApiId, self.parentId, self.pathPart])

    def render(self) -> resource_model:
        data = {
            "ruuid": "cdev::aws::apigateway::resource",
            "name": self.name,
            "hash": self.hash,
            "restApiId": self.restApiId,
            "parentId": self.parentId,
            "pathPart": self.pathPart,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return resource_model(**filtered_data)

    def from_output(self, key: resource_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::resource::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::resource::{self.hash}", "key": key, "type": "cdev_output"})


class Integration(Cdev_Resource):
    """
    Represents an update integration.


    """

    def __init__(self, cdev_name: str, restApiId: str, resourceId: str, httpMethod: str, type: IntegrationType, integrationHttpMethod: str=None, uri: str=None, connectionType: ConnectionType=None, connectionId: str=None, credentials: str=None, requestParameters: Dict[str, str]=None, requestTemplates: Dict[str, str]=None, passthroughBehavior: str=None, cacheNamespace: str=None, cacheKeyParameters: List[str]=None, contentHandling: ContentHandlingStrategy=None, timeoutInMillis: int=None, tlsConfig: TlsConfig=None):
        ""
        super().__init__(cdev_name)

        self.restApiId = restApiId
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.resourceId = resourceId
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.httpMethod = httpMethod
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.type = type
        """
        [Required] Specifies a put integration input's type.


        """

        self.integrationHttpMethod = integrationHttpMethod
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.uri = uri
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.connectionType = connectionType
        """
        The type of the network connection to the integration endpoint. The valid value is `INTERNET` for connections through the public routable internet or `VPC_LINK` for private connections between API Gateway and a network load balancer in a VPC. The default value is `INTERNET`.


        """

        self.connectionId = connectionId
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.credentials = credentials
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.requestParameters = requestParameters
        """
        A key-value map specifying request parameters that are passed from the method request to the back end. The key is an integration request parameter name and the associated value is a method request parameter value or static value that must be enclosed within single quotes and pre-encoded as required by the back end. The method request parameter value must match the pattern of `method.request.{location}.{name}`, where `location` is `querystring`, `path`, or `header` and `name` must be a valid and unique method request parameter name.


        """

        self.requestTemplates = requestTemplates
        """
        Represents a map of Velocity templates that are applied on the request payload based on the value of the Content-Type header sent by the client. The content type value is the key in this map, and the template (as a String) is the value.


        """

        self.passthroughBehavior = passthroughBehavior
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.cacheNamespace = cacheNamespace
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.cacheKeyParameters = cacheKeyParameters
        """
        Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


        """

        self.contentHandling = contentHandling
        """
        Specifies how to handle request payload content type conversions. Supported values are `CONVERT_TO_BINARY` and `CONVERT_TO_TEXT`, with the following behaviors:

 * `CONVERT_TO_BINARY`: Converts a request payload from a Base64-encoded string to the corresponding binary blob.


* `CONVERT_TO_TEXT`: Converts a request payload from a binary blob to a Base64-encoded string.



 If this property is not defined, the request payload will be passed through from the method request to integration request without modification, provided that the `passthroughBehavior` is configured to support payload pass-through.


        """

        self.timeoutInMillis = timeoutInMillis
        """
        Custom timeout between 50 and 29,000 milliseconds. The default value is 29,000 milliseconds or 29 seconds.


        """

        self.tlsConfig = tlsConfig

        self.hash = hasher.hash_list([self.restApiId, self.resourceId, self.httpMethod, self.type, self.integrationHttpMethod, self.uri, self.connectionType, self.connectionId, self.credentials, self.requestParameters, self.requestTemplates, self.passthroughBehavior, self.cacheNamespace, self.cacheKeyParameters, self.contentHandling, self.timeoutInMillis, self.tlsConfig])

    def render(self) -> integration_model:
        data = {
            "ruuid": "cdev::aws::apigateway::integration",
            "name": self.name,
            "hash": self.hash,
            "restApiId": self.restApiId,
            "resourceId": self.resourceId,
            "httpMethod": self.httpMethod,
            "type": self.type,
            "integrationHttpMethod": self.integrationHttpMethod,
            "uri": self.uri,
            "connectionType": self.connectionType,
            "connectionId": self.connectionId,
            "credentials": self.credentials,
            "requestParameters": self.requestParameters,
            "requestTemplates": self.requestTemplates,
            "passthroughBehavior": self.passthroughBehavior,
            "cacheNamespace": self.cacheNamespace,
            "cacheKeyParameters": self.cacheKeyParameters,
            "contentHandling": self.contentHandling,
            "timeoutInMillis": self.timeoutInMillis,
            "tlsConfig": self.tlsConfig,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return integration_model(**filtered_data)

    def from_output(self, key: integration_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::integration::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::integration::{self.hash}", "key": key, "type": "cdev_output"})


class Stage(Cdev_Resource):
    """
    Changes information about a Stage resource.


    """

    def __init__(self, cdev_name: str, restApiId: str, stageName: str, deploymentId: str, description: str=None, cacheClusterEnabled: bool=None, cacheClusterSize: CacheClusterSize=None, variables: Dict[str, str]=None, documentationVersion: str=None, canarySettings: CanarySettings=None, tracingEnabled: bool=None, tags: Dict[str, str]=None):
        ""
        super().__init__(cdev_name)

        self.restApiId = restApiId
        """
        The version of the associated API documentation.


        """

        self.stageName = stageName
        """
        The version of the associated API documentation.


        """

        self.deploymentId = deploymentId
        """
        The version of the associated API documentation.


        """

        self.description = description
        """
        The version of the associated API documentation.


        """

        self.cacheClusterEnabled = cacheClusterEnabled
        """
        Specifies whether active tracing with X-ray is enabled for the Stage.


        """

        self.cacheClusterSize = cacheClusterSize
        """
        The stage's cache cluster size.


        """

        self.variables = variables
        """
        A map that defines the stage variables for the new Stage resource. Variable names can have alphanumeric and underscore characters, and the values must match `[A-Za-z0-9-._~:/?#&=,]+`.


        """

        self.documentationVersion = documentationVersion
        """
        The version of the associated API documentation.


        """

        self.canarySettings = canarySettings
        """
        The canary deployment settings of this stage.


        """

        self.tracingEnabled = tracingEnabled
        """
        Specifies whether active tracing with X-ray is enabled for the Stage.


        """

        self.tags = tags
        """
        The key-value map of strings. The valid character set is [a-zA-Z+-=.\_:/]. The tag key can be up to 128 characters and must not start with `aws:`. The tag value can be up to 256 characters.


        """

        self.hash = hasher.hash_list([self.restApiId, self.stageName, self.deploymentId, self.description, self.cacheClusterEnabled, self.cacheClusterSize, self.variables, self.documentationVersion, self.canarySettings, self.tracingEnabled, self.tags])

    def render(self) -> stage_model:
        data = {
            "ruuid": "cdev::aws::apigateway::stage",
            "name": self.name,
            "hash": self.hash,
            "restApiId": self.restApiId,
            "stageName": self.stageName,
            "deploymentId": self.deploymentId,
            "description": self.description,
            "cacheClusterEnabled": self.cacheClusterEnabled,
            "cacheClusterSize": self.cacheClusterSize,
            "variables": self.variables,
            "documentationVersion": self.documentationVersion,
            "canarySettings": self.canarySettings,
            "tracingEnabled": self.tracingEnabled,
            "tags": self.tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return stage_model(**filtered_data)

    def from_output(self, key: stage_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::stage::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::stage::{self.hash}", "key": key, "type": "cdev_output"})


class Deployment(Cdev_Resource):
    """
    Changes information about a Deployment resource.


    """

    def __init__(self, cdev_name: str, restApiId: str, stageName: str=None, stageDescription: str=None, description: str=None, cacheClusterEnabled: bool=None, cacheClusterSize: CacheClusterSize=None, variables: Dict[str, str]=None, canarySettings: DeploymentCanarySettings=None, tracingEnabled: bool=None):
        ""
        super().__init__(cdev_name)

        self.restApiId = restApiId
        """
        The description for the Deployment resource to create.


        """

        self.stageName = stageName
        """
        The description for the Deployment resource to create.


        """

        self.stageDescription = stageDescription
        """
        The description for the Deployment resource to create.


        """

        self.description = description
        """
        The description for the Deployment resource to create.


        """

        self.cacheClusterEnabled = cacheClusterEnabled
        """
        Specifies whether active tracing with X-ray is enabled for the Stage.


        """

        self.cacheClusterSize = cacheClusterSize
        """
        Specifies the cache cluster size for the Stage resource specified in the input, if a cache cluster is enabled.


        """

        self.variables = variables
        """
        A map that defines the stage variables for the Stage resource that is associated with the new deployment. Variable names can have alphanumeric and underscore characters, and the values must match `[A-Za-z0-9-._~:/?#&=,]+`.


        """

        self.canarySettings = canarySettings
        """
        The input configuration for the canary deployment when the deployment is a canary release deployment. 


        """

        self.tracingEnabled = tracingEnabled
        """
        Specifies whether active tracing with X-ray is enabled for the Stage.


        """

        self.hash = hasher.hash_list([self.restApiId, self.stageName, self.stageDescription, self.description, self.cacheClusterEnabled, self.cacheClusterSize, self.variables, self.canarySettings, self.tracingEnabled])

    def render(self) -> deployment_model:
        data = {
            "ruuid": "cdev::aws::apigateway::deployment",
            "name": self.name,
            "hash": self.hash,
            "restApiId": self.restApiId,
            "stageName": self.stageName,
            "stageDescription": self.stageDescription,
            "description": self.description,
            "cacheClusterEnabled": self.cacheClusterEnabled,
            "cacheClusterSize": self.cacheClusterSize,
            "variables": self.variables,
            "canarySettings": self.canarySettings,
            "tracingEnabled": self.tracingEnabled,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return deployment_model(**filtered_data)

    def from_output(self, key: deployment_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::deployment::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigateway::deployment::{self.hash}", "key": key, "type": "cdev_output"})


