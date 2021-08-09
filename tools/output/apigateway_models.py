from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Union, Dict

from ...models import Cloud_Output, Rendered_Resource

from ...backend import cloud_mapper_manager


class ApiKeySourceType(str, Enum): 


    HEADER = 'HEADER'
    
    AUTHORIZER = 'AUTHORIZER'
    

class EndpointType(str, Enum): 
    """
    The endpoint type. The valid values are `EDGE` for edge-optimized API setup, most suitable for mobile applications; `REGIONAL` for regional API endpoint setup, most suitable for calling from AWS Region; and `PRIVATE` for private APIs.


    """


    REGIONAL = 'REGIONAL'
    
    EDGE = 'EDGE'
    
    PRIVATE = 'PRIVATE'
    

class EndpointConfiguration(BaseModel):
    """
    The endpoint configuration to indicate the types of endpoints an API (RestApi) or its custom domain name (DomainName) has. 


    """


    types: Union[List[str], Cloud_Output]
    """
    The endpoint type. The valid values are `EDGE` for edge-optimized API setup, most suitable for mobile applications; `REGIONAL` for regional API endpoint setup, most suitable for calling from AWS Region; and `PRIVATE` for private APIs.


    """

    vpcEndpointIds: Union[List[str], Cloud_Output]
    """
    The description for the Deployment resource to create.


    """


    def __init__(self, types: List[str], vpcEndpointIds: List[str] ):
        "My doc string"
        super().__init__(**{
            "types": types,
            "vpcEndpointIds": vpcEndpointIds,
        })        



class IntegrationType(str, Enum): 
    """
    The integration type. The valid value is `HTTP` for integrating an API method with an HTTP backend; `AWS` with any AWS service endpoints; `MOCK` for testing without actually invoking the backend; `HTTP_PROXY` for integrating with the HTTP proxy integration; `AWS_PROXY` for integrating with the Lambda proxy integration. 


    """


    HTTP = 'HTTP'
    
    AWS = 'AWS'
    
    MOCK = 'MOCK'
    
    HTTP_PROXY = 'HTTP_PROXY'
    
    AWS_PROXY = 'AWS_PROXY'
    

class ConnectionType(str, Enum): 


    INTERNET = 'INTERNET'
    
    VPC_LINK = 'VPC_LINK'
    

class ContentHandlingStrategy(str, Enum): 


    CONVERT_TO_BINARY = 'CONVERT_TO_BINARY'
    
    CONVERT_TO_TEXT = 'CONVERT_TO_TEXT'
    

class TlsConfig(BaseModel):


    insecureSkipVerification: Union[bool, Cloud_Output]
    """
    Specifies whether or not API Gateway skips verification that the certificate for an integration endpoint is issued by a [supported certificate authority](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-supported-certificate-authorities-for-http-endpoints.html). This isn’t recommended, but it enables you to use certificates that are signed by private certificate authorities, or certificates that are self-signed. If enabled, API Gateway still performs basic certificate validation, which includes checking the certificate's expiration date, hostname, and presence of a root certificate authority. Supported only for `HTTP` and `HTTP_PROXY` integrations.


    """


    def __init__(self, insecureSkipVerification: bool ):
        "My doc string"
        super().__init__(**{
            "insecureSkipVerification": insecureSkipVerification,
        })        



class Op(str, Enum): 


    add = 'add'
    
    remove = 'remove'
    
    replace = 'replace'
    
    move = 'move'
    
    copy = 'copy'
    
    test = 'test'
    

class PatchOperation(BaseModel):
    """
    A single patch operation to apply to the specified resource. Please refer to http://tools.ietf.org/html/rfc6902#section-4 for an explanation of how each operation is used.
    """


    op: Union[Op, Cloud_Output]
    """
     An update operation to be performed with this PATCH request. The valid value can be `add`, `remove`, `replace` or `copy`. Not all valid operations are supported for a given resource. Support of the operations depends on specific operational contexts. Attempts to apply an unsupported operation on a resource will return an error message.


    """

    path: Union[str, Cloud_Output]
    """
    The `copy` update operation's source as identified by a `JSON-Pointer` value referencing the location within the targeted resource to copy the value from. For example, to promote a canary deployment, you copy the canary deployment ID to the affiliated deployment ID by calling a PATCH request on a Stage resource with `"op":"copy"`, `"from":"/canarySettings/deploymentId"` and `"path":"/deploymentId"`.


    """

    value: Union[str, Cloud_Output]
    """
    The `copy` update operation's source as identified by a `JSON-Pointer` value referencing the location within the targeted resource to copy the value from. For example, to promote a canary deployment, you copy the canary deployment ID to the affiliated deployment ID by calling a PATCH request on a Stage resource with `"op":"copy"`, `"from":"/canarySettings/deploymentId"` and `"path":"/deploymentId"`.


    """

    fromx: Union[str, Cloud_Output]
    """
    The `copy` update operation's source as identified by a `JSON-Pointer` value referencing the location within the targeted resource to copy the value from. For example, to promote a canary deployment, you copy the canary deployment ID to the affiliated deployment ID by calling a PATCH request on a Stage resource with `"op":"copy"`, `"from":"/canarySettings/deploymentId"` and `"path":"/deploymentId"`.


    """


    def __init__(self, op: Op, path: str, value: str, fromx: str ):
        "My doc string"
        super().__init__(**{
            "op": op,
            "path": path,
            "value": value,
            "fromx": fromx,
        })        



class CacheClusterSize(str, Enum): 
    """
    Returns the size of the **CacheCluster**.


    """
    p = 'p'

    #0.5 = '0.5'
    #
    #1.6 = '1.6'
    #
    #6.1 = '6.1'
    #
    #13.5 = '13.5'
    #
    #28.4 = '28.4'
    #
    #58.2 = '58.2'
    #
    #118 = '118'
    #
    #237 = '237'
    

