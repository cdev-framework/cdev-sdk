from enum import Enum
from typing import List
import docker
from cdev.settings import SETTINGS as CDEV_SETTINGS
import os
import sys
import platform
import json
from pkg_resources import Distribution
import re
from parsley import makeGrammar

from .utils import PackageTypes, ModulePackagingInfo, lambda_python_environments

DEPLOYMENT_PLATFORM = CDEV_SETTINGS.get("DEPLOYMENT_PLATFORM")

DEPLOYMENT_PYTHON_VERSION = CDEV_SETTINGS.get("DEPLOYMENT_PYTHON_VERSION")


def docker_available() -> bool:
    return True


CACHE_LOCATION = os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "dockercache.json")


class DockerDownloadCache:
    """
    Naive cache implentation for know which files have been downloaded.  
    """

    def __init__(self) -> None:

        if not os.path.isfile(CACHE_LOCATION):
            self._cache = {
                lambda_python_environments.py36: {},
                lambda_python_environments.py37: {},
                lambda_python_environments.py38_x86_64: {},
                lambda_python_environments.py38_arm64: {},
                lambda_python_environments.py39_x86_64: {},
                lambda_python_environments.py39_arm64: {},
                lambda_python_environments.py3_x86_64: {},
                lambda_python_environments.py3_arm64: {},
            }


        else:
            with open(CACHE_LOCATION) as fh:
                self._cache = json.load(fh)


        self._cache_dirs = {
            lambda_python_environments.py36: "py36",
            lambda_python_environments.py37: "py37",
            lambda_python_environments.py38_x86_64: "py38x8664",
            lambda_python_environments.py38_arm64: "py38arm64",
            lambda_python_environments.py39_x86_64: "py39x8664",
            lambda_python_environments.py39_arm64: "py39arm64",
            lambda_python_environments.py3_x86_64: "py3x8664",
            lambda_python_environments.py3_arm64: "py3arm64",
        }


    def find_item(self, environment: lambda_python_environments, id: str):
        raw_data = self._cache.get(environment).get(id)
        if raw_data:
            return [ModulePackagingInfo(**x) for x in raw_data]
        else:
            None


    def add_item(self, environment: lambda_python_environments, id: str, item: ModulePackagingInfo):
        self._cache[environment][id] = item

        with open(CACHE_LOCATION, "w") as fh:
            json.dump(self._cache, fh, indent=4)


    def get_packaging_dir(self, environment: lambda_python_environments):
        BASE_PACKAGING_DIR = os.path.abspath(os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), ".packages"))

        if not os.path.isdir(BASE_PACKAGING_DIR):
            os.mkdir(BASE_PACKAGING_DIR)


        FULL_DIR = os.path.join(BASE_PACKAGING_DIR, self._cache_dirs.get(environment))

        if not os.path.isdir(FULL_DIR):
            os.mkdir(FULL_DIR)
    
        return FULL_DIR


DOWNLOAD_CACHE = DockerDownloadCache()

def download_package_and_create_moduleinfo(project: Distribution, environment: lambda_python_environments, module_name: str) -> ModulePackagingInfo:
    """
    Download a project in a platform compatible way to extract a particular top level module info from the project. Note that this function implements
    a cache so that it only downloads the project the first time it ever is called for the pair (project_name, environment). This means that most calls
    to this function will not have to actually download the project.

    Args:
        project (Distribution): The distribution object that contains the metadata for the package
        environment (lambda_python_environments): Deployment environment the project needs to support
        module_name (str): The top level module from this project that we want

    Returns:
        info (ModulePackagingInfo): Object for the information on packaging this module
    """
    
    package_information = _download_package(project, environment)

    potential_modules = [x for x in package_information if x.module_name == module_name]


    if not len(potential_modules) == 1:
        raise Exception


    final_module = potential_modules[0]

    return final_module


def _download_package(project: Distribution, environment: lambda_python_environments) -> List[ModulePackagingInfo]:
    """
    Perform the actual downloading of the package and then parse out the needed information about the top level modules made available
    from the project. Uses the cache to make sure that way we only download the project when actually needed. 

    Args:
        project (Distribution): The distribution object that contains the metadata for the package
        environment (lambda_python_environments): Deployment environment the project needs to support
    
    Returns:
        info (List[ModulePackagingInfo]): ModulePackagingInfo for all the top level modules in the project
    
    """
    cache_item = DOWNLOAD_CACHE.find_item(environment, project.project_name)
    if cache_item:
        return cache_item 

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)
    
    print(f"DOWNLOADING {project} FROM DOCKER ({project.project_name})")
    client =  docker.from_env()

    client.images.pull("public.ecr.aws/lambda/python:3.8-arm64")
    
    print(f"PULLED IMAGE")

    container = client.containers.run("public.ecr.aws/lambda/python:3.8-arm64",
                        entrypoint="/var/lang/bin/pip", 
                        command=f"install {project.project_name}=={project.version} --target /tmp --no-user",
                        volumes=[f'{packaging_dir}:/tmp'],
                        detach=True,
                        user=os.getuid()
                    )
    
    for x in container.logs(stream=True):
        msg = x.decode('ascii')
        print(f"Building Package -> {msg}")

    
    info = _create_package_info(project.project_name, environment)
    
   
    
    return info

    
