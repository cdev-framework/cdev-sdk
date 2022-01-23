from enum import Enum
from typing import FrozenSet, List, NamedTuple, Tuple, NewType, overload, Optional, Union, Iterable, Mapping
from typing_extensions import Literal, SupportsIndex
from collections.abc import Sequence


from core.utils.types import ImmutableModel, frozendict

CLOUD_OUTPUT_ID = 'cdev_cloud_output'


class OutputType(str, Enum):
    RESOURCE = 'resource'
    REFERENCE = 'reference'


output_operation = NewType('output_operation', Tuple[str, Tuple, frozendict])


class cloud_output_model(ImmutableModel):
    """
    Often we want resources that depend on the value of output of other resources that is only known after a cloud resource is created. This serves
    as a placeholder for that desired value until it is available.
    """

    name: str
    """
    Name of the resource
    """

    ruuid: str
    """
    Ruuid of the resource
    """

    key: str
    """
    The key to lookup the output value by (ex: arn)
    """

    type: OutputType


    id: Literal['cdev_cloud_output']



class cloud_output_dynamic_model(cloud_output_model):
    output_operations: Tuple[output_operation,...]


class Cloud_Output():
    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        self._name = name
        self._ruuid = ruuid
        self._key = key
        self._type = type


    def render(self) -> cloud_output_dynamic_model:
        return cloud_output_model(
            name=self._name,
            ruuid=self._ruuid,
            key=self._key,
            type=self._type,
            id='cdev_cloud_output',
        )


class Cloud_Output_Dynamic(Cloud_Output):
    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        super().__init__(name, ruuid, key, type)
        self._operations: List[output_operation] = []


    def render(self) -> cloud_output_dynamic_model:
        operations = tuple([(x[0], tuple(x[1]), frozendict(x[2])) for x in self._operations])

        return cloud_output_dynamic_model(
            name=self._name,
            ruuid=self._ruuid,
            key=self._key,
            type=self._type,
            id='cdev_cloud_output',
            output_operations=operations
        )