class CanarySettings(BaseModel):
    """
    Configuration settings of a canary deployment.


    """


    percentTraffic: Union[int, Cloud_Output]
    """
    The percent (0-100) of traffic diverted to a canary deployment.


    """

    deploymentId: Union[str, Cloud_Output]
    """
    The ID of the canary deployment.


    """

    stageVariableOverrides: Dict[str, str]
    """
    Stage variables overridden for a canary release deployment, including new stage variables introduced in the canary. These stage variables are represented as a string-to-string map between stage variable names and their values.


    """

    useStageCache: Union[bool, Cloud_Output]
    """
    A Boolean flag to indicate whether the canary deployment uses the stage cache or not.


    """


    def __init__(self, percentTraffic: int, deploymentId: str, stageVariableOverrides: Dict, useStageCache: bool ):
        "My doc string"
        super().__init__(**{
            "percentTraffic": percentTraffic,
            "deploymentId": deploymentId,
            "stageVariableOverrides": stageVariableOverrides,
            "useStageCache": useStageCache,
        })        




class DeploymentCanarySettings(BaseModel):
    """
    The input configuration for a canary deployment.


    """


    percentTraffic: Union[int, Cloud_Output]
    """
    The percentage (0.0-100.0) of traffic routed to the canary deployment.


    """

    stageVariableOverrides: Dict[str, str]
    """
    A stage variable overrides used for the canary release deployment. They can override existing stage variables or add new stage variables for the canary release deployment. These stage variables are represented as a string-to-string map between stage variable names and their values.


    """

    useStageCache: Union[bool, Cloud_Output]
    """
    A Boolean flag to indicate whether the canary release deployment uses the stage cache or not.


    """


    def __init__(self, percentTraffic: int, stageVariableOverrides: Dict, useStageCache: bool ):
        "My doc string"
        super().__init__(**{
            "percentTraffic": percentTraffic,
            "stageVariableOverrides": stageVariableOverrides,
            "useStageCache": useStageCache,
        })        




class restapi_output(str, Enum):
    """
    Creates a new RestApi resource.


    """

    id = "id"
    """
    The API's identifier. This identifier is unique across all of your APIs in API Gateway.


    """

    name = "name"
    """
    The API's name.


    """

    description = "description"
    """
    The API's description.


    """

    createdDate = "createdDate"
    """
    The timestamp when the API was created.


    """

    version = "version"
    """
    A version identifier for the API.


    """

    warnings = "warnings"
    """
    The warning messages reported when `failonwarnings` is turned on during API import.


    """

    binaryMediaTypes = "binaryMediaTypes"
    """
    The list of binary media types supported by the RestApi. By default, the RestApi supports only UTF-8-encoded text payloads.


    """

    minimumCompressionSize = "minimumCompressionSize"
    """
    A nullable integer that is used to enable compression (with non-negative between 0 and 10485760 (10M) bytes, inclusive) or disable compression (with a null value) on an API. When compression is enabled, compression or decompression is not applied on the payload if the payload size is smaller than this value. Setting it to zero allows compression for any payload size.


    """

    apiKeySource = "apiKeySource"
    """
    The source of the API key for metering requests according to a usage plan. Valid values are: * `HEADER` to read the API key from the `X-API-Key` header of a request.
* `AUTHORIZER` to read the API key from the `UsageIdentifierKey` from a custom authorizer.



    """

    endpointConfiguration = "endpointConfiguration"
    """
    The endpoint configuration of this RestApi showing the endpoint types of the API.


    """

    policy = "policy"
    """
    A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.


    """

    tags = "tags"
    """
    The collection of tags. Each tag element is associated with a given resource.


    """

    disableExecuteApiEndpoint = "disableExecuteApiEndpoint"
    """
    Specifies whether clients can invoke your API by using the default `execute-api` endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.


    """

    root_resource_id = "root_resource_id"



class resource_output(str, Enum):
    """
    Creates a Resource resource.


    """

    id = "id"
    """
    The resource's identifier.


    """

    parentId = "parentId"
    """
    The parent resource's identifier.


    """

    pathPart = "pathPart"
    """
    The last path segment for this resource.


    """

    path = "path"
    """
    The full path for this resource.


    """

    resourceMethods = "resourceMethods"
    """
    Gets an API resource's method of a given HTTP verb.

  The resource methods are a map of methods indexed by methods' HTTP verbs enabled on the resource. This method map is included in the `200 OK` response of the `GET /restapis/{restapi_id}/resources/{resource_id}` or `GET /restapis/{restapi_id}/resources/{resource_id}?embed=methods` request.

 #### Example: Get the GET method of an API resource

 ##### Request

 
```
GET /restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET HTTP/1.1 Content-Type: application/json Host: apigateway.us-east-1.amazonaws.com X-Amz-Date: 20170223T031827Z Authorization: AWS4-HMAC-SHA256 Credential={access_key_ID}/20170223/us-east-1/apigateway/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature={sig4_hash}
```
 ##### Response

 
```
{ "_links": { "curies": [ { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-integration-{rel}.html", "name": "integration", "templated": true }, { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-integration-response-{rel}.html", "name": "integrationresponse", "templated": true }, { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-method-{rel}.html", "name": "method", "templated": true }, { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-method-response-{rel}.html", "name": "methodresponse", "templated": true } ], "self": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET", "name": "GET", "title": "GET" }, "integration:put": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration" }, "method:delete": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET" }, "method:integration": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration" }, "method:responses": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/responses/200", "name": "200", "title": "200" }, "method:update": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET" }, "methodresponse:put": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/responses/{status_code}", "templated": true } }, "apiKeyRequired": false, "authorizationType": "NONE", "httpMethod": "GET", "_embedded": { "method:integration": { "_links": { "self": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration" }, "integration:delete": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration" }, "integration:responses": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200", "name": "200", "title": "200" }, "integration:update": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration" }, "integrationresponse:put": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/{status_code}", "templated": true } }, "cacheKeyParameters": [], "cacheNamespace": "3kzxbg5sa2", "credentials": "arn:aws:iam::123456789012:role/apigAwsProxyRole", "httpMethod": "POST", "passthroughBehavior": "WHEN_NO_MATCH", "requestParameters": { "integration.request.header.Content-Type": "'application/x-amz-json-1.1'" }, "requestTemplates": { "application/json": "{\n}" }, "type": "AWS", "uri": "arn:aws:apigateway:us-east-1:kinesis:action/ListStreams", "_embedded": { "integration:responses": { "_links": { "self": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200", "name": "200", "title": "200" }, "integrationresponse:delete": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200" }, "integrationresponse:update": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200" } }, "responseParameters": { "method.response.header.Content-Type": "'application/xml'" }, "responseTemplates": { "application/json": "$util.urlDecode(\"%3CkinesisStreams%3E#foreach($stream in $input.path('$.StreamNames'))%3Cstream%3E%3Cname%3E$stream%3C/name%3E%3C/stream%3E#end%3C/kinesisStreams%3E\")\n" }, "statusCode": "200" } } }, "method:responses": { "_links": { "self": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/responses/200", "name": "200", "title": "200" }, "methodresponse:delete": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/responses/200" }, "methodresponse:update": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/responses/200" } }, "responseModels": { "application/json": "Empty" }, "responseParameters": { "method.response.header.Content-Type": false }, "statusCode": "200" } } }
```
 If the `OPTIONS` is enabled on the resource, you can follow the example here to get that method. Just replace the `GET` of the last path segment in the request URL with `OPTIONS`.

   
    """



