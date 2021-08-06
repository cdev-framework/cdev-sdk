from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Union, Dict

from ...models import Cloud_Output, Rendered_Resource

from ...backend import cloud_mapper_manager




class Cors(BaseModel):
    """
    Represents a CORS configuration. Supported only for HTTP APIs. See [Configuring CORS](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html) for more information.


    """


    AllowCredentials: Union[bool, Cloud_Output]
    """
    Specifies whether credentials are included in the CORS request. Supported only for HTTP APIs.


    """

    AllowHeaders: Union[List[str], Cloud_Output]
    """
    The API identifier.


    """

    AllowMethods: Union[List[str], Cloud_Output]
    """
    Specifies the format of the payload sent to an integration. Required for HTTP APIs.


    """

    AllowOrigins: Union[List[str], Cloud_Output]
    """
    The API identifier.


    """

    ExposeHeaders: Union[List[str], Cloud_Output]
    """
    The API identifier.


    """

    MaxAge: Union[int, Cloud_Output]
    """
    The number of seconds that the browser should cache preflight request results. Supported only for HTTP APIs.


    """


    def __init__(self, AllowCredentials: bool, AllowHeaders: List[str], AllowMethods: List[str], AllowOrigins: List[str], ExposeHeaders: List[str], MaxAge: int ):
        "My doc string"
        super().__init__(**{
            "AllowCredentials": AllowCredentials,
            "AllowHeaders": AllowHeaders,
            "AllowMethods": AllowMethods,
            "AllowOrigins": AllowOrigins,
            "ExposeHeaders": ExposeHeaders,
            "MaxAge": MaxAge,
        })        






class ProtocolType(str, Enum): 
    """
    Represents a protocol type.
    """


    WEBSOCKET = 'WEBSOCKET'
    
    HTTP = 'HTTP'
    




class AuthorizationType(str, Enum): 
    """
    The authorization type. For WebSocket APIs, valid values are NONE for open access, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer. For HTTP APIs, valid values are NONE for open access, JWT for using JSON Web Tokens, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer.


    """


    NONE = 'NONE'
    
    AWS_IAM = 'AWS_IAM'
    
    CUSTOM = 'CUSTOM'
    
    JWT = 'JWT'
    


class ParameterConstraints(BaseModel):
    """
    Validation constraints imposed on parameters of a request (path, query string, headers).


    """


    Required: Union[bool, Cloud_Output]
    """
    Whether or not the parameter is required.


    """


    def __init__(self, Required: bool ):
        "My doc string"
        super().__init__(**{
            "Required": Required,
        })        




class ConnectionType(str, Enum): 
    """
    Represents a connection type.


    """


    INTERNET = 'INTERNET'
    
    VPC_LINK = 'VPC_LINK'
    

class ContentHandlingStrategy(str, Enum): 
    """
    Specifies how to handle response payload content type conversions. Supported only for WebSocket APIs.


    """


    CONVERT_TO_BINARY = 'CONVERT_TO_BINARY'
    
    CONVERT_TO_TEXT = 'CONVERT_TO_TEXT'
    

class IntegrationType(str, Enum): 
    """
    Represents an API method integration type.


    """


    AWS = 'AWS'
    
    HTTP = 'HTTP'
    
    MOCK = 'MOCK'
    
    HTTP_PROXY = 'HTTP_PROXY'
    
    AWS_PROXY = 'AWS_PROXY'
    

class PassthroughBehavior(str, Enum): 
    """
    Represents passthrough behavior for an integration response. Supported only for WebSocket APIs.


    """


    WHEN_NO_MATCH = 'WHEN_NO_MATCH'
    
    NEVER = 'NEVER'
    
    WHEN_NO_TEMPLATES = 'WHEN_NO_TEMPLATES'
    



class TlsConfigInput(BaseModel):
    """
    The TLS configuration for a private integration. If you specify a TLS configuration, private integration traffic uses the HTTPS protocol. Supported only for HTTP APIs.


    """


    ServerNameToVerify: Union[str, Cloud_Output]
    """
    If you specify a server name, API Gateway uses it to verify the hostname on the integration's certificate. The server name is also included in the TLS handshake to support Server Name Indication (SNI) or virtual hosting.


    """


    def __init__(self, ServerNameToVerify: str ):
        "My doc string"
        super().__init__(**{
            "ServerNameToVerify": ServerNameToVerify,
        })        