def _create_package_info(project_name: str,  environment: lambda_python_environments) -> List[ModulePackagingInfo]:
    """
    Creates a list of ModulePackagingInfo objects that represent the top level modules made available from this 
    package. It uses the information from the 'dist-info' that was downloaded for the projects by PIP This function 
    recursively calls itself to compute the information for dependant projects that were downloaded.

    Arg:
        project_name (str): Name of the project to create the information for
        environment (lambda_python_environments): Deployment environment the project needs to support

    Returns:
        info (List[ModulePackagingInfo]): ModulePackagingInfo objects for each of the top level modules in this project

    """

    # We check and add to the cache at this layer because we recursively call this function to compute the 
    # information about dependencies of a project. Since projects can share dependencies it saves time from recomputing 
    # this info
    cache_item = DOWNLOAD_CACHE.find_item(environment, project_name)
    if cache_item:
        return cache_item 

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)

    dist_info_dir = None

    for _,dir_names,_ in os.walk(packaging_dir):
        # We need to look through the packaging dir to find the dist-info folder for the project.
        # Note the dist-info folder is <project_name>-<version>.dist-info
        # https://www.python.org/dev/peps/pep-0376/#one-dist-info-directory-per-installed-distribution
        regex_dist_info = "(.*).dist-info"
        
        for dir_name in dir_names:
            m = re.match(regex_dist_info, dir_name)
            if not m:
                #print(f"No regex match {dir_name} -> {regex_dist_info}")
                continue

            # [<project_name>-<version>, dist-info]
            dir_name_split = m.groups()
            
            # project_name
            split_name_version = dir_name_split[0].split("-") 

            name = split_name_version[0]
            version = split_name_version[1]

            # Note that if a project contains '-' they are converted to '_' so that the above regex/string parsing works, so convert any '-'
            # into '_' when looking for the correct directory
            if name == project_name.replace("-","_"):
                dist_info_dir = os.path.join(packaging_dir, f"{name}-{version}.dist-info")
                break

        break 

    if not dist_info_dir:
        print(f"Could not find dist info for {project_name}")
        raise Exception

    if not os.path.isdir(os.path.join(packaging_dir, dist_info_dir)):
        print(f"COULD NOT FIND {os.path.join(packaging_dir, dist_info_dir)}")
        raise Exception

    

    
    # If no top level file is found then assume the only top level module is the same as the project name
    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")):
        top_level_module_names = [project_name]

    else:
        with open(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")) as fh:
            top_level_module_names = [x.strip() for x in fh.readlines()]



    tmp_flat_requirements: List[ModulePackagingInfo] = []
    tmp_tree_requirements: List[ModulePackagingInfo] = []
    rv = []

    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "METADATA")):
        # If not metadata file is found then assume no dependencies
        print(f"COULD NOT FIND {os.path.join(packaging_dir, dist_info_dir, 'METADATA')}")
        

    else:
        required_packages = set()
        current_package_version = ''
        with open(os.path.join(packaging_dir, dist_info_dir, "METADATA")) as fh:
            lines = fh.readlines()

            for line in lines:
                
                if not line:
                    break

                if line.split(":")[0] == "Version":
                    current_package_version = line.split(":")[1].strip()

                if line.split(":")[0] == "Requires-Dist":
                    # ex:
                    # Requires-Dist: pytz (>=2017.3)
                    stripped_information = line.split(":")[1].strip()
                    requirement_project_name = _parse_requirement_line(stripped_information)
                    if requirement_project_name:
                        required_packages.add(requirement_project_name)

        for required_package in required_packages:

            dependent_pkg_infos = _create_package_info(required_package, environment)
            for dependent_pkg_info in dependent_pkg_infos:
                tmp_flat_requirements.extend(dependent_pkg_info.flat)
                tmp_flat_requirements.append(dependent_pkg_info)

                tmp_tree_requirements.append(dependent_pkg_info)
    

    for top_level_module_name in top_level_module_names:
        # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
        # If it can not be found as either than there is an issue
        potential_dir = os.path.join(packaging_dir, top_level_module_name)
        potential_file = os.path.join(packaging_dir, top_level_module_name +".py")


        if os.path.isdir(potential_dir):
            tmp_fp = potential_dir

        elif os.path.isfile(potential_file):
            tmp_fp = potential_file

        else:
            # TODO just continue cause things like numpy have __dummy__ in their top level pkg names but dont provide it
            continue

        info = ModulePackagingInfo(**{
            "module_name": top_level_module_name,
            "type": PackageTypes.PIP,
            "version_id": current_package_version,
            "fp": tmp_fp,
            "flat": tmp_flat_requirements,
            "tree": tmp_tree_requirements
        })

        rv.append(info)   

    # Add the information to the cache
    DOWNLOAD_CACHE.add_item(environment, project_name, [x.dict() for x in rv])

    return rv