class integration_output(str, Enum):
    """
    Sets up a method's integration.


    """

    type = "type"
    """
    Specifies an API method integration type. The valid value is one of the following:

 * `AWS`: for integrating the API method request with an AWS service action, including the Lambda function-invoking action. With the Lambda function-invoking action, this is referred to as the Lambda custom integration. With any other AWS service action, this is known as AWS integration.
* `AWS_PROXY`: for integrating the API method request with the Lambda function-invoking action with the client request passed through as-is. This integration is also referred to as the Lambda proxy integration.
* `HTTP`: for integrating the API method request with an HTTP endpoint, including a private HTTP endpoint within a VPC. This integration is also referred to as the HTTP custom integration.
* `HTTP_PROXY`: for integrating the API method request with an HTTP endpoint, including a private HTTP endpoint within a VPC, with the client request passed through as-is. This is also referred to as the HTTP proxy integration.
* `MOCK`: for integrating the API method request with API Gateway as a "loop-back" endpoint without invoking any backend.

 For the HTTP and HTTP proxy integrations, each integration can specify a protocol (`http/https`), port and path. Standard 80 and 443 ports are supported as well as custom ports above 1024. An HTTP or HTTP proxy integration with a `connectionType` of `VPC_LINK` is referred to as a private integration and uses a VpcLink to connect API Gateway to a network load balancer of a VPC.


    """

    httpMethod = "httpMethod"
    """
    Specifies the integration's HTTP method type.


    """

    uri = "uri"
    """
    Specifies Uniform Resource Identifier (URI) of the integration endpoint.

 *  For `HTTP` or `HTTP_PROXY` integrations, the URI must be a fully formed, encoded HTTP(S) URL according to the [RFC-3986 specification](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier), for either standard integration, where `connectionType` is not `VPC_LINK`, or private integration, where `connectionType` is `VPC_LINK`. For a private HTTP integration, the URI is not used for routing. 


*  For `AWS` or `AWS_PROXY` integrations, the URI is of the form `arn:aws:apigateway:{region}:{subdomain.service|service}:path|action/{service_api}`. Here, `{Region}` is the API Gateway region (e.g., `us-east-1`); `{service}` is the name of the integrated AWS service (e.g., `s3`); and `{subdomain}` is a designated subdomain supported by certain AWS service for fast host-name lookup. `action` can be used for an AWS service action-based API, using an `Action={name}&{p1}={v1}&p2={v2}...` query string. The ensuing `{service_api}` refers to a supported action `{name}` plus any required input parameters. Alternatively, `path` can be used for an AWS service path-based API. The ensuing `service_api` refers to the path to an AWS service resource, including the region of the integrated AWS service, if applicable. For example, for integration with the S3 API of `[GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectGET.html)`, the `uri` can be either `arn:aws:apigateway:us-west-2:s3:action/GetObject&Bucket={bucket}&Key={key}` or `arn:aws:apigateway:us-west-2:s3:path/{bucket}/{key}`



    """

    connectionType = "connectionType"
    """
    The type of the network connection to the integration endpoint. The valid value is `INTERNET` for connections through the public routable internet or `VPC_LINK` for private connections between API Gateway and a network load balancer in a VPC. The default value is `INTERNET`.


    """

    connectionId = "connectionId"
    """
    The ([`id`](https://docs.aws.amazon.com/apigateway/api-reference/resource/vpc-link/#id)) of the VpcLink used for the integration when `connectionType=VPC_LINK` and undefined, otherwise.


    """

    credentials = "credentials"
    """
    Specifies the credentials required for the integration, if any. For AWS integrations, three options are available. To specify an IAM Role for API Gateway to assume, use the role's Amazon Resource Name (ARN). To require that the caller's identity be passed through from the request, specify the string `arn:aws:iam::\*:user/\*`. To use resource-based permissions on supported AWS services, specify null.


    """

    requestParameters = "requestParameters"
    """
    A key-value map specifying request parameters that are passed from the method request to the back end. The key is an integration request parameter name and the associated value is a method request parameter value or static value that must be enclosed within single quotes and pre-encoded as required by the back end. The method request parameter value must match the pattern of `method.request.{location}.{name}`, where `location` is `querystring`, `path`, or `header` and `name` must be a valid and unique method request parameter name.


    """

    requestTemplates = "requestTemplates"
    """
    Represents a map of Velocity templates that are applied on the request payload based on the value of the Content-Type header sent by the client. The content type value is the key in this map, and the template (as a String) is the value.


    """

    passthroughBehavior = "passthroughBehavior"
    """
      Specifies how the method request body of an unmapped content type will be passed through the integration request to the back end without transformation. A content type is unmapped if no mapping template is defined in the integration or the content type does not match any of the mapped content types, as specified in `requestTemplates`. The valid value is one of the following: 

 * `WHEN_NO_MATCH`: passes the method request body through the integration request to the back end without transformation when the method request content type does not match any content type associated with the mapping templates defined in the integration request.
* `WHEN_NO_TEMPLATES`: passes the method request body through the integration request to the back end without transformation when no mapping template is defined in the integration request. If a template is defined when this option is selected, the method request of an unmapped content-type will be rejected with an HTTP `415 Unsupported Media Type` response.
* `NEVER`: rejects the method request with an HTTP `415 Unsupported Media Type` response when either the method request content type does not match any content type associated with the mapping templates defined in the integration request or no mapping template is defined in the integration request.

 
    """

    contentHandling = "contentHandling"
    """
    Specifies how to handle request payload content type conversions. Supported values are `CONVERT_TO_BINARY` and `CONVERT_TO_TEXT`, with the following behaviors:

 * `CONVERT_TO_BINARY`: Converts a request payload from a Base64-encoded string to the corresponding binary blob.


* `CONVERT_TO_TEXT`: Converts a request payload from a binary blob to a Base64-encoded string.



 If this property is not defined, the request payload will be passed through from the method request to integration request without modification, provided that the `passthroughBehavior` is configured to support payload pass-through.


    """

    timeoutInMillis = "timeoutInMillis"
    """
    Custom timeout between 50 and 29,000 milliseconds. The default value is 29,000 milliseconds or 29 seconds.


    """

    cacheNamespace = "cacheNamespace"
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.


    """

    cacheKeyParameters = "cacheKeyParameters"
    """
    A list of request parameters whose values API Gateway caches. To be valid values for `cacheKeyParameters`, these parameters must also be specified for Method `requestParameters`.


    """

    integrationResponses = "integrationResponses"
    """
    Specifies the integration's responses.

   #### Example: Get integration responses of a method

 ##### Request

  