class AccessLogSettings(BaseModel):
    """
    Settings for logging access in a stage.


    """


    DestinationArn: Union[str, Cloud_Output]
    """
    The ARN of the CloudWatch Logs log group to receive access logs.


    """

    Format: Union[str, Cloud_Output]
    """
    A single line format of the access logs of data, as specified by selected $context variables. The format must include at least $context.requestId.


    """


    def __init__(self, DestinationArn: str, Format: str ):
        "My doc string"
        super().__init__(**{
            "DestinationArn": DestinationArn,
            "Format": Format,
        })        



class LoggingLevel(str, Enum): 
    """
    The logging level.


    """


    ERROR = 'ERROR'
    
    INFO = 'INFO'
    
    OFF = 'OFF'
    

class RouteSettings(BaseModel):
    """
    Represents a collection of route settings.


    """


    DataTraceEnabled: Union[bool, Cloud_Output]
    """
    Specifies whether detailed metrics are enabled.


    """

    DetailedMetricsEnabled: Union[bool, Cloud_Output]
    """
    Specifies whether detailed metrics are enabled.


    """

    LoggingLevel: Union[LoggingLevel, Cloud_Output]
    """
    Specifies the logging level for this route: INFO, ERROR, or OFF. This property affects the log entries pushed to Amazon CloudWatch Logs. Supported only for WebSocket APIs.


    """

    ThrottlingBurstLimit: Union[int, Cloud_Output]
    """
    Specifies the throttling burst limit.


    """

    ThrottlingRateLimit: Union[int, Cloud_Output]
    """
    Specifies the throttling rate limit.


    """


    def __init__(self, DataTraceEnabled: bool, DetailedMetricsEnabled: bool, LoggingLevel: LoggingLevel, ThrottlingBurstLimit: int, ThrottlingRateLimit: int ):
        "My doc string"
        super().__init__(**{
            "DataTraceEnabled": DataTraceEnabled,
            "DetailedMetricsEnabled": DetailedMetricsEnabled,
            "LoggingLevel": LoggingLevel,
            "ThrottlingBurstLimit": ThrottlingBurstLimit,
            "ThrottlingRateLimit": ThrottlingRateLimit,
        })        





class api_output(str, Enum):
    """
    Creates an Api resource.


    """

    ApiEndpoint = "ApiEndpoint"
    """
    The URI of the API, of the form {api-id}.execute-api.{region}.amazonaws.com. The stage name is typically appended to this URI to form a complete path to a deployed API stage.


    """

    ApiGatewayManaged = "ApiGatewayManaged"
    """
    Specifies whether an API is managed by API Gateway. You can't update or delete a managed API by using API Gateway. A managed API can be deleted only through the tooling or service that created it.


    """

    ApiId = "ApiId"
    """
    The API ID.


    """

    ApiKeySelectionExpression = "ApiKeySelectionExpression"
    """
    An API key selection expression. Supported only for WebSocket APIs. See [API Key Selection Expressions](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-selection-expressions.html#apigateway-websocket-api-apikey-selection-expressions).


    """

    CorsConfiguration = "CorsConfiguration"
    """
    A CORS configuration. Supported only for HTTP APIs.


    """

    CreatedDate = "CreatedDate"
    """
    The timestamp when the API was created.


    """

    Description = "Description"
    """
    The description of the API.


    """

    DisableSchemaValidation = "DisableSchemaValidation"
    """
    Avoid validating models when creating a deployment. Supported only for WebSocket APIs.


    """

    DisableExecuteApiEndpoint = "DisableExecuteApiEndpoint"
    """
    Specifies whether clients can invoke your API by using the default execute-api endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.


    """

    ImportInfo = "ImportInfo"
    """
    The validation information during API import. This may include particular properties of your OpenAPI definition which are ignored during import. Supported only for HTTP APIs.


    """

    Name = "Name"
    """
    The name of the API.


    """

    ProtocolType = "ProtocolType"
    """
    The API protocol.


    """

    RouteSelectionExpression = "RouteSelectionExpression"
    """
    The route selection expression for the API. For HTTP APIs, the routeSelectionExpression must be ${request.method} ${request.path}. If not provided, this will be the default for HTTP APIs. This property is required for WebSocket APIs.


    """

    Tags = "Tags"
    """
    A collection of tags associated with the API.


    """

    Version = "Version"
    """
    A version identifier for the API.


    """

    Warnings = "Warnings"
    """
    The warning messages reported when failonwarnings is turned on during API import.


    """