#https://www.python.org/dev/peps/pep-0508/
grammar = """
    wsp           = ' ' | '\t'
    version_cmp   = wsp* <'<=' | '<' | '!=' | '==' | '>=' | '>' | '~=' | '==='>
    version       = wsp* <( letterOrDigit | '-' | '_' | '.' | '*' | '+' | '!' )+>
    version_one   = version_cmp:op version:v wsp* -> (op, v)
    version_many  = version_one:v1 (wsp* ',' version_one)*:v2 -> [v1] + v2
    versionspec   = ('(' version_many:v ')' ->v) | version_many
    urlspec       = '@' wsp* <URI_reference>
    marker_op     = version_cmp | (wsp* 'in') | (wsp* 'not' wsp+ 'in')
    python_str_c  = (wsp | letter | digit | '(' | ')' | '.' | '{' | '}' |
                     '-' | '_' | '*' | '#' | ':' | ';' | ',' | '/' | '?' |
                     '[' | ']' | '!' | '~' | '`' | '@' | '$' | '%' | '^' |
                     '&' | '=' | '+' | '|' | '<' | '>' )
    dquote        = '"'
    squote        = '\\''
    python_str    = (squote <(python_str_c | dquote)*>:s squote |
                     dquote <(python_str_c | squote)*>:s dquote) -> s
    env_var       = ('python_version' | 'python_full_version' |
                     'os_name' | 'sys_platform' | 'platform_release' |
                     'platform_system' | 'platform_version' |
                     'platform_machine' | 'platform_python_implementation' |
                     'implementation_name' | 'implementation_version' |
                     'extra' # ONLY when defined by a containing layer
                     ):varname -> lookup(varname)
    marker_var    = wsp* (env_var | python_str)
    marker_expr   = marker_var:l marker_op:o marker_var:r -> (o, l, r)
                  | wsp* '(' marker:m wsp* ')' -> m
    marker_and    = marker_expr:l wsp* 'and' marker_expr:r -> ('and', l, r)
                  | marker_expr:m -> m
    marker_or     = marker_and:l wsp* 'or' marker_and:r -> ('or', l, r)
                      | marker_and:m -> m
    marker        = marker_or
    quoted_marker = ';' wsp* marker
    identifier_end = letterOrDigit | (('-' | '_' | '.' )* letterOrDigit)
    identifier    = < letterOrDigit identifier_end* >
    name          = identifier
    extras_list   = identifier:i (wsp* ',' wsp* identifier)*:ids -> [i] + ids
    extras        = '[' wsp* extras_list?:e wsp* ']' -> e
    name_req      = (name:n wsp* extras?:e wsp* versionspec?:v wsp* quoted_marker?:m
                     -> (n, e or [], v or [], m))
    url_req       = (name:n wsp* extras?:e wsp* urlspec:v (wsp+ | end) quoted_marker?:m
                     -> (n, e or [], v, m))
    specification = wsp* ( url_req | name_req ):s wsp* -> s
    # The result is a tuple - name, list-of-extras,
    # list-of-version-constraints-or-a-url, marker-ast or None


    URI_reference = <URI | relative_ref>
    URI           = scheme ':' hier_part ('?' query )? ( '#' fragment)?
    hier_part     = ('//' authority path_abempty) | path_absolute | path_rootless | path_empty
    absolute_URI  = scheme ':' hier_part ( '?' query )?
    relative_ref  = relative_part ( '?' query )? ( '#' fragment )?
    relative_part = '//' authority path_abempty | path_absolute | path_noscheme | path_empty
    scheme        = letter ( letter | digit | '+' | '-' | '.')*
    authority     = ( userinfo '@' )? host ( ':' port )?
    userinfo      = ( unreserved | pct_encoded | sub_delims | ':')*
    host          = IP_literal | IPv4address | reg_name
    port          = digit*
    IP_literal    = '[' ( IPv6address | IPvFuture) ']'
    IPvFuture     = 'v' hexdig+ '.' ( unreserved | sub_delims | ':')+
    IPv6address   = (
                      ( h16 ':'){6} ls32
                      | '::' ( h16 ':'){5} ls32
                      | ( h16 )?  '::' ( h16 ':'){4} ls32
                      | ( ( h16 ':')? h16 )? '::' ( h16 ':'){3} ls32
                      | ( ( h16 ':'){0,2} h16 )? '::' ( h16 ':'){2} ls32
                      | ( ( h16 ':'){0,3} h16 )? '::' h16 ':' ls32
                      | ( ( h16 ':'){0,4} h16 )? '::' ls32
                      | ( ( h16 ':'){0,5} h16 )? '::' h16
                      | ( ( h16 ':'){0,6} h16 )? '::' )
    h16           = hexdig{1,4}
    ls32          = ( h16 ':' h16) | IPv4address
    IPv4address   = dec_octet '.' dec_octet '.' dec_octet '.' dec_octet
    nz            = ~'0' digit
    dec_octet     = (
                      digit # 0-9
                      | nz digit # 10-99
                      | '1' digit{2} # 100-199
                      | '2' ('0' | '1' | '2' | '3' | '4') digit # 200-249
                      | '25' ('0' | '1' | '2' | '3' | '4' | '5') )# %250-255
    reg_name = ( unreserved | pct_encoded | sub_delims)*
    path = (
            path_abempty # begins with '/' or is empty
            | path_absolute # begins with '/' but not '//'
            | path_noscheme # begins with a non-colon segment
            | path_rootless # begins with a segment
            | path_empty ) # zero characters
    path_abempty  = ( '/' segment)*
    path_absolute = '/' ( segment_nz ( '/' segment)* )?
    path_noscheme = segment_nz_nc ( '/' segment)*
    path_rootless = segment_nz ( '/' segment)*
    path_empty    = pchar{0}
    segment       = pchar*
    segment_nz    = pchar+
    segment_nz_nc = ( unreserved | pct_encoded | sub_delims | '@')+
                    # non-zero-length segment without any colon ':'
    pchar         = unreserved | pct_encoded | sub_delims | ':' | '@'
    query         = ( pchar | '/' | '?')*
    fragment      = ( pchar | '/' | '?')*
    pct_encoded   = '%' hexdig
    unreserved    = letter | digit | '-' | '.' | '_' | '~'
    reserved      = gen_delims | sub_delims
    gen_delims    = ':' | '/' | '?' | '#' | '(' | ')?' | '@'
    sub_delims    = '!' | '$' | '&' | '\\'' | '(' | ')' | '*' | '+' | ',' | ';' | '='
    hexdig        = digit | 'a' | 'A' | 'b' | 'B' | 'c' | 'C' | 'd' | 'D' | 'e' | 'E' | 'f' | 'F'
"""