```
GET /restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200 HTTP/1.1 Content-Type: application/json Host: apigateway.us-east-1.amazonaws.com X-Amz-Date: 20160607T191449Z Authorization: AWS4-HMAC-SHA256 Credential={access_key_ID}/20160607/us-east-1/apigateway/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature={sig4_hash} 
```
 ##### Response

 The successful response returns `200 OK` status and a payload as follows:

 
```
{ "_links": { "curies": { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-integration-response-{rel}.html", "name": "integrationresponse", "templated": true }, "self": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200", "title": "200" }, "integrationresponse:delete": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200" }, "integrationresponse:update": { "href": "/restapis/fugvjdxtri/resources/3kzxbg5sa2/methods/GET/integration/responses/200" } }, "responseParameters": { "method.response.header.Content-Type": "'application/xml'" }, "responseTemplates": { "application/json": "$util.urlDecode(\"%3CkinesisStreams%3E#foreach($stream in $input.path('$.StreamNames'))%3Cstream%3E%3Cname%3E$stream%3C/name%3E%3C/stream%3E#end%3C/kinesisStreams%3E\")\n" }, "statusCode": "200" }
```
    [Creating an API](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-create-api.html) 
    """

    tlsConfig = "tlsConfig"
    """
    Specifies the TLS configuration for an integration.


    """



class stage_output(str, Enum):
    """
    Creates a new Stage resource that references a pre-existing Deployment for the API. 


    """

    deploymentId = "deploymentId"
    """
    The identifier of the Deployment that the stage points to.


    """

    clientCertificateId = "clientCertificateId"
    """
    The identifier of a client certificate for an API stage.


    """

    stageName = "stageName"
    """
    The name of the stage is the first path segment in the Uniform Resource Identifier (URI) of a call to API Gateway. Stage names can only contain alphanumeric characters, hyphens, and underscores. Maximum length is 128 characters.


    """

    description = "description"
    """
    The stage's description.


    """

    cacheClusterEnabled = "cacheClusterEnabled"
    """
    Specifies whether a cache cluster is enabled for the stage.


    """

    cacheClusterSize = "cacheClusterSize"
    """
    The size of the cache cluster for the stage, if enabled.


    """

    cacheClusterStatus = "cacheClusterStatus"
    """
    The status of the cache cluster for the stage, if enabled.


    """

    methodSettings = "methodSettings"
    """
    A map that defines the method settings for a Stage resource. Keys (designated as `/{method_setting_key` below) are method paths defined as `{resource_path}/{http_method}` for an individual method override, or `/\*/\*` for overriding all methods in the stage. 


    """

    variables = "variables"
    """
    A map that defines the stage variables for a Stage resource. Variable names can have alphanumeric and underscore characters, and the values must match `[A-Za-z0-9-._~:/?#&=,]+`.


    """

    documentationVersion = "documentationVersion"
    """
    The version of the associated API documentation.


    """

    accessLogSettings = "accessLogSettings"
    """
    Settings for logging access in this stage.


    """

    canarySettings = "canarySettings"
    """
    Settings for the canary deployment in this stage.


    """

    tracingEnabled = "tracingEnabled"
    """
    Specifies whether active tracing with X-ray is enabled for the Stage.


    """

    webAclArn = "webAclArn"
    """
    The ARN of the WebAcl associated with the Stage.


    """

    tags = "tags"
    """
    The collection of tags. Each tag element is associated with a given resource.


    """

    createdDate = "createdDate"
    """
    The timestamp when the stage was created.


    """

    lastUpdatedDate = "lastUpdatedDate"
    """
    The timestamp when the stage last updated.


    """



class integrationresponse_output(str, Enum):
    """
    Represents a put integration.


    """

    statusCode = "statusCode"
    """
    Specifies the status code that is used to map the integration response to an existing MethodResponse.


    """

    selectionPattern = "selectionPattern"
    """
    Specifies the regular expression (regex) pattern used to choose an integration response based on the response from the back end. For example, if the success response returns nothing and the error response returns some string, you could use the `.+` regex to match error response. However, make sure that the error response does not contain any newline (`\n`) character in such cases. If the back end is an AWS Lambda function, the AWS Lambda function error header is matched. For all other HTTP and AWS back ends, the HTTP status code is matched.


    """

    responseParameters = "responseParameters"
    """
    A key-value map specifying response parameters that are passed to the method response from the back end. The key is a method response header parameter name and the mapped value is an integration response header value, a static value enclosed within a pair of single quotes, or a JSON expression from the integration response body. The mapping key must match the pattern of `method.response.header.{name}`, where `name` is a valid and unique header name. The mapped non-static value must match the pattern of `integration.response.header.{name}` or `integration.response.body.{JSON-expression}`, where `name` is a valid and unique response header name and `JSON-expression` is a valid JSON expression without the `$` prefix.


    """

    responseTemplates = "responseTemplates"
    """
    Specifies the templates used to transform the integration response body. Response templates are represented as a key/value map, with a content-type as the key and a template as the value.


    """

    contentHandling = "contentHandling"
    """
    Specifies how to handle response payload content type conversions. Supported values are `CONVERT_TO_BINARY` and `CONVERT_TO_TEXT`, with the following behaviors:

 * `CONVERT_TO_BINARY`: Converts a response payload from a Base64-encoded string to the corresponding binary blob.