class route_output(str, Enum):
    """
    Creates a Route for an API.


    """

    ApiGatewayManaged = "ApiGatewayManaged"
    """
    Specifies whether a route is managed by API Gateway. If you created an API using quick create, the $default route is managed by API Gateway. You can't modify the $default route key.


    """

    ApiKeyRequired = "ApiKeyRequired"
    """
    Specifies whether an API key is required for this route. Supported only for WebSocket APIs.


    """

    AuthorizationScopes = "AuthorizationScopes"
    """
    A list of authorization scopes configured on a route. The scopes are used with a JWT authorizer to authorize the method invocation. The authorization works by matching the route scopes against the scopes parsed from the access token in the incoming request. The method invocation is authorized if any route scope matches a claimed scope in the access token. Otherwise, the invocation is not authorized. When the route scope is configured, the client must provide an access token instead of an identity token for authorization purposes.


    """

    AuthorizationType = "AuthorizationType"
    """
    The authorization type for the route. For WebSocket APIs, valid values are NONE for open access, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer For HTTP APIs, valid values are NONE for open access, JWT for using JSON Web Tokens, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer.


    """

    AuthorizerId = "AuthorizerId"
    """
    The identifier of the Authorizer resource to be associated with this route. The authorizer identifier is generated by API Gateway when you created the authorizer.


    """

    ModelSelectionExpression = "ModelSelectionExpression"
    """
    The model selection expression for the route. Supported only for WebSocket APIs.


    """

    OperationName = "OperationName"
    """
    The operation name for the route.


    """

    RequestModels = "RequestModels"
    """
    The request models for the route. Supported only for WebSocket APIs.


    """

    RequestParameters = "RequestParameters"
    """
    The request parameters for the route. Supported only for WebSocket APIs.


    """

    RouteId = "RouteId"
    """
    The route ID.


    """

    RouteKey = "RouteKey"
    """
    The route key for the route.


    """

    RouteResponseSelectionExpression = "RouteResponseSelectionExpression"
    """
    The route response selection expression for the route. Supported only for WebSocket APIs.


    """

    Target = "Target"
    """
    The target for the route.


    """