class Cloud_Output_Str(Sequence, Cloud_Output_Dynamic,):

    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        super().__init__(name, ruuid, key, type)

    def __iter__(self):
        print(f'iter')

    def __len__(self):
        raise Exception

    @overload
    def __getitem__(self, idx: int):
        print(f'indx get item {idx}')

    @overload
    def __getitem__(self, s: slice):
        print(f'slice get item {s}')


    def __getitem__(self, key):
        print(f"{key}")
        self._operations.append(('__getitem__',[],{}))

    
    def capitalize(self) -> 'Cloud_Output_Str':
        """Make the first character have upper case and the rest lower case.

        Append the operation to the Cloud Output Object and return the same Object for 
        any further operations.

        """
        self._operations.append(('capitalize', (), {}))
        return self

    def casefold(self, ) -> 'Cloud_Output_Str':
        """Make S suitable for caseless comparisons.

        Append the operation to the Cloud Output Object and return the same Object for 
        any further operations.
        
        """
        self._operations.append(('casefold', (), {}))
        return self

    s = ""

    def center(self, __width: SupportsIndex, __fillchar: str = ...) -> 'Cloud_Output_Str':
        """S centered in a string of length width. Padding is done using the specified fill character (default is a space)

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(('center', (__width), {'__fillchar': __fillchar}))
        return self

    def count(self, x: str, __start: Union[SupportsIndex, None] = ..., __end: Union[SupportsIndex, None] = ...) -> int:
        """The number of non-overlapping occurrences of substring sub in string S[start:end].
        
        Returns a Cloud Output Int on which further operations can be chained. The created Cloud Output Int
        will contain all previous operations of the current Cloud Output String that this is being called on.

        Optional arguments start and end are interpreted as in slice notation.
        """
        self._operations.append(
            (
                'count', 
                (), 
                {
                    '__start': __start,
                    '__end': __end
                }
            )
        )

    def endswith(
        self, 
        __suffix: Union[str, Tuple[str, ...]],
        __start: Union[SupportsIndex, None] = ..., 
        __end: Union[SupportsIndex,None] = ...) -> bool:
        """Return True if S ends with the specified suffix, False otherwise.
        
        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        suffix can also be a tuple of strings to try.
        """
        self._operations.append(
            (
                'endswith', 
                (),
                {
                    "__suffix": __suffix,
                    "__start": __start,
                    "__end    ": __end,
                }
            )
        )

    def expandtabs(self, tabsize=8) -> 'Cloud_Output_Str':
        """Return a copy of S where all tab characters are expanded using spaces.
        
        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        
        If tabsize is not given, a tab size of 8 characters is assumed.
        """
        self._operations.append(
            (
                'expandtabs', 
                (), 
                {
                    'tabsize': tabsize
                }
            )
        )
        return self

    def find(self, __sub: str, __start: Union[SupportsIndex, None] = ..., __end: Union[SupportsIndex,None] = ...) -> int:
        """
        Return the lowest index in S where substring sub is found,
        such that sub is contained within S[start:end].  
        
        Returns a Cloud Output Int on which further operations can be chained. The created Cloud Output Int
        will contain all previous operations of the current Cloud Output String that this is being called on.

        Optional arguments start and end are interpreted as in slice notation.
        """
        self._operations.append(
            (
                'find', 
                (), 
                {
                    "__sub": __sub,
                    "__start": __start,
                    "__end": __end,
                }
            )
        )

    def format(self, *args, **kwargs) -> 'Cloud_Output_Str':
        """Format S, using substitutions from args and kwargs.
        The substitutions are identified by braces ('{' and '}').
        
        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'format', 
                args, 
                kwargs
            )
        )
        return self

    def format_map(self, mapping) -> 'Cloud_Output_Str':
        """Format S, using substitutions from mapping.
        The substitutions are identified by braces ('{' and '}').

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'format_map', 
                (), 
                {
                    'mapping': mapping
                }
            )
        )
        return self

    def index(self, _sub: str, __start: Union[SupportsIndex,None] = ..., __end: Union[SupportsIndex,None] = ...) -> int:
        """Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].  

        Returns a Cloud Output Int on which further operations can be chained. The created Cloud Output Int
        will contain all previous operations of the current Cloud Output String that this is being called on.
        
        Optional arguments start and end are interpreted as in slice notation.

        Raises ValueError when the substring is not found.
        """
        self._operations.append(
            (
                'index', 
                (), 
                {
                    "_sub": _sub,
                    "__start": __start,
                    "__end": __end,
                }
            )
        )

    def isalnum(self) -> bool:
        """Return True if all characters in S are alphanumeric and there is at least one character in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isalnum', (), {}))


    def isalpha(self, ) -> bool:
        """Return True if all characters in S are alphabetic and there is at least one character in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isalpha', (), {}))

    def isdecimal(self, ) -> bool:
        """
        Return True if there are only decimal characters in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isdecimal', (), {}))

    def isdigit(self, ) -> bool:
        """
        Return True if all characters in S are digits and there is at least one character in S, False otherwise.
        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isdigit', (), {}))

    def isidentifier(self, ) -> bool:
        """
        Return True if S is a valid identifier according to the language definition.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.

        Use keyword.iskeyword() to test for reserved identifiers
        such as "def" and "class".

        """
        self._operations.append(('isidentifier', (), {}))

    def islower(self, ) -> bool:
        """
        Return True if all cased characters in S are lowercase and there is at least one cased character in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('islower', (), {}))

    def isnumeric(self, ) -> bool:
        """
        Return True if there are only numeric characters in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isnumeric', (), {}))

    def isprintable(self, ) -> bool:
        """
        Return True if all characters in S are considered printable in repr() or S is empty, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isprintable', (), {}))

    def isspace(self, ) -> bool:
        """
        Return True if all characters in S are whitespace and there is at least one character in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isspace', (), {}))

    def istitle(self, ) -> bool:
        """
        Return True if S is a titlecased string and there is at least one
        character in S, i.e. upper- and titlecase characters may only
        follow uncased characters and lowercase characters only cased ones.
        Return False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('istitle', (), {}))

    def isupper(self, ) -> bool:
        """
        Return True if all cased characters in S are uppercase and there is
        at least one cased character in S, False otherwise.

        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        """
        self._operations.append(('isupper', (), {}))

    s.join
    def join(self, _iterable: Iterable[str]) -> 'Cloud_Output_Str':
        """
        Return a string which is the concatenation of the strings in the

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'join',
                (), 
                {
                    "_iterable": _iterable
                }
            )
        )
        return self

    def ljust(self, __width: SupportsIndex, __fillchar: str = ...) -> 'Cloud_Output_Str':
        """
        Return S left-justified in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space).

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'ljust',
                (),
                {
                    '__width': __width,
                    '__fillchar': __fillchar
                }
            )
        )
        return self

    def lower(self) -> 'Cloud_Output_Str':
        """
        Return a copy of the string S converted to lowercase.

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'lower',
                (),
                {}
            )
        )
        return self

    def lstrip(self, __chars: Union[str, None] = ...) -> 'Cloud_Output_Str':
        """
        Return a copy of the string S with leading whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        """
        self._operations.append(
            (
                'lstrip', 
                (), 
                {
                    "__chars":__chars
                }
            )
        )

    #def partition(self, __sep: str) -> (head, sep, tail):
    #    """
    #    Search for the separator sep in S, and return the part before it,
    #    the separator itself, and the part after it.  If the separator is not
    #    found, return S and two empty strings.
    #    """
    #    self._operations.append(('partition', (), {}))

    s.replace()
    def replace(self, __old: str, __new: str, __count: SupportsIndex = ...) -> 'Cloud_Output_Str':
        """Change all occurrences of substring old replaced by new. 
        
        If the optional argument count is given, only the first count occurrences are replaced.
        """
        self._operations.append(
            (
                'replace',
                (),
                {
                    "__old": __old,
                    "__new": __new,
                    "__count": __count
                }
            )
        )

    s.rfind
    def rfind(self, __sub: str, __start: Union[SupportsIndex, None] = ..., __end: Union[SupportsIndex, None] = ...) -> int:
        """Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].  
        
        Returns a Cloud Output Int on which further operations can be chained. The created Cloud Output Int
        will contain all previous operations of the current Cloud Output String that this is being called on.

        Optional arguments start and end are interpreted as in slice notation.

        Return -1 on failure.
        """
        self._operations.append(
            (
                'rfind',
                (),
                {
                    "__sub": __sub,
                    "__start": __start,
                    "__end": __end,   
                }
            )
        )

    s.rin
    def rindex(self, __sub: str, __start: Union[SupportsIndex, None] = ..., __end: Union[SupportsIndex, None] = ...) -> int:
        """Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].  
        
        Returns a Cloud Output Int on which further operations can be chained. The created Cloud Output Int
        will contain all previous operations of the current Cloud Output String that this is being called on.

        Optional arguments start and end are interpreted as in slice notation.

        Raises ValueError when the substring is not found.
        """
        self._operations.append(
            (
                'rindex',
                (),
                {
                    "__sub": __sub,
                    "__start": __start,
                    "__end": __end,   
                }
            )
        )

    def rjust(self, __width: SupportsIndex, __fillchar: str = ...) -> 'Cloud_Output_Str':
        """Right-justify S in a string of length width. Padding is
        done using the specified fill character (default is a space).

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'rjust',
                (),
                {
                    "__width": __width,
                    "__fillchar": __fillchar
                }
            )
        )

    #def rpartition(self, sep) -> (head, sep, tail):
    #    """
    #    Search for the separator sep in S, starting at the end of S, and return
    #    the part before it, the separator itself, and the part after it.  If the
    #    """
    #    self._operations.append(('rpartition', (), {}))

    def rsplit(self, sep: Union[str, None] = ..., maxsplit: SupportsIndex = ...) -> List['Cloud_Output_Str']:
        """Return a list of the words in S, using sep as the
        delimiter string, starting at the end of the string and
        working to the front.  

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        
        If maxsplit is given, at most maxsplit splits are done. 
        
        If sep is not specified, any whitespace string is a separator.
        """
        self._operations.append(
            (
                'rsplit',
                (),
                {
                    "sep": sep,
                    "maxsplit": maxsplit
                }
            )
        )
        return self

    
    def rstrip(self, __chars: Optional[str] = ...)  -> 'Cloud_Output_Str':
        """Return S with trailing whitespace removed.
        
        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        
        If chars is given and not None, remove characters in chars instead.
        """
        self._operations.append(
            (
                'rstrip',
                (), 
                {
                    "__chars": __chars
                }
            )
        )

    def split(self, sep=None, maxsplit=-1) -> List['Cloud_Output_Str']:
        """Return a list of the words in S, using sep as the delimiter string.  

        ## TODO Sequence type
        
        If maxsplit is given, at most maxsplit splits are done.
        
        If sep is not specified or is None, any whitespace string is a separator and empty strings are
        removed from the result.
        """
        self._operations.append(
            (
                'split', 
                (),
                {
                    "sep": sep,
                    "maxsplit": maxsplit
                }
            )
        )

    def splitlines(self, keepends: bool = ...) -> List['Cloud_Output_Str']:
        """
        Return a list of the lines in S, breaking at line boundaries.

        ## TODO Sequence type
        
        Line breaks are not included in the resulting list unless keepends is given and true.
        """
        self._operations.append(
            (
                'splitlines', 
                (), 
                {
                    "keepends": keepends
                }
            )
        )

    def startswith(
        self, 
        __prefix: Union[str, Tuple[str, ...]], 
        __start: Optional[SupportsIndex] = ..., 
        __end: Optional[SupportsIndex] = ...) -> bool:
        """Return True if S starts with the specified prefix, False otherwise.
        
        Returns a Cloud Output Boolean on which further operations can be chained. The created Cloud Output Boolean
        will contain all previous operations of the current Cloud Output String that this is being called on.
        
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        prefix can also be a tuple of strings to try.
        """
        self._operations.append(
            (
                'startswith', 
                (), 
                {
                    "__prefix": __prefix,
                    "__start": __start,
                    "__end": __end,
                }
            )
        )

    def strip(self, __chars: Optional[str] = ...)  -> 'Cloud_Output_Str':
        """S with leading and trailing whitespace removed.
        
        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        
        If chars is given and not None, remove characters in chars instead.
        """
        self._operations.append(
            (
                'strip',
                (),
                {
                    "__chars": __chars
                }
            )
        )
        return self

    def swapcase(self) -> 'Cloud_Output_Str':
        """S with uppercase characters converted to lowercase and vice versa.

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'swapcase', 
                (), 
                {}
            )
        )

        return self


    def title(self) -> 'Cloud_Output_Str':
        """Titlecased version of S

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        
        i.e. words start with title case characters, all remaining cased characters have lower case.
        """
        self._operations.append(
            (
                'title',
                (),
                {}
            )
        )
        return self

    def translate(
        self,
        __table: Mapping[
                int, 
                Union[ 
                    Union[int ,str,None], 
                    Sequence[ Union[int, str, None] ] 
                ]
            ]
        ) -> 'Cloud_Output_Str':
        """S in which each character has been mapped through the given translation table. 
        
        The table must implement
        lookup/indexing via __getitem__, for instance a dictionary or list,
        mapping Unicode ordinals to Unicode ordinals, strings, or None. If
        this operation raises LookupError, the character is left untouched.
        Characters mapped to None are deleted.
        """
        self._operations.append(
            (
                'translate', 
                (),
                {
                    "__table": __table
                }
            )
        )

    def upper(self, ) -> 'Cloud_Output_Str':
        """
        Return a copy of S converted to uppercase.

        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        """
        self._operations.append(
            (
                'upper', 
                (), 
                {}
            )
        )

        return self

    s.zfi
    def zfill(self, __width: SupportsIndex) -> 'Cloud_Output_Str':
        """Pad a numeric string S with zeros on the left, to fill a field of the specified width. 
        
        Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
        
        The string S is never truncated.
        """
        self._operations.append(
            (
                'zfill', 
                (), 
                {
                    "__width": __width
                }
            )
        )