* `CONVERT_TO_TEXT`: Converts a response payload from a binary blob to a Base64-encoded string.



 If this property is not defined, the response payload will be passed through from the integration response to the method response without modification.


    """



class method_output(str, Enum):
    """
    Add a method to an existing Resource resource.


    """

    httpMethod = "httpMethod"
    """
    The method's HTTP verb.


    """

    authorizationType = "authorizationType"
    """
    The method's authorization type. Valid values are `NONE` for open access, `AWS_IAM` for using AWS IAM permissions, `CUSTOM` for using a custom authorizer, or `COGNITO_USER_POOLS` for using a Cognito user pool.


    """

    authorizerId = "authorizerId"
    """
    The identifier of an Authorizer to use on this method. The `authorizationType` must be `CUSTOM`.


    """

    apiKeyRequired = "apiKeyRequired"
    """
    A boolean flag specifying whether a valid ApiKey is required to invoke this method.


    """

    requestValidatorId = "requestValidatorId"
    """
    The identifier of a RequestValidator for request validation.


    """

    operationName = "operationName"
    """
    A human-friendly operation identifier for the method. For example, you can assign the `operationName` of `ListPets` for the `GET /pets` method in the `PetStore` example.


    """

    requestParameters = "requestParameters"
    """
    A key-value map defining required or optional method request parameters that can be accepted by API Gateway. A key is a method request parameter name matching the pattern of `method.request.{location}.{name}`, where `location` is `querystring`, `path`, or `header` and `name` is a valid and unique parameter name. The value associated with the key is a Boolean flag indicating whether the parameter is required (`true`) or optional (`false`). The method request parameter names defined here are available in Integration to be mapped to integration request parameters or templates.


    """

    requestModels = "requestModels"
    """
    A key-value map specifying data schemas, represented by Model resources, (as the mapped value) of the request payloads of given content types (as the mapping key).


    """

    methodResponses = "methodResponses"
    """
    Gets a method response associated with a given HTTP status code. 

  The collection of method responses are encapsulated in a key-value map, where the key is a response's HTTP status code and the value is a MethodResponse resource that specifies the response returned to the caller from the back end through the integration response.

 #### Example: Get a 200 OK response of a GET method

 ##### Request

  
```
GET /restapis/uojnr9hd57/resources/0cjtch/methods/GET/responses/200 HTTP/1.1 Content-Type: application/json Host: apigateway.us-east-1.amazonaws.com Content-Length: 117 X-Amz-Date: 20160613T215008Z Authorization: AWS4-HMAC-SHA256 Credential={access_key_ID}/20160613/us-east-1/apigateway/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature={sig4_hash}
```
 ##### Response

 The successful response returns a `200 OK` status code and a payload similar to the following:

 
```
{ "_links": { "curies": { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-method-response-{rel}.html", "name": "methodresponse", "templated": true }, "self": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/responses/200", "title": "200" }, "methodresponse:delete": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/responses/200" }, "methodresponse:update": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/responses/200" } }, "responseModels": { "application/json": "Empty" }, "responseParameters": { "method.response.header.operator": false, "method.response.header.operand_2": false, "method.response.header.operand_1": false }, "statusCode": "200" }
```
    [AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/apigateway/get-method-response.html) 
    """

    methodIntegration = "methodIntegration"
    """
    Gets the method's integration responsible for passing the client-submitted request to the back end and performing necessary transformations to make the request compliant with the back end.

   #### Example:

 ##### Request

  
```
GET /restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration HTTP/1.1 Content-Type: application/json Host: apigateway.us-east-1.amazonaws.com Content-Length: 117 X-Amz-Date: 20160613T213210Z Authorization: AWS4-HMAC-SHA256 Credential={access_key_ID}/20160613/us-east-1/apigateway/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature={sig4_hash}
```
 ##### Response

 The successful response returns a `200 OK` status code and a payload similar to the following:

 