class integration_output(str, Enum):
    """
    Creates an Integration.


    """

    ApiGatewayManaged = "ApiGatewayManaged"
    """
    Specifies whether an integration is managed by API Gateway. If you created an API using using quick create, the resulting integration is managed by API Gateway. You can update a managed integration, but you can't delete it.


    """

    ConnectionId = "ConnectionId"
    """
    The ID of the VPC link for a private integration. Supported only for HTTP APIs.


    """

    ConnectionType = "ConnectionType"
    """
    The type of the network connection to the integration endpoint. Specify INTERNET for connections through the public routable internet or VPC\_LINK for private connections between API Gateway and resources in a VPC. The default value is INTERNET.


    """

    ContentHandlingStrategy = "ContentHandlingStrategy"
    """
    Supported only for WebSocket APIs. Specifies how to handle response payload content type conversions. Supported values are CONVERT\_TO\_BINARY and CONVERT\_TO\_TEXT, with the following behaviors:

 CONVERT\_TO\_BINARY: Converts a response payload from a Base64-encoded string to the corresponding binary blob.

 CONVERT\_TO\_TEXT: Converts a response payload from a binary blob to a Base64-encoded string.

 If this property is not defined, the response payload will be passed through from the integration response to the route response or method response without modification.


    """

    CredentialsArn = "CredentialsArn"
    """
    Specifies the credentials required for the integration, if any. For AWS integrations, three options are available. To specify an IAM Role for API Gateway to assume, use the role's Amazon Resource Name (ARN). To require that the caller's identity be passed through from the request, specify the string arn:aws:iam::*:user/*. To use resource-based permissions on supported AWS services, specify null.


    """

    Description = "Description"
    """
    Represents the description of an integration.


    """

    IntegrationId = "IntegrationId"
    """
    Represents the identifier of an integration.


    """

    IntegrationMethod = "IntegrationMethod"
    """
    Specifies the integration's HTTP method type.


    """

    IntegrationResponseSelectionExpression = "IntegrationResponseSelectionExpression"
    """
    The integration response selection expression for the integration. Supported only for WebSocket APIs. See [Integration Response Selection Expressions](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-selection-expressions.html#apigateway-websocket-api-integration-response-selection-expressions).


    """

    IntegrationSubtype = "IntegrationSubtype"
    """
    Supported only for HTTP API AWS\_PROXY integrations. Specifies the AWS service action to invoke. To learn more, see [Integration subtype reference](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-aws-services-reference.html).


    """

    IntegrationType = "IntegrationType"
    """
    The integration type of an integration. One of the following:

 AWS: for integrating the route or method request with an AWS service action, including the Lambda function-invoking action. With the Lambda function-invoking action, this is referred to as the Lambda custom integration. With any other AWS service action, this is known as AWS integration. Supported only for WebSocket APIs.

 AWS\_PROXY: for integrating the route or method request with a Lambda function or other AWS service action. This integration is also referred to as a Lambda proxy integration.

 HTTP: for integrating the route or method request with an HTTP endpoint. This integration is also referred to as the HTTP custom integration. Supported only for WebSocket APIs.

 HTTP\_PROXY: for integrating the route or method request with an HTTP endpoint, with the client request passed through as-is. This is also referred to as HTTP proxy integration.

 MOCK: for integrating the route or method request with API Gateway as a "loopback" endpoint without invoking any backend. Supported only for WebSocket APIs.


    """

    IntegrationUri = "IntegrationUri"
    """
    For a Lambda integration, specify the URI of a Lambda function.

 For an HTTP integration, specify a fully-qualified URL.

 For an HTTP API private integration, specify the ARN of an Application Load Balancer listener, Network Load Balancer listener, or AWS Cloud Map service. If you specify the ARN of an AWS Cloud Map service, API Gateway uses DiscoverInstances to identify resources. You can use query parameters to target specific resources. To learn more, see [DiscoverInstances](https://docs.aws.amazon.com/cloud-map/latest/api/API_DiscoverInstances.html). For private integrations, all resources must be owned by the same AWS account.


    """

    PassthroughBehavior = "PassthroughBehavior"
    """
    Specifies the pass-through behavior for incoming requests based on the Content-Type header in the request, and the available mapping templates specified as the requestTemplates property on the Integration resource. There are three valid values: WHEN\_NO\_MATCH, WHEN\_NO\_TEMPLATES, and NEVER. Supported only for WebSocket APIs.

 WHEN\_NO\_MATCH passes the request body for unmapped content types through to the integration backend without transformation.

 NEVER rejects unmapped content types with an HTTP 415 Unsupported Media Type response.

 WHEN\_NO\_TEMPLATES allows pass-through when the integration has no content types mapped to templates. However, if there is at least one content type defined, unmapped content types will be rejected with the same HTTP 415 Unsupported Media Type response.


    """

    PayloadFormatVersion = "PayloadFormatVersion"
    """
    Specifies the format of the payload sent to an integration. Required for HTTP APIs.


    """

    RequestParameters = "RequestParameters"
    """
    For WebSocket APIs, a key-value map specifying request parameters that are passed from the method request to the backend. The key is an integration request parameter name and the associated value is a method request parameter value or static value that must be enclosed within single quotes and pre-encoded as required by the backend. The method request parameter value must match the pattern of method.request.{location}.{name}
 , where 
 {location}
 is querystring, path, or header; and 
 {name}
 must be a valid and unique method request parameter name.

 For HTTP API integrations with a specified integrationSubtype, request parameters are a key-value map specifying parameters that are passed to AWS\_PROXY integrations. You can provide static values, or map request data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Working with AWS service integrations for HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-aws-services.html).

 For HTTP API itegrations, without a specified integrationSubtype request parameters are a key-value map specifying how to transform HTTP requests before sending them to backend integrations. The key should follow the pattern <action>:<header|querystring|path>.<location>. The action can be append, overwrite or remove. For values, you can provide static values, or map request data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Transforming API requests and responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).


    """

    RequestTemplates = "RequestTemplates"
    """
    Represents a map of Velocity templates that are applied on the request payload based on the value of the Content-Type header sent by the client. The content type value is the key in this map, and the template (as a String) is the value. Supported only for WebSocket APIs.


    """

    ResponseParameters = "ResponseParameters"
    """
    Supported only for HTTP APIs. You use response parameters to transform the HTTP response from a backend integration before returning the response to clients. Specify a key-value map from a selection key to response parameters. The selection key must be a valid HTTP status code within the range of 200-599. Response parameters are a key-value map. The key must match pattern <action>:<header>.<location> or overwrite.statuscode. The action can be append, overwrite or remove. The value can be a static value, or map to response data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Transforming API requests and responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).


    """

    TemplateSelectionExpression = "TemplateSelectionExpression"
    """
    The template selection expression for the integration. Supported only for WebSocket APIs.


    """

    TimeoutInMillis = "TimeoutInMillis"
    """
    Custom timeout between 50 and 29,000 milliseconds for WebSocket APIs and between 50 and 30,000 milliseconds for HTTP APIs. The default timeout is 29 seconds for WebSocket APIs and 30 seconds for HTTP APIs.


    """

    TlsConfig = "TlsConfig"
    """
    The TLS configuration for a private integration. If you specify a TLS configuration, private integration traffic uses the HTTPS protocol. Supported only for HTTP APIs.


    """