def format_full_version(info):
    version = '{0.major}.{0.minor}.{0.micro}'.format(info)
    kind = info.releaselevel
    if kind != 'final':
        version += kind[0] + str(info.serial)
    return version

if hasattr(sys, 'implementation'):
    implementation_version = format_full_version(sys.implementation.version)
    implementation_name = sys.implementation.name
else:
    implementation_version = '0'
    implementation_name = ''
# TODO override these bindings to produce the data for the deployment environment
bindings = {
    'implementation_name': implementation_name,
    'implementation_version': implementation_version,
    'os_name': os.name,
    'platform_machine': platform.machine(),
    'platform_python_implementation': platform.python_implementation(),
    'platform_release': platform.release(),
    'platform_system': platform.system(),
    'platform_version': platform.version(),
    'python_full_version': platform.python_version(),
    'python_version': '.'.join(platform.python_version_tuple()[:2]),
    'sys_platform': sys.platform,
}

compiled = makeGrammar(grammar, {'lookup': bindings.__getitem__})
def _parse_requirement_line(line: str) -> str:
    """
    From a dist-require line parse out the name of the need project.  
    """
    # All this code is directly lifted from PEP 508 which is the specification of this line.
    # https://www.python.org/dev/peps/pep-0508/
    try:
        parsed_info = compiled(line).specification()

        return parsed_info[0]

    except Exception:
        return None
