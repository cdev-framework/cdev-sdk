import os
from typing import Dict, List, Optional, Set

from pydantic.types import FilePath
from pydantic import BaseModel, DirectoryPath
from enum import Enum
from pathlib import PosixPath, WindowsPath

from core.utils import paths as core_paths, hasher as cdev_hasher
from core.utils.logger import log
from core.utils.platforms import lambda_python_environment

import sys
from parsley import makeGrammar

from rich import print



def get_lines_from_file_list(file_list, function_info) -> List[str]:
    # Get the list of lines from a file based on the function info provided
    line_nos = _compress_lines(function_info)

    actual_lines = []

    for i in line_nos:
        if i == -1:
            actual_lines.append(os.linesep)
        elif i <= len(file_list):
            actual_lines.append(file_list[i - 1])

    return actual_lines


def get_file_as_list(path):
    # Returns the file as a list of lines
    if not os.path.isfile:
        return None

    with open(path) as fh:
        rv = fh.read().splitlines()

    return rv


def _compress_lines(original_lines):
    # Takes input SORTED([(l1,l2), (l3,l4), ...])
    # returns [l1,...,l2,l3,...,l4]
    rv = []

    for pair in original_lines:
        for i in range(pair[0], pair[1] + 1):
            if rv and rv[-1] == i:
                # if the last element already equals the current value continue... helps eleminate touching boundaries
                continue

            rv.append(i)

        if sys.version_info > (3, 8):
            rv.append(-1)

    return rv


def get_parsed_path(original_path, function_name, final_base_directory: DirectoryPath, prefix=None):
    split_path = core_paths.get_relative_to_workspace_path(original_path).split("/")
    
    # the last item in the path is .py file name... change the  .py to _py so it works as a dir
    final_file_name = split_path[-1].split(".")[0] + "_" + function_name + ".py"
    
    try:
        split_path.remove(".")
        split_path.remove("..")
    except Exception as e:
        pass

    if prefix:
        split_path.insert(0, prefix)

    final_file_dir = core_paths.create_path(final_base_directory, split_path[:-1])


    log.debug("Created Parsed Path is %s", os.path.join(final_file_dir, final_file_name) )
    return os.path.join(final_file_dir, final_file_name)


class ExternalDependencyWriteInfo(BaseModel):
    location: str
    id: str

    class Config:
        json_encoders = {
            PosixPath: lambda v: v.as_posix(),  # or lambda v: str(v)
            WindowsPath: lambda v: v.as_posix(),
        }

        extra = "ignore"

    def __hash__(self) -> int:
        return int(cdev_hasher.hash_string(self.id), base=16)


class PackageTypes(str, Enum):
    BUILTIN = "builtin"
    STANDARDLIB = "standardlib"
    PIP = "pip"
    LOCALPACKAGE = "localpackage"
    AWSINCLUDED = "awsincluded"

class Architecture(str, Enum):
    X86 = "x86_64"
    ARM64 = "aarch64"
    ANY = "any"



class ModulePackagingInfo(BaseModel):
    module_name: str
    type: PackageTypes
    version_id: Optional[str]
    arch: Optional[Architecture] = Architecture.ANY
    fp: Optional[str]
    tree: Optional[List["ModulePackagingInfo"]]
    flat: Optional[List["ModulePackagingInfo"]]
    is_relative: Optional[bool]

    def set_flat(self, flat: List["ModulePackagingInfo"]):
        self.flat = flat

    def set_tree(self, tree: List["ModulePackagingInfo"]):
        self.tree = tree

    def get_id_str(self) -> str:
        if self.type == PackageTypes.LOCALPACKAGE:
            if os.path.isfile(self.fp):
                return f"{self.module_name}-{self.fp}-{cdev_hasher.hash_file(self.fp)}"

            else:
                return f"{self.module_name}-{self.fp}"

        elif self.type == PackageTypes.PIP:
            return f"{self.module_name}-{self.version_id}-{self.arch}"

        else:
            return self.module_name

    def __str__(self) -> str:
        return self.get_id_str()

    def __repr__(self) -> str:
        return f"{self.get_id_str()}"

    def __hash__(self) -> int:
        return int(cdev_hasher.hash_string(self.get_id_str()), base=16)