class stage_output(str, Enum):
    """
    Creates a Stage for an API.


    """

    AccessLogSettings = "AccessLogSettings"
    """
    Settings for logging access in this stage.


    """

    ApiGatewayManaged = "ApiGatewayManaged"
    """
    Specifies whether a stage is managed by API Gateway. If you created an API using quick create, the $default stage is managed by API Gateway. You can't modify the $default stage.


    """

    AutoDeploy = "AutoDeploy"
    """
    Specifies whether updates to an API automatically trigger a new deployment. The default value is false.


    """

    ClientCertificateId = "ClientCertificateId"
    """
    The identifier of a client certificate for a Stage. Supported only for WebSocket APIs.


    """

    CreatedDate = "CreatedDate"
    """
    The timestamp when the stage was created.


    """

    DefaultRouteSettings = "DefaultRouteSettings"
    """
    Default route settings for the stage.


    """

    DeploymentId = "DeploymentId"
    """
    The identifier of the Deployment that the Stage is associated with. Can't be updated if autoDeploy is enabled.


    """

    Description = "Description"
    """
    The description of the stage.


    """

    LastDeploymentStatusMessage = "LastDeploymentStatusMessage"
    """
    Describes the status of the last deployment of a stage. Supported only for stages with autoDeploy enabled.


    """

    LastUpdatedDate = "LastUpdatedDate"
    """
    The timestamp when the stage was last updated.


    """

    RouteSettings = "RouteSettings"
    """
    Route settings for the stage, by routeKey.


    """

    StageName = "StageName"
    """
    The name of the stage.


    """

    StageVariables = "StageVariables"
    """
    A map that defines the stage variables for a stage resource. Variable names can have alphanumeric and underscore characters, and the values must match [A-Za-z0-9-.\_~:/?#&=,]+.


    """

    Tags = "Tags"
    """
    The collection of tags. Each tag element is associated with a given resource.


    """



class deployment_output(str, Enum):
    """
    Creates a Deployment for an API.


    """

    AutoDeployed = "AutoDeployed"
    """
    Specifies whether a deployment was automatically released.


    """

    CreatedDate = "CreatedDate"
    """
    The date and time when the Deployment resource was created.


    """

    DeploymentId = "DeploymentId"
    """
    The identifier for the deployment.


    """

    DeploymentStatus = "DeploymentStatus"
    """
    The status of the deployment: PENDING, FAILED, or SUCCEEDED.


    """

    DeploymentStatusMessage = "DeploymentStatusMessage"
    """
    May contain additional feedback on the status of an API deployment.


    """

    Description = "Description"
    """
    The description for the deployment.


    """