```
{ "_links": { "curies": [ { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-integration-{rel}.html", "name": "integration", "templated": true }, { "href": "https://docs.aws.amazon.com/apigateway/latest/developerguide/restapi-integration-response-{rel}.html", "name": "integrationresponse", "templated": true } ], "self": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration" }, "integration:delete": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration" }, "integration:responses": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration/responses/200", "name": "200", "title": "200" }, "integration:update": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration" }, "integrationresponse:put": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration/responses/{status_code}", "templated": true } }, "cacheKeyParameters": [], "cacheNamespace": "0cjtch", "credentials": "arn:aws:iam::123456789012:role/apigAwsProxyRole", "httpMethod": "POST", "passthroughBehavior": "WHEN_NO_MATCH", "requestTemplates": { "application/json": "{\n \"a\": \"$input.params('operand1')\",\n \"b\": \"$input.params('operand2')\", \n \"op\": \"$input.params('operator')\" \n}" }, "type": "AWS", "uri": "arn:aws:apigateway:us-west-2:lambda:path//2015-03-31/functions/arn:aws:lambda:us-west-2:123456789012:function:Calc/invocations", "_embedded": { "integration:responses": { "_links": { "self": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration/responses/200", "name": "200", "title": "200" }, "integrationresponse:delete": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration/responses/200" }, "integrationresponse:update": { "href": "/restapis/uojnr9hd57/resources/0cjtch/methods/GET/integration/responses/200" } }, "responseParameters": { "method.response.header.operator": "integration.response.body.op", "method.response.header.operand_2": "integration.response.body.b", "method.response.header.operand_1": "integration.response.body.a" }, "responseTemplates": { "application/json": "#set($res = $input.path('$'))\n{\n \"result\": \"$res.a, $res.b, $res.op => $res.c\",\n \"a\" : \"$res.a\",\n \"b\" : \"$res.b\",\n \"op\" : \"$res.op\",\n \"c\" : \"$res.c\"\n}" }, "selectionPattern": "", "statusCode": "200" } } }
```
    [AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/apigateway/get-integration.html) 
    """

    authorizationScopes = "authorizationScopes"
    """
    A list of authorization scopes configured on the method. The scopes are used with a `COGNITO_USER_POOLS` authorizer to authorize the method invocation. The authorization works by matching the method scopes against the scopes parsed from the access token in the incoming request. The method invocation is authorized if any method scopes matches a claimed scope in the access token. Otherwise, the invocation is not authorized. When the method scope is configured, the client must provide an access token instead of an identity token for authorization purposes.


    """



class methodresponse_output(str, Enum):
    """
    Adds a MethodResponse to an existing Method resource.


    """

    statusCode = "statusCode"
    """
    The method response's status code.


    """

    responseParameters = "responseParameters"
    """
    A key-value map specifying required or optional response parameters that API Gateway can send back to the caller. A key defines a method response header and the value specifies whether the associated method response header is required or not. The expression of the key must match the pattern `method.response.header.{name}`, where `name` is a valid and unique header name. API Gateway passes certain integration response data to the method response headers specified here according to the mapping you prescribe in the API's IntegrationResponse. The integration response data that can be mapped include an integration response header expressed in `integration.response.header.{name}`, a static value enclosed within a pair of single quotes (e.g., `'application/json'`), or a JSON expression from the back-end response payload in the form of `integration.response.body.{JSON-expression}`, where `JSON-expression` is a valid JSON expression without the `$` prefix.)


    """

    responseModels = "responseModels"
    """
    Specifies the Model resources used for the response's content-type. Response models are represented as a key/value map, with a content-type as the key and a Model name as the value.


    """



class deployment_output(str, Enum):
    """
    Creates a Deployment resource, which makes a specified RestApi callable over the internet.


    """

    id = "id"
    """
    The identifier for the deployment resource.


    """

    description = "description"
    """
    The description for the deployment resource.


    """

    createdDate = "createdDate"
    """
    The date and time that the deployment resource was created.


    """

    apiSummary = "apiSummary"
    """
    A summary of the RestApi at the date and time that the deployment resource was created.


    """



class restapi_model(Rendered_Resource):
    """

    Deletes the specified API.
    
    """


    name: Union[str, Cloud_Output]
    """
    A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
    """


    description: Optional[Union[str, Cloud_Output]]
    """
    A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
    """


    version: Optional[Union[str, Cloud_Output]]
    """
    A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
    """


    cloneFrom: Optional[Union[str, Cloud_Output]]
    """
    A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
    """


    binaryMediaTypes: Optional[Union[List[str], Cloud_Output]]
    """
    The ID of the RestApi that you want to clone from.
    """


    minimumCompressionSize: Optional[Union[int, Cloud_Output]]
    """
    A nullable integer that is used to enable compression (with non-negative between 0 and 10485760 (10M) bytes, inclusive) or disable compression (with a null value) on an API. When compression is enabled, compression or decompression is not applied on the payload if the payload size is smaller than this value. Setting it to zero allows compression for any payload size.
    """


    apiKeySource: Optional[Union[ApiKeySourceType, Cloud_Output]] 
    """
    The source of the API key for metering requests according to a usage plan. Valid values are: * `HEADER` to read the API key from the `X-API-Key` header of a request.