ModulePackagingInfo.update_forward_refs()


_depth_to_color = {0: "white", 1: "blue", 2: "yellow", 3: "magenta", 4: "red"}


def print_dependency_tree(
    handler_name: str, top_level_modules: List[ModulePackagingInfo]
):
    print(f"Handler: {handler_name}")

    for module_info in top_level_modules:

        _recursive_dfs_print(module_info, 0)
        print("|")


def _recursive_dfs_print(module_info: ModulePackagingInfo, depth: int):

    base_str = f"|[{_depth_to_color.get(depth%5)}]{'-' * depth } {module_info.get_id_str()}[/{_depth_to_color.get(depth%5)}] ({module_info.type})"
    print(base_str)

    if module_info.tree:
        for child_module in module_info.tree:
            _recursive_dfs_print(child_module, depth + 1)


def print_handler_package():
    pass


def print_layer_package():
    pass




environment_to_architecture_suffix: Dict[lambda_python_environment, Architecture] = {
    lambda_python_environment.py37: Architecture.X86,
    lambda_python_environment.py38_x86_64: Architecture.X86,
    lambda_python_environment.py38_arm64: Architecture.ARM64,
    lambda_python_environment.py39_x86_64: Architecture.X86,
    lambda_python_environment.py39_arm64: Architecture.ARM64,
    lambda_python_environment.py3_x86_64: Architecture.X86,
    lambda_python_environment.py3_arm64: Architecture.ARM64,
}


CONTAINER_NAMES = {
    lambda_python_environment.py37: "public.ecr.aws/lambda/python:3.7",
    lambda_python_environment.py38_x86_64: "public.ecr.aws/lambda/python:3.8-x86_64",
    lambda_python_environment.py38_arm64: "public.ecr.aws/lambda/python:3.8-arm64",
    lambda_python_environment.py39_x86_64: "public.ecr.aws/lambda/python:3.9-x86_64",
    lambda_python_environment.py39_arm64: "public.ecr.aws/lambda/python:3.9-arm64",
    lambda_python_environment.py3_x86_64: "public.ecr.aws/lambda/python:3-x86_64",
    lambda_python_environment.py3_arm64: "public.ecr.aws/lambda/python:3-arm64",
}