class api_model(Rendered_Resource):
    """

    Updates an Api resource.
    
    """


    ApiKeySelectionExpression: Optional[Union[str, Cloud_Output]]
    """
    The route selection expression for the API. For HTTP APIs, the routeSelectionExpression must be ${request.method} ${request.path}. If not provided, this will be the default for HTTP APIs. This property is required for WebSocket APIs.
    """


    CorsConfiguration: Optional[Union[Cors, Cloud_Output]] 
    """
    A CORS configuration. Supported only for HTTP APIs. See [Configuring CORS](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html) for more information.
    """


    CredentialsArn: Optional[Union[str, Cloud_Output]]
    """
    This property is part of quick create. It specifies the credentials required for the integration, if any. For a Lambda integration, three options are available. To specify an IAM Role for API Gateway to assume, use the role's Amazon Resource Name (ARN). To require that the caller's identity be passed through from the request, specify arn:aws:iam::*:user/*. To use resource-based permissions on supported AWS services, specify null. Currently, this property is not used for HTTP integrations. Supported only for HTTP APIs.
    """


    Description: Optional[Union[str, Cloud_Output]]
    """
    The description of the API.
    """


    DisableSchemaValidation: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether clients can invoke your API by using the default execute-api endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.
    """


    DisableExecuteApiEndpoint: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether clients can invoke your API by using the default execute-api endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.
    """


    Name: Union[str, Cloud_Output]
    """
    The name of the API.
    """


    ProtocolType: Union[ProtocolType, Cloud_Output] 
    """
    The API protocol.
    """


    RouteKey: Optional[Union[str, Cloud_Output]]
    """
    This property is part of quick create. If you don't specify a routeKey, a default route of $default is created. The $default route acts as a catch-all for any request made to your API, for a particular stage. The $default route key can't be modified. You can add routes after creating the API, and you can update the route keys of additional routes. Supported only for HTTP APIs.
    """


    RouteSelectionExpression: Optional[Union[str, Cloud_Output]]
    """
    The route selection expression for the API. For HTTP APIs, the routeSelectionExpression must be ${request.method} ${request.path}. If not provided, this will be the default for HTTP APIs. This property is required for WebSocket APIs.
    """


    Tags: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    The collection of tags. Each tag element is associated with a given resource.
    """


    Target: Optional[Union[str, Cloud_Output]]
    """
    This property is part of quick create. Quick create produces an API with an integration, a default catch-all route, and a default stage which is configured to automatically deploy changes. For HTTP integrations, specify a fully qualified URL. For Lambda integrations, specify a function ARN. The type of the integration will be HTTP\_PROXY or AWS\_PROXY, respectively. Supported only for HTTP APIs.
    """


    Version: Optional[Union[str, Cloud_Output]]
    """
    A version identifier for the API.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['Name', 'ProtocolType', 'ApiKeySelectionExpression', 'CorsConfiguration', 'CredentialsArn', 'Description', 'DisableSchemaValidation', 'DisableExecuteApiEndpoint', 'RouteKey', 'RouteSelectionExpression', 'Tags', 'Target', 'Version'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class route_model(Rendered_Resource):
    """

    Updates a Route.
    
    """


    ApiId: Union[str, Cloud_Output]
    """
    The API identifier.
    """


    ApiKeyRequired: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether an API key is required for the route. Supported only for WebSocket APIs.
    """


    AuthorizationScopes: Optional[Union[List[str], Cloud_Output]]
    """
    A version identifier for the API.
    """


    AuthorizationType: Optional[Union[AuthorizationType, Cloud_Output]] 
    """
    The authorization type for the route. For WebSocket APIs, valid values are NONE for open access, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer For HTTP APIs, valid values are NONE for open access, JWT for using JSON Web Tokens, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer.
    """


    AuthorizerId: Optional[Union[str, Cloud_Output]]
    """
    The identifier of the Authorizer resource to be associated with this route. The authorizer identifier is generated by API Gateway when you created the authorizer.
    """


    ModelSelectionExpression: Optional[Union[str, Cloud_Output]]
    """
    The route response selection expression for the route. Supported only for WebSocket APIs.
    """


    OperationName: Optional[Union[str, Cloud_Output]]
    """
    The operation name for the route.
    """


    RequestModels: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    The request models for the route. Supported only for WebSocket APIs.
    """


    RequestParameters: Optional[Union[Dict[str,ParameterConstraints], Cloud_Output]]
    """
    The request parameters for the route. Supported only for WebSocket APIs.
    """


    RouteKey: Union[str, Cloud_Output]
    """
    The route key for the route.
    """


    RouteResponseSelectionExpression: Optional[Union[str, Cloud_Output]]
    """
    The route response selection expression for the route. Supported only for WebSocket APIs.
    """


    Target: Optional[Union[str, Cloud_Output]]
    """
    The target for the route.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'RouteKey', 'ApiKeyRequired', 'AuthorizationScopes', 'AuthorizationType', 'AuthorizerId', 'ModelSelectionExpression', 'OperationName', 'RequestModels', 'RequestParameters', 'RouteResponseSelectionExpression', 'Target'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'RouteId'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class integration_model(Rendered_Resource):
    """

    Updates an Integration.
    
    """


    ApiId: Union[str, Cloud_Output]
    """
    The API identifier.
    """


    ConnectionId: Optional[Union[str, Cloud_Output]]
    """
    The ID of the VPC link for a private integration. Supported only for HTTP APIs.
    """


    ConnectionType: Optional[Union[ConnectionType, Cloud_Output]] 
    """
    The type of the network connection to the integration endpoint. Specify INTERNET for connections through the public routable internet or VPC\_LINK for private connections between API Gateway and resources in a VPC. The default value is INTERNET.
    """


    ContentHandlingStrategy: Optional[Union[ContentHandlingStrategy, Cloud_Output]] 
    """
    Supported only for WebSocket APIs. Specifies how to handle response payload content type conversions. Supported values are CONVERT\_TO\_BINARY and CONVERT\_TO\_TEXT, with the following behaviors:

 CONVERT\_TO\_BINARY: Converts a response payload from a Base64-encoded string to the corresponding binary blob.

 CONVERT\_TO\_TEXT: Converts a response payload from a binary blob to a Base64-encoded string.

 If this property is not defined, the response payload will be passed through from the integration response to the route response or method response without modification.
    """


    CredentialsArn: Optional[Union[str, Cloud_Output]]
    """
    Specifies the credentials required for the integration, if any. For AWS integrations, three options are available. To specify an IAM Role for API Gateway to assume, use the role's Amazon Resource Name (ARN). To require that the caller's identity be passed through from the request, specify the string arn:aws:iam::*:user/*. To use resource-based permissions on supported AWS services, specify null.
    """


    Description: Optional[Union[str, Cloud_Output]]
    """
    The description of the integration.
    """


    IntegrationMethod: Optional[Union[str, Cloud_Output]]
    """
    Specifies the format of the payload sent to an integration. Required for HTTP APIs.
    """


    IntegrationSubtype: Optional[Union[str, Cloud_Output]]
    """
    Supported only for HTTP API AWS\_PROXY integrations. Specifies the AWS service action to invoke. To learn more, see [Integration subtype reference](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-aws-services-reference.html).
    """


    IntegrationType: Union[IntegrationType, Cloud_Output] 
    """
    The integration type of an integration. One of the following:

 AWS: for integrating the route or method request with an AWS service action, including the Lambda function-invoking action. With the Lambda function-invoking action, this is referred to as the Lambda custom integration. With any other AWS service action, this is known as AWS integration. Supported only for WebSocket APIs.

 AWS\_PROXY: for integrating the route or method request with a Lambda function or other AWS service action. This integration is also referred to as a Lambda proxy integration.

 HTTP: for integrating the route or method request with an HTTP endpoint. This integration is also referred to as the HTTP custom integration. Supported only for WebSocket APIs.

 HTTP\_PROXY: for integrating the route or method request with an HTTP endpoint, with the client request passed through as-is. This is also referred to as HTTP proxy integration. For HTTP API private integrations, use an HTTP\_PROXY integration.

 MOCK: for integrating the route or method request with API Gateway as a "loopback" endpoint without invoking any backend. Supported only for WebSocket APIs.
    """


    IntegrationUri: Optional[Union[str, Cloud_Output]]
    """
    For a Lambda integration, specify the URI of a Lambda function.

 For an HTTP integration, specify a fully-qualified URL.

 For an HTTP API private integration, specify the ARN of an Application Load Balancer listener, Network Load Balancer listener, or AWS Cloud Map service. If you specify the ARN of an AWS Cloud Map service, API Gateway uses DiscoverInstances to identify resources. You can use query parameters to target specific resources. To learn more, see [DiscoverInstances](https://docs.aws.amazon.com/cloud-map/latest/api/API_DiscoverInstances.html). For private integrations, all resources must be owned by the same AWS account.
    """


    PassthroughBehavior: Optional[Union[PassthroughBehavior, Cloud_Output]] 
    """
    Specifies the pass-through behavior for incoming requests based on the Content-Type header in the request, and the available mapping templates specified as the requestTemplates property on the Integration resource. There are three valid values: WHEN\_NO\_MATCH, WHEN\_NO\_TEMPLATES, and NEVER. Supported only for WebSocket APIs.

 WHEN\_NO\_MATCH passes the request body for unmapped content types through to the integration backend without transformation.

 NEVER rejects unmapped content types with an HTTP 415 Unsupported Media Type response.

 WHEN\_NO\_TEMPLATES allows pass-through when the integration has no content types mapped to templates. However, if there is at least one content type defined, unmapped content types will be rejected with the same HTTP 415 Unsupported Media Type response.
    """


    PayloadFormatVersion: Optional[Union[str, Cloud_Output]]
    """
    Specifies the format of the payload sent to an integration. Required for HTTP APIs.
    """


    RequestParameters: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    For WebSocket APIs, a key-value map specifying request parameters that are passed from the method request to the backend. The key is an integration request parameter name and the associated value is a method request parameter value or static value that must be enclosed within single quotes and pre-encoded as required by the backend. The method request parameter value must match the pattern of method.request.{location}.{name}
 , where 
 {location}
 is querystring, path, or header; and 
 {name}
 must be a valid and unique method request parameter name.

 For HTTP API integrations with a specified integrationSubtype, request parameters are a key-value map specifying parameters that are passed to AWS\_PROXY integrations. You can provide static values, or map request data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Working with AWS service integrations for HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-aws-services.html).

 For HTTP API integrations without a specified integrationSubtype request parameters are a key-value map specifying how to transform HTTP requests before sending them to the backend. The key should follow the pattern <action>:<header|querystring|path>.<location> where action can be append, overwrite or remove. For values, you can provide static values, or map request data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Transforming API requests and responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).
    """


    RequestTemplates: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    Represents a map of Velocity templates that are applied on the request payload based on the value of the Content-Type header sent by the client. The content type value is the key in this map, and the template (as a String) is the value. Supported only for WebSocket APIs.
    """


    ResponseParameters: Optional[Union[Dict[str,None], Cloud_Output]]
    """
    Supported only for HTTP APIs. You use response parameters to transform the HTTP response from a backend integration before returning the response to clients. Specify a key-value map from a selection key to response parameters. The selection key must be a valid HTTP status code within the range of 200-599. Response parameters are a key-value map. The key must match pattern <action>:<header>.<location> or overwrite.statuscode. The action can be append, overwrite or remove. The value can be a static value, or map to response data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Transforming API requests and responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).
    """


    TemplateSelectionExpression: Optional[Union[str, Cloud_Output]]
    """
    The template selection expression for the integration.
    """


    TimeoutInMillis: Optional[Union[int, Cloud_Output]]
    """
    Custom timeout between 50 and 29,000 milliseconds for WebSocket APIs and between 50 and 30,000 milliseconds for HTTP APIs. The default timeout is 29 seconds for WebSocket APIs and 30 seconds for HTTP APIs.
    """


    TlsConfig: Optional[Union[TlsConfigInput, Cloud_Output]] 
    """
    The TLS configuration for a private integration. If you specify a TLS configuration, private integration traffic uses the HTTPS protocol. Supported only for HTTP APIs.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'IntegrationType', 'ConnectionId', 'ConnectionType', 'ContentHandlingStrategy', 'CredentialsArn', 'Description', 'IntegrationMethod', 'IntegrationSubtype', 'IntegrationUri', 'PassthroughBehavior', 'PayloadFormatVersion', 'RequestParameters', 'RequestTemplates', 'ResponseParameters', 'TemplateSelectionExpression', 'TimeoutInMillis', 'TlsConfig'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'IntegrationId'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class stage_model(Rendered_Resource):
    """

    Updates a Stage.
    
    """


    AccessLogSettings: Optional[Union[AccessLogSettings, Cloud_Output]] 
    """
    Settings for logging access in this stage.
    """


    ApiId: Union[str, Cloud_Output]
    """
    The API identifier.
    """


    AutoDeploy: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether updates to an API automatically trigger a new deployment. The default value is false.
    """


    ClientCertificateId: Optional[Union[str, Cloud_Output]]
    """
    The deployment identifier of the API stage.
    """


    DefaultRouteSettings: Optional[Union[RouteSettings, Cloud_Output]] 
    """
    The default route settings for the stage.
    """


    DeploymentId: Optional[Union[str, Cloud_Output]]
    """
    The deployment identifier of the API stage.
    """


    Description: Optional[Union[str, Cloud_Output]]
    """
    The description for the API stage.
    """


    RouteSettings: Optional[Union[Dict[str,RouteSettings], Cloud_Output]]
    """
    Route settings for the stage, by routeKey.
    """


    StageName: Union[str, Cloud_Output]
    """
    The name of the stage.
    """


    StageVariables: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A map that defines the stage variables for a Stage. Variable names can have alphanumeric and underscore characters, and the values must match [A-Za-z0-9-.\_~:/?#&=,]+.
    """


    Tags: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    The collection of tags. Each tag element is associated with a given resource.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'StageName', 'AccessLogSettings', 'AutoDeploy', 'ClientCertificateId', 'DefaultRouteSettings', 'DeploymentId', 'Description', 'RouteSettings', 'StageVariables', 'Tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'StageName'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class deployment_model(Rendered_Resource):
    """

    Updates a Deployment.
    
    """


    ApiId: Union[str, Cloud_Output]
    """
    The API identifier.
    """


    Description: Optional[Union[str, Cloud_Output]]
    """
    The description for the deployment resource.
    """


    StageName: Optional[Union[str, Cloud_Output]]
    """
    The name of the Stage resource for the Deployment resource to create.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'Description', 'StageName'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['ApiId', 'DeploymentId'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


