from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Callable, Any
from pathlib import Path


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .apigatewayv2_models import *


class Api(Cdev_Resource):
    """
    Updates an Api resource.


    """

    def __init__(self, cdev_name: str, Name: str, ProtocolType: ProtocolType, ApiKeySelectionExpression: str=None, CorsConfiguration: Cors=None, CredentialsArn: str=None, Description: str=None, DisableSchemaValidation: bool=None, DisableExecuteApiEndpoint: bool=None, RouteKey: str=None, RouteSelectionExpression: str=None, Tags: Dict[str, str]=None, Target: str=None, Version: str=None):
        ""
        super().__init__(cdev_name)

        self.ApiKeySelectionExpression = ApiKeySelectionExpression
        """
        The route selection expression for the API. For HTTP APIs, the routeSelectionExpression must be ${request.method} ${request.path}. If not provided, this will be the default for HTTP APIs. This property is required for WebSocket APIs.


        """

        self.CorsConfiguration = CorsConfiguration
        """
        A CORS configuration. Supported only for HTTP APIs. See [Configuring CORS](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html) for more information.


        """

        self.CredentialsArn = CredentialsArn
        """
        This property is part of quick create. It specifies the credentials required for the integration, if any. For a Lambda integration, three options are available. To specify an IAM Role for API Gateway to assume, use the role's Amazon Resource Name (ARN). To require that the caller's identity be passed through from the request, specify arn:aws:iam::*:user/*. To use resource-based permissions on supported AWS services, specify null. Currently, this property is not used for HTTP integrations. Supported only for HTTP APIs.


        """

        self.Description = Description
        """
        The description of the API.


        """

        self.DisableSchemaValidation = DisableSchemaValidation
        """
        Specifies whether clients can invoke your API by using the default execute-api endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.


        """

        self.DisableExecuteApiEndpoint = DisableExecuteApiEndpoint
        """
        Specifies whether clients can invoke your API by using the default execute-api endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.


        """

        self.Name = Name
        """
        The name of the API.


        """

        self.ProtocolType = ProtocolType
        """
        The API protocol.


        """

        self.RouteKey = RouteKey
        """
        This property is part of quick create. If you don't specify a routeKey, a default route of $default is created. The $default route acts as a catch-all for any request made to your API, for a particular stage. The $default route key can't be modified. You can add routes after creating the API, and you can update the route keys of additional routes. Supported only for HTTP APIs.


        """

        self.RouteSelectionExpression = RouteSelectionExpression
        """
        The route selection expression for the API. For HTTP APIs, the routeSelectionExpression must be ${request.method} ${request.path}. If not provided, this will be the default for HTTP APIs. This property is required for WebSocket APIs.


        """

        self.Tags = Tags
        """
        The collection of tags. Each tag element is associated with a given resource.


        """

        self.Target = Target
        """
        This property is part of quick create. Quick create produces an API with an integration, a default catch-all route, and a default stage which is configured to automatically deploy changes. For HTTP integrations, specify a fully qualified URL. For Lambda integrations, specify a function ARN. The type of the integration will be HTTP\_PROXY or AWS\_PROXY, respectively. Supported only for HTTP APIs.


        """

        self.Version = Version
        """
        A version identifier for the API.


        """

        self.hash = hasher.hash_list([self.Name, self.ProtocolType, self.ApiKeySelectionExpression, self.CorsConfiguration, self.CredentialsArn, self.Description, self.DisableSchemaValidation, self.DisableExecuteApiEndpoint, self.RouteKey, self.RouteSelectionExpression, self.Tags, self.Target, self.Version])

    def render(self) -> api_model:
        data = {
            "ruuid": "cdev::aws::apigatewayv2::api",
            "name": self.name,
            "hash": self.hash,
            "ApiKeySelectionExpression": self.ApiKeySelectionExpression,
            "CorsConfiguration": self.CorsConfiguration,
            "CredentialsArn": self.CredentialsArn,
            "Description": self.Description,
            "DisableSchemaValidation": self.DisableSchemaValidation,
            "DisableExecuteApiEndpoint": self.DisableExecuteApiEndpoint,
            "Name": self.Name,
            "ProtocolType": self.ProtocolType,
            "RouteKey": self.RouteKey,
            "RouteSelectionExpression": self.RouteSelectionExpression,
            "Tags": self.Tags,
            "Target": self.Target,
            "Version": self.Version,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return api_model(**filtered_data)

    def from_output(self, key: api_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::api::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::api::{self.hash}", "key": key, "type": "cdev_output"})


class Route(Cdev_Resource):
    """
    Updates a Route.


    """

    def __init__(self, cdev_name: str, ApiId: str, RouteKey: str, ApiKeyRequired: bool=None, AuthorizationScopes: List[str]=None, AuthorizationType: AuthorizationType=None, AuthorizerId: str=None, ModelSelectionExpression: str=None, OperationName: str=None, RequestModels: Dict[str, str]=None, RequestParameters: Dict[str, ParameterConstraints]=None, RouteResponseSelectionExpression: str=None, Target: str=None):
        ""
        super().__init__(cdev_name)

        self.ApiId = ApiId
        """
        The API identifier.


        """

        self.ApiKeyRequired = ApiKeyRequired
        """
        Specifies whether an API key is required for the route. Supported only for WebSocket APIs.


        """

        self.AuthorizationScopes = AuthorizationScopes
        """
        A version identifier for the API.


        """

        self.AuthorizationType = AuthorizationType
        """
        The authorization type for the route. For WebSocket APIs, valid values are NONE for open access, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer For HTTP APIs, valid values are NONE for open access, JWT for using JSON Web Tokens, AWS\_IAM for using AWS IAM permissions, and CUSTOM for using a Lambda authorizer.


        """

        self.AuthorizerId = AuthorizerId
        """
        The identifier of the Authorizer resource to be associated with this route. The authorizer identifier is generated by API Gateway when you created the authorizer.


        """

        self.ModelSelectionExpression = ModelSelectionExpression
        """
        The route response selection expression for the route. Supported only for WebSocket APIs.


        """

        self.OperationName = OperationName
        """
        The operation name for the route.


        """

        self.RequestModels = RequestModels
        """
        The request models for the route. Supported only for WebSocket APIs.


        """

        self.RequestParameters = RequestParameters
        """
        The request parameters for the route. Supported only for WebSocket APIs.


        """

        self.RouteKey = RouteKey
        """
        The route key for the route.


        """

        self.RouteResponseSelectionExpression = RouteResponseSelectionExpression
        """
        The route response selection expression for the route. Supported only for WebSocket APIs.


        """

        self.Target = Target
        """
        The target for the route.


        """

        self.hash = hasher.hash_list([self.ApiId, self.RouteKey, self.ApiKeyRequired, self.AuthorizationScopes, self.AuthorizationType, self.AuthorizerId, self.ModelSelectionExpression, self.OperationName, self.RequestModels, self.RequestParameters, self.RouteResponseSelectionExpression, self.Target])

    def render(self) -> route_model:
        data = {
            "ruuid": "cdev::aws::apigatewayv2::route",
            "name": self.name,
            "hash": self.hash,
            "ApiId": self.ApiId,
            "ApiKeyRequired": self.ApiKeyRequired,
            "AuthorizationScopes": self.AuthorizationScopes,
            "AuthorizationType": self.AuthorizationType,
            "AuthorizerId": self.AuthorizerId,
            "ModelSelectionExpression": self.ModelSelectionExpression,
            "OperationName": self.OperationName,
            "RequestModels": self.RequestModels,
            "RequestParameters": self.RequestParameters,
            "RouteKey": self.RouteKey,
            "RouteResponseSelectionExpression": self.RouteResponseSelectionExpression,
            "Target": self.Target,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return route_model(**filtered_data)

    def from_output(self, key: route_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::route::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::route::{self.hash}", "key": key, "type": "cdev_output"})


class Integration(Cdev_Resource):
    """
    Updates an Integration.


    """

    def __init__(self, cdev_name: str, ApiId: str, IntegrationType: IntegrationType, ConnectionId: str=None, ConnectionType: ConnectionType=None, ContentHandlingStrategy: ContentHandlingStrategy=None, CredentialsArn: str=None, Description: str=None, IntegrationMethod: str=None, IntegrationSubtype: str=None, IntegrationUri: str=None, PassthroughBehavior: PassthroughBehavior=None, PayloadFormatVersion: str=None, RequestParameters: Dict[str, str]=None, RequestTemplates: Dict[str, str]=None, ResponseParameters: Dict[str, None]=None, TemplateSelectionExpression: str=None, TimeoutInMillis: int=None, TlsConfig: TlsConfigInput=None):
        ""
        super().__init__(cdev_name)

        self.ApiId = ApiId
        """
        The API identifier.


        """

        self.ConnectionId = ConnectionId
        """
        The ID of the VPC link for a private integration. Supported only for HTTP APIs.


        """

        self.ConnectionType = ConnectionType
        """
        The type of the network connection to the integration endpoint. Specify INTERNET for connections through the public routable internet or VPC\_LINK for private connections between API Gateway and resources in a VPC. The default value is INTERNET.


        """

        self.ContentHandlingStrategy = ContentHandlingStrategy
        """
        Supported only for WebSocket APIs. Specifies how to handle response payload content type conversions. Supported values are CONVERT\_TO\_BINARY and CONVERT\_TO\_TEXT, with the following behaviors:

 CONVERT\_TO\_BINARY: Converts a response payload from a Base64-encoded string to the corresponding binary blob.

 CONVERT\_TO\_TEXT: Converts a response payload from a binary blob to a Base64-encoded string.

 If this property is not defined, the response payload will be passed through from the integration response to the route response or method response without modification.


        """

        self.CredentialsArn = CredentialsArn
        """
        Specifies the credentials required for the integration, if any. For AWS integrations, three options are available. To specify an IAM Role for API Gateway to assume, use the role's Amazon Resource Name (ARN). To require that the caller's identity be passed through from the request, specify the string arn:aws:iam::*:user/*. To use resource-based permissions on supported AWS services, specify null.


        """

        self.Description = Description
        """
        The description of the integration.


        """

        self.IntegrationMethod = IntegrationMethod
        """
        Specifies the format of the payload sent to an integration. Required for HTTP APIs.


        """

        self.IntegrationSubtype = IntegrationSubtype
        """
        Supported only for HTTP API AWS\_PROXY integrations. Specifies the AWS service action to invoke. To learn more, see [Integration subtype reference](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-aws-services-reference.html).


        """

        self.IntegrationType = IntegrationType
        """
        The integration type of an integration. One of the following:

 AWS: for integrating the route or method request with an AWS service action, including the Lambda function-invoking action. With the Lambda function-invoking action, this is referred to as the Lambda custom integration. With any other AWS service action, this is known as AWS integration. Supported only for WebSocket APIs.

 AWS\_PROXY: for integrating the route or method request with a Lambda function or other AWS service action. This integration is also referred to as a Lambda proxy integration.

 HTTP: for integrating the route or method request with an HTTP endpoint. This integration is also referred to as the HTTP custom integration. Supported only for WebSocket APIs.

 HTTP\_PROXY: for integrating the route or method request with an HTTP endpoint, with the client request passed through as-is. This is also referred to as HTTP proxy integration. For HTTP API private integrations, use an HTTP\_PROXY integration.

 MOCK: for integrating the route or method request with API Gateway as a "loopback" endpoint without invoking any backend. Supported only for WebSocket APIs.


        """

        self.IntegrationUri = IntegrationUri
        """
        For a Lambda integration, specify the URI of a Lambda function.

 For an HTTP integration, specify a fully-qualified URL.

 For an HTTP API private integration, specify the ARN of an Application Load Balancer listener, Network Load Balancer listener, or AWS Cloud Map service. If you specify the ARN of an AWS Cloud Map service, API Gateway uses DiscoverInstances to identify resources. You can use query parameters to target specific resources. To learn more, see [DiscoverInstances](https://docs.aws.amazon.com/cloud-map/latest/api/API_DiscoverInstances.html). For private integrations, all resources must be owned by the same AWS account.


        """

        self.PassthroughBehavior = PassthroughBehavior
        """
        Specifies the pass-through behavior for incoming requests based on the Content-Type header in the request, and the available mapping templates specified as the requestTemplates property on the Integration resource. There are three valid values: WHEN\_NO\_MATCH, WHEN\_NO\_TEMPLATES, and NEVER. Supported only for WebSocket APIs.

 WHEN\_NO\_MATCH passes the request body for unmapped content types through to the integration backend without transformation.

 NEVER rejects unmapped content types with an HTTP 415 Unsupported Media Type response.

 WHEN\_NO\_TEMPLATES allows pass-through when the integration has no content types mapped to templates. However, if there is at least one content type defined, unmapped content types will be rejected with the same HTTP 415 Unsupported Media Type response.


        """

        self.PayloadFormatVersion = PayloadFormatVersion
        """
        Specifies the format of the payload sent to an integration. Required for HTTP APIs.


        """

        self.RequestParameters = RequestParameters
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

        self.RequestTemplates = RequestTemplates
        """
        Represents a map of Velocity templates that are applied on the request payload based on the value of the Content-Type header sent by the client. The content type value is the key in this map, and the template (as a String) is the value. Supported only for WebSocket APIs.


        """

        self.ResponseParameters = ResponseParameters
        """
        Supported only for HTTP APIs. You use response parameters to transform the HTTP response from a backend integration before returning the response to clients. Specify a key-value map from a selection key to response parameters. The selection key must be a valid HTTP status code within the range of 200-599. Response parameters are a key-value map. The key must match pattern <action>:<header>.<location> or overwrite.statuscode. The action can be append, overwrite or remove. The value can be a static value, or map to response data, stage variables, or context variables that are evaluated at runtime. To learn more, see [Transforming API requests and responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).


        """

        self.TemplateSelectionExpression = TemplateSelectionExpression
        """
        The template selection expression for the integration.


        """

        self.TimeoutInMillis = TimeoutInMillis
        """
        Custom timeout between 50 and 29,000 milliseconds for WebSocket APIs and between 50 and 30,000 milliseconds for HTTP APIs. The default timeout is 29 seconds for WebSocket APIs and 30 seconds for HTTP APIs.


        """

        self.TlsConfig = TlsConfig
        """
        The TLS configuration for a private integration. If you specify a TLS configuration, private integration traffic uses the HTTPS protocol. Supported only for HTTP APIs.


        """

        self.hash = hasher.hash_list([self.ApiId, self.IntegrationType, self.ConnectionId, self.ConnectionType, self.ContentHandlingStrategy, self.CredentialsArn, self.Description, self.IntegrationMethod, self.IntegrationSubtype, self.IntegrationUri, self.PassthroughBehavior, self.PayloadFormatVersion, self.RequestParameters, self.RequestTemplates, self.ResponseParameters, self.TemplateSelectionExpression, self.TimeoutInMillis, self.TlsConfig])

    def render(self) -> integration_model:
        data = {
            "ruuid": "cdev::aws::apigatewayv2::integration",
            "name": self.name,
            "hash": self.hash,
            "ApiId": self.ApiId,
            "ConnectionId": self.ConnectionId,
            "ConnectionType": self.ConnectionType,
            "ContentHandlingStrategy": self.ContentHandlingStrategy,
            "CredentialsArn": self.CredentialsArn,
            "Description": self.Description,
            "IntegrationMethod": self.IntegrationMethod,
            "IntegrationSubtype": self.IntegrationSubtype,
            "IntegrationType": self.IntegrationType,
            "IntegrationUri": self.IntegrationUri,
            "PassthroughBehavior": self.PassthroughBehavior,
            "PayloadFormatVersion": self.PayloadFormatVersion,
            "RequestParameters": self.RequestParameters,
            "RequestTemplates": self.RequestTemplates,
            "ResponseParameters": self.ResponseParameters,
            "TemplateSelectionExpression": self.TemplateSelectionExpression,
            "TimeoutInMillis": self.TimeoutInMillis,
            "TlsConfig": self.TlsConfig,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return integration_model(**filtered_data)

    def from_output(self, key: integration_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::integration::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::integration::{self.hash}", "key": key, "type": "cdev_output"})


class Stage(Cdev_Resource):
    """
    Updates a Stage.


    """

    def __init__(self, cdev_name: str, ApiId: str, StageName: str, AccessLogSettings: AccessLogSettings=None, AutoDeploy: bool=None, ClientCertificateId: str=None, DefaultRouteSettings: RouteSettings=None, DeploymentId: str=None, Description: str=None, RouteSettings: Dict[str, RouteSettings]=None, StageVariables: Dict[str, str]=None, Tags: Dict[str, str]=None):
        ""
        super().__init__(cdev_name)

        self.AccessLogSettings = AccessLogSettings
        """
        Settings for logging access in this stage.


        """

        self.ApiId = ApiId
        """
        The API identifier.


        """

        self.AutoDeploy = AutoDeploy
        """
        Specifies whether updates to an API automatically trigger a new deployment. The default value is false.


        """

        self.ClientCertificateId = ClientCertificateId
        """
        The deployment identifier of the API stage.


        """

        self.DefaultRouteSettings = DefaultRouteSettings
        """
        The default route settings for the stage.


        """

        self.DeploymentId = DeploymentId
        """
        The deployment identifier of the API stage.


        """

        self.Description = Description
        """
        The description for the API stage.


        """

        self.RouteSettings = RouteSettings
        """
        Route settings for the stage, by routeKey.


        """

        self.StageName = StageName
        """
        The name of the stage.


        """

        self.StageVariables = StageVariables
        """
        A map that defines the stage variables for a Stage. Variable names can have alphanumeric and underscore characters, and the values must match [A-Za-z0-9-.\_~:/?#&=,]+.


        """

        self.Tags = Tags
        """
        The collection of tags. Each tag element is associated with a given resource.


        """

        self.hash = hasher.hash_list([self.ApiId, self.StageName, self.AccessLogSettings, self.AutoDeploy, self.ClientCertificateId, self.DefaultRouteSettings, self.DeploymentId, self.Description, self.RouteSettings, self.StageVariables, self.Tags])

    def render(self) -> stage_model:
        data = {
            "ruuid": "cdev::aws::apigatewayv2::stage",
            "name": self.name,
            "hash": self.hash,
            "AccessLogSettings": self.AccessLogSettings,
            "ApiId": self.ApiId,
            "AutoDeploy": self.AutoDeploy,
            "ClientCertificateId": self.ClientCertificateId,
            "DefaultRouteSettings": self.DefaultRouteSettings,
            "DeploymentId": self.DeploymentId,
            "Description": self.Description,
            "RouteSettings": self.RouteSettings,
            "StageName": self.StageName,
            "StageVariables": self.StageVariables,
            "Tags": self.Tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return stage_model(**filtered_data)

    def from_output(self, key: stage_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::stage::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::stage::{self.hash}", "key": key, "type": "cdev_output"})


class Deployment(Cdev_Resource):
    """
    Updates a Deployment.


    """

    def __init__(self, cdev_name: str, ApiId: str, Description: str=None, StageName: str=None):
        ""
        super().__init__(cdev_name)

        self.ApiId = ApiId
        """
        The API identifier.


        """

        self.Description = Description
        """
        The description for the deployment resource.


        """

        self.StageName = StageName
        """
        The name of the Stage resource for the Deployment resource to create.


        """

        self.hash = hasher.hash_list([self.ApiId, self.Description, self.StageName])

    def render(self) -> deployment_model:
        data = {
            "ruuid": "cdev::aws::apigatewayv2::deployment",
            "name": self.name,
            "hash": self.hash,
            "ApiId": self.ApiId,
            "Description": self.Description,
            "StageName": self.StageName,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return deployment_model(**filtered_data)

    def from_output(self, key: deployment_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::deployment::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::apigatewayv2::deployment::{self.hash}", "key": key, "type": "cdev_output"})