# https://www.python.org/dev/peps/pep-0508/
grammar = """
    wsp           = ' ' | '\t'
    version_cmp   = wsp* <'<=' | '<' | '!=' | '==' | '>=' | '>' | '~=' | '==='>
    version       = wsp* <( letterOrDigit | '-' | '_' | '.' | '*' | '+' | '!' )+>
    version_one   = version_cmp:op version:v wsp* -> (op, v)
    version_many  = version_one:v1 (wsp* ',' version_one)*:v2 -> [v1] + v2
    versionspec   = ('(' version_many:v ')' ->v) | version_many
    urlspec       = '@' wsp* <URI_reference>
    marker_op     = version_cmp | (wsp* 'in') | (wsp* 'not' wsp+ 'in') -> 'not in'
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

bindings = {
    "py6_86": {
        "implementation_name": "cpython",
        "implementation_version": "3.6.15",
        "os_name": "posix",
        "platform_machine": "x86_64",
        "platform_python_implementation": "CPython",
        "platform_release": "4.14.246-198.474.amzn2.x86_64",
        "platform_system": "Linux",
        "platform_version": "#1 SMP Wed Sep 15 00:16:00 UTC 2021",
        "python_full_version": "3.6.15",
        "python_version": "3.6",
        "sys_platform": "linux",
    },
    "py7_86": {
        "implementation_name": "cpython",
        "implementation_version": "3.7.12",
        "os_name": "posix",
        "platform_machine": "x86_64",
        "platform_python_implementation": "CPython",
        "platform_release": "4.14.246-198.474.amzn2.x86_64",
        "platform_system": "Linux",
        "platform_version": "#1 SMP Wed Sep 15 00:16:00 UTC 2021",
        "python_full_version": "3.7.12",
        "python_version": "3.7",
        "sys_platform": "linux",
    },
    "py8_arm": {
        "implementation_name": "cpython",
        "implementation_version": "3.8.11",
        "os_name": "posix",
        "platform_machine": "aarch64",
        "platform_python_implementation": "CPython",
        "platform_release": "4.14.246-198.474.amzn2.aarch64",
        "platform_system": "Linux",
        "platform_version": "#1 SMP Wed Sep 15 00:16:11 UTC 2021",
        "python_full_version": "3.8.11",
        "python_version": "3.8",
        "sys_platform": "linux",
    },
    "py8_86": {
        "implementation_name": "cpython",
        "implementation_version": "3.8.11",
        "os_name": "posix",
        "platform_machine": "x86_64",
        "platform_python_implementation": "CPython",
        "platform_release": "4.14.246-198.474.amzn2.x86_64",
        "platform_system": "Linux",
        "platform_version": "#1 SMP Wed Sep 15 00:16:00 UTC 2021",
        "python_full_version": "3.8.11",
        "python_version": "3.8",
        "sys_platform": "linux",
    },
    "py9_arm": {
        "implementation_name": "cpython",
        "implementation_version": "3.9.6",
        "os_name": "posix",
        "platform_machine": "aarch64",
        "platform_python_implementation": "CPython",
        "platform_release": "4.14.246-198.474.amzn2.aarch64",
        "platform_system": "Linux",
        "platform_version": "#1 SMP Wed Sep 15 00:16:11 UTC 2021",
        "python_full_version": "3.9.6",
        "python_version": "3.9",
        "sys_platform": "linux",
    },
    "py9_86": {
        "implementation_name": "cpython",
        "implementation_version": "3.9.6",
        "os_name": "posix",
        "platform_machine": "x86_64",
        "platform_python_implementation": "CPython",
        "platform_release": "4.14.246-198.474.amzn2.x86_64",
        "platform_system": "Linux",
        "platform_version": "#1 SMP Wed Sep 15 00:16:00 UTC 2021",
        "python_full_version": "3.9.6",
        "python_version": "3.9",
        "sys_platform": "linux",
    },
}

compiled = makeGrammar(grammar, {"lookup": bindings.get("py8_arm").__getitem__})


def parse_requirement_line(line: str) -> str:
    """
    From a dist-require line parse out the name of the need project.
    """
    # All this code is directly lifted from PEP 508 which is the specification of this line.
    # https://www.python.org/dev/peps/pep-0508/
    try:
        parsed_info = compiled(line).specification()
        
        if parsed_info[3]:
            if not evaluate_expression(parsed_info[3]):
                return None

        return parsed_info[0]

    except Exception:
        return None


OPERATORS = set(
    [
        "in",
        "==",
        "!=",
        "not in",
        "and",
        "or",
        "<=",
        "<",
        "!=",
        "==",
        ">=",
        ">",
    ]
)


def evaluate_expression(expr) -> bool:
    operator = expr[0]
    right_side = expr[1]
    left_side = expr[2]

    if operator not in OPERATORS:
        raise Exception

    if operator == "and":
        right_side_evaluated = evaluate_expression(right_side)

        if not right_side_evaluated:
            return False

        left_side_evaluated = evaluate_expression(left_side)

        return right_side_evaluated and left_side_evaluated

    elif operator == "or":
        right_side_evaluated = evaluate_expression(right_side)

        if right_side_evaluated:
            return True

        left_side_evaluated = evaluate_expression(left_side)

        return right_side_evaluated or left_side_evaluated

    elif operator == "in":
        return right_side in left_side

    elif operator == "==":
        return right_side == left_side

    elif operator == "!=":
        return right_side != left_side

    elif operator == "not in":
        return not right_side in left_side

    elif operator == "<=":
        return right_side <= left_side

    elif operator == "<":
        return right_side < left_side

    elif operator == "!=":
        return right_side != left_side

    elif operator == "==":
        return right_side == left_side

    elif operator == ">=":
        return right_side >= left_side

    elif operator == ">":
        return right_side > left_side

    else:
        raise Exception