* `AUTHORIZER` to read the API key from the `UsageIdentifierKey` from a custom authorizer.
    """


    endpointConfiguration: Optional[Union[EndpointConfiguration, Cloud_Output]] 
    """
    The endpoint configuration of this RestApi showing the endpoint types of the API.
    """


    policy: Optional[Union[str, Cloud_Output]]
    """
    A stringified JSON policy document that applies to this RestApi regardless of the caller and Method configuration.
    """


    tags: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    The key-value map of strings. The valid character set is [a-zA-Z+-=.\_:/]. The tag key can be up to 128 characters and must not start with `aws:`. The tag value can be up to 256 characters.
    """


    disableExecuteApiEndpoint: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether clients can invoke your API by using the default `execute-api` endpoint. By default, clients can invoke your API with the default https://{api\_id}.execute-api.{region}.amazonaws.com endpoint. To require that clients use a custom domain name to invoke your API, disable the default endpoint.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['name', 'description', 'version', 'cloneFrom', 'binaryMediaTypes', 'minimumCompressionSize', 'apiKeySource', 'endpointConfiguration', 'policy', 'tags', 'disableExecuteApiEndpoint'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set([('restApiId', 'id')])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class resource_model(Rendered_Resource):
    """

    Deletes a Resource resource.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    The last path segment for this resource.
    """


    parentId: Union[str, Cloud_Output]
    """
    The last path segment for this resource.
    """


    pathPart: Union[str, Cloud_Output]
    """
    The last path segment for this resource.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'parentId', 'pathPart'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', ('resourceId', 'id')])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class integration_model(Rendered_Resource):
    """

    Represents an update integration.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    resourceId: Union[str, Cloud_Output]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    httpMethod: Union[str, Cloud_Output]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    type: Union[IntegrationType, Cloud_Output] 
    """
    [Required] Specifies a put integration input's type.
    """


    integrationHttpMethod: Optional[Union[str, Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    uri: Optional[Union[str, Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    connectionType: Optional[Union[ConnectionType, Cloud_Output]] 
    """
    The type of the network connection to the integration endpoint. The valid value is `INTERNET` for connections through the public routable internet or `VPC_LINK` for private connections between API Gateway and a network load balancer in a VPC. The default value is `INTERNET`.
    """


    connectionId: Optional[Union[str, Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    credentials: Optional[Union[str, Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    requestParameters: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A key-value map specifying request parameters that are passed from the method request to the back end. The key is an integration request parameter name and the associated value is a method request parameter value or static value that must be enclosed within single quotes and pre-encoded as required by the back end. The method request parameter value must match the pattern of `method.request.{location}.{name}`, where `location` is `querystring`, `path`, or `header` and `name` must be a valid and unique method request parameter name.
    """


    requestTemplates: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    Represents a map of Velocity templates that are applied on the request payload based on the value of the Content-Type header sent by the client. The content type value is the key in this map, and the template (as a String) is the value.
    """


    passthroughBehavior: Optional[Union[str, Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    cacheNamespace: Optional[Union[str, Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    cacheKeyParameters: Optional[Union[List[str], Cloud_Output]]
    """
    Specifies a group of related cached parameters. By default, API Gateway uses the resource ID as the `cacheNamespace`. You can specify the same `cacheNamespace` across resources to return the same cached data for requests to different resources.
    """


    contentHandling: Optional[Union[ContentHandlingStrategy, Cloud_Output]] 
    """
    Specifies how to handle request payload content type conversions. Supported values are `CONVERT_TO_BINARY` and `CONVERT_TO_TEXT`, with the following behaviors:

 * `CONVERT_TO_BINARY`: Converts a request payload from a Base64-encoded string to the corresponding binary blob.


* `CONVERT_TO_TEXT`: Converts a request payload from a binary blob to a Base64-encoded string.



 If this property is not defined, the request payload will be passed through from the method request to integration request without modification, provided that the `passthroughBehavior` is configured to support payload pass-through.
    """


    timeoutInMillis: Optional[Union[int, Cloud_Output]]
    """
    Custom timeout between 50 and 29,000 milliseconds. The default value is 29,000 milliseconds or 29 seconds.
    """


    tlsConfig: Optional[Union[TlsConfig, Cloud_Output]] 



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod', 'type', 'integrationHttpMethod', 'uri', 'connectionType', 'connectionId', 'credentials', 'requestParameters', 'requestTemplates', 'passthroughBehavior', 'cacheNamespace', 'cacheKeyParameters', 'contentHandling', 'timeoutInMillis', 'tlsConfig'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class stage_model(Rendered_Resource):
    """

    Changes information about a Stage resource.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    The version of the associated API documentation.
    """


    stageName: Union[str, Cloud_Output]
    """
    The version of the associated API documentation.
    """


    deploymentId: Union[str, Cloud_Output]
    """
    The version of the associated API documentation.
    """


    description: Optional[Union[str, Cloud_Output]]
    """
    The version of the associated API documentation.
    """


    cacheClusterEnabled: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether active tracing with X-ray is enabled for the Stage.
    """


    cacheClusterSize: Optional[Union[CacheClusterSize, Cloud_Output]] 
    """
    The stage's cache cluster size.
    """


    variables: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A map that defines the stage variables for the new Stage resource. Variable names can have alphanumeric and underscore characters, and the values must match `[A-Za-z0-9-._~:/?#&=,]+`.
    """


    documentationVersion: Optional[Union[str, Cloud_Output]]
    """
    The version of the associated API documentation.
    """


    canarySettings: Optional[Union[CanarySettings, Cloud_Output]] 
    """
    The canary deployment settings of this stage.
    """


    tracingEnabled: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether active tracing with X-ray is enabled for the Stage.
    """


    tags: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    The key-value map of strings. The valid character set is [a-zA-Z+-=.\_:/]. The tag key can be up to 128 characters and must not start with `aws:`. The tag value can be up to 256 characters.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'stageName', 'deploymentId', 'description', 'cacheClusterEnabled', 'cacheClusterSize', 'variables', 'documentationVersion', 'canarySettings', 'tracingEnabled', 'tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'stageName'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class integrationresponse_model(Rendered_Resource):
    """

    Represents an update integration response.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    Specifies the selection pattern of a put integration response.
    """


    resourceId: Union[str, Cloud_Output]
    """
    Specifies the selection pattern of a put integration response.
    """


    httpMethod: Union[str, Cloud_Output]
    """
    Specifies the selection pattern of a put integration response.
    """


    statusCode: Union[str, Cloud_Output]
    """
    [Required] Specifies the status code that is used to map the integration response to an existing MethodResponse.
    """


    selectionPattern: Optional[Union[str, Cloud_Output]]
    """
    Specifies the selection pattern of a put integration response.
    """


    responseParameters: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A key-value map specifying response parameters that are passed to the method response from the back end. The key is a method response header parameter name and the mapped value is an integration response header value, a static value enclosed within a pair of single quotes, or a JSON expression from the integration response body. The mapping key must match the pattern of `method.response.header.{name}`, where `name` is a valid and unique header name. The mapped non-static value must match the pattern of `integration.response.header.{name}` or `integration.response.body.{JSON-expression}`, where `name` must be a valid and unique response header name and `JSON-expression` a valid JSON expression without the `$` prefix.
    """


    responseTemplates: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    Specifies a put integration response's templates.
    """


    contentHandling: Optional[Union[ContentHandlingStrategy, Cloud_Output]] 
    """
    Specifies how to handle response payload content type conversions. Supported values are `CONVERT_TO_BINARY` and `CONVERT_TO_TEXT`, with the following behaviors:

 * `CONVERT_TO_BINARY`: Converts a response payload from a Base64-encoded string to the corresponding binary blob.


* `CONVERT_TO_TEXT`: Converts a response payload from a binary blob to a Base64-encoded string.



 If this property is not defined, the response payload will be passed through from the integration response to the method response without modification.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod', 'statusCode', 'selectionPattern', 'responseParameters', 'responseTemplates', 'contentHandling'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod', 'statusCode'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class method_model(Rendered_Resource):
    """

    Updates an existing Method resource.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    resourceId: Union[str, Cloud_Output]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    httpMethod: Union[str, Cloud_Output]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    authorizationType: Union[str, Cloud_Output]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    authorizerId: Optional[Union[str, Cloud_Output]]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    apiKeyRequired: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether the method required a valid ApiKey.
    """


    operationName: Optional[Union[str, Cloud_Output]]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    requestParameters: Optional[Union[Dict[str,bool], Cloud_Output]]
    """
    A key-value map defining required or optional method request parameters that can be accepted by API Gateway. A key defines a method request parameter name matching the pattern of `method.request.{location}.{name}`, where `location` is `querystring`, `path`, or `header` and `name` is a valid and unique parameter name. The value associated with the key is a Boolean flag indicating whether the parameter is required (`true`) or optional (`false`). The method request parameter names defined here are available in Integration to be mapped to integration request parameters or body-mapping templates.
    """


    requestModels: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    Specifies the Model resources used for the request's content type. Request models are represented as a key/value map, with a content type as the key and a Model name as the value.
    """


    requestValidatorId: Optional[Union[str, Cloud_Output]]
    """
    The identifier of a RequestValidator for validating the method request.
    """


    authorizationScopes: Optional[Union[List[str], Cloud_Output]]
    """
    The identifier of a RequestValidator for validating the method request.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod', 'authorizationType', 'authorizerId', 'apiKeyRequired', 'operationName', 'requestParameters', 'requestModels', 'requestValidatorId', 'authorizationScopes'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class methodresponse_model(Rendered_Resource):
    """

    Updates an existing MethodResponse resource.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    [Required] The HTTP verb of the Method resource.
    """


    resourceId: Union[str, Cloud_Output]
    """
    [Required] The HTTP verb of the Method resource.
    """


    httpMethod: Union[str, Cloud_Output]
    """
    [Required] The HTTP verb of the Method resource.
    """


    statusCode: Union[str, Cloud_Output]
    """
    [Required] The method response's status code.
    """


    responseParameters: Optional[Union[Dict[str,bool], Cloud_Output]]
    """
    A key-value map specifying required or optional response parameters that API Gateway can send back to the caller. A key defines a method response header name and the associated value is a Boolean flag indicating whether the method response parameter is required or not. The method response header names must match the pattern of `method.response.header.{name}`, where `name` is a valid and unique header name. The response parameter names defined here are available in the integration response to be mapped from an integration response header expressed in `integration.response.header.{name}`, a static value enclosed within a pair of single quotes (e.g., `'application/json'`), or a JSON expression from the back-end response payload in the form of `integration.response.body.{JSON-expression}`, where `JSON-expression` is a valid JSON expression without the `$` prefix.)
    """


    responseModels: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    Specifies the Model resources used for the response's content type. Response models are represented as a key/value map, with a content type as the key and a Model name as the value.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod', 'statusCode', 'responseParameters', 'responseModels'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'resourceId', 'httpMethod', 'statusCode'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class deployment_model(Rendered_Resource):
    """

    Changes information about a Deployment resource.
    
    """


    restApiId: Union[str, Cloud_Output]
    """
    The description for the Deployment resource to create.
    """


    stageName: Optional[Union[str, Cloud_Output]]
    """
    The description for the Deployment resource to create.
    """


    stageDescription: Optional[Union[str, Cloud_Output]]
    """
    The description for the Deployment resource to create.
    """


    description: Optional[Union[str, Cloud_Output]]
    """
    The description for the Deployment resource to create.
    """


    cacheClusterEnabled: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether active tracing with X-ray is enabled for the Stage.
    """


    cacheClusterSize: Optional[Union[CacheClusterSize, Cloud_Output]] 
    """
    Specifies the cache cluster size for the Stage resource specified in the input, if a cache cluster is enabled.
    """


    variables: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A map that defines the stage variables for the Stage resource that is associated with the new deployment. Variable names can have alphanumeric and underscore characters, and the values must match `[A-Za-z0-9-._~:/?#&=,]+`.
    """


    canarySettings: Optional[Union[DeploymentCanarySettings, Cloud_Output]] 
    """
    The input configuration for the canary deployment when the deployment is a canary release deployment.
    """


    tracingEnabled: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether active tracing with X-ray is enabled for the Stage.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', 'stageName', 'stageDescription', 'description', 'cacheClusterEnabled', 'cacheClusterSize', 'variables', 'canarySettings', 'tracingEnabled'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['restApiId', ('deploymentId', 'id')])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


