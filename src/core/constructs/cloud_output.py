"""Structure that encapsulates the desire to capture and use output from deploying a resource on the cloud.

Often, it is required to use the returned values provided by the cloud as input into another resource. For
example, wanting to pass a created db name into the environment variables of a serverless function that will
reference it. Therefor, it is important that these values are core primitives within the framework.

The core framework has tried to make working with these types of values feel as natural as possible, but it
is important to have an understanding of how they are designed to avoid confusion. A `Cloud Output` represents
a future value that is not currently know at the execution time of the current code. They are designed to look
and feel like the `types` they will evaluate to by providing methods that mirror common methods of the evaluated
type.

For example, a `Cloud Output String` contains methods such as `replace` that mirror `replace` on a regular string.
These methods can be chained together to create more complex functionality. For a more in depth discussion on the
capabilities and limits of this system read out documentation at <link>.

"""

from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    NewType,
    overload,
    Optional,
    Union,
    Iterable,
    Mapping,
    TypeVar,
    Generic,
)
from typing_extensions import Literal, SupportsIndex
from collections.abc import Sequence

from core.constructs.models import ImmutableModel, frozendict
from core.utils import hasher

CLOUD_OUTPUT_ID = "cdev_cloud_output"

# Wrapper type to help keep annotations compact
output_operation = NewType("output_operation", Tuple[str, Tuple, frozendict])


class OutputType(str, Enum):
    """Type of Cloud Output

    Since Cloud Output can be derived from resources and references, we need to denote where the Output is coming from.
    """

    RESOURCE = "resource"
    REFERENCE = "reference"


########################
##### Immutable Models
########################
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
    """
    Type of the underlying item we want to get the output of
    """

    id: Literal["cdev_cloud_output"]
    """
    Literal that allows a dict to be identified as a Cloud Output Model
    """


class cloud_output_dynamic_model(cloud_output_model):
    """
    A cloud output model that has accompanying operations to be applied to the derived value
    """

    output_operations: Tuple[output_operation, ...]
    """
    Tuple of all the operations to be applied to the derived value
    """


def evaluate_dynamic_output(
    original_value: Any, cloud_output_dynamic: cloud_output_dynamic_model
) -> Any:
    """Evaluate a set of operations on a starting value.

    Args:
        original_value (Any): The original value to operate on
        cloud_output_dynamic (cloud_output_dynamic_model): The model containing the operations to execute

    Raises:
        Exception: [description]

    Returns:
        Any: The transformed value
    """
    operations = cloud_output_dynamic.output_operations

    intermediate_value = original_value
    for x in operations:
        func_name = x[0]
        xargs = x[1]
        kwargs = x[2]

        if func_name == "**not":
            # There is not hidden method that implements not, so we need to hard code this.
            new_rv = not intermediate_value

        elif func_name == "**and":
            new_rv = intermediate_value and xargs[0]

        elif func_name == "**or":
            new_rv = intermediate_value or xargs[0]

        elif func_name == "**xor":
            new_rv = intermediate_value ^ xargs[0]

        elif func_name == "join":
            new_rv = getattr(intermediate_value, func_name)(xargs)

        else:
            object_methods = set(
                [
                    method_name
                    for method_name in dir(str)
                    if callable(getattr(str, method_name))
                ]
            )

            if func_name not in object_methods:
                print(object_methods)
                raise Exception(
                    f"'{func_name}' not in available methods for {intermediate_value} ({type(intermediate_value)})"
                )

            if xargs and kwargs:
                new_rv = getattr(intermediate_value, func_name)(**kwargs)
            elif (not xargs) and kwargs:
                new_rv = getattr(intermediate_value, func_name)(**kwargs)
            elif xargs and (not kwargs):
                new_rv = getattr(intermediate_value, func_name)(*xargs)
            elif (not xargs) and (not kwargs):
                new_rv = getattr(intermediate_value, func_name)()
            else:
                pass
        intermediate_value = new_rv

    return intermediate_value


########################
##### Helper Classes
########################
class Cloud_Output:
    """
    Mutable Class that can used during the creation phases to represent a desired cloud output model.
    """

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
            id="cdev_cloud_output",
        )

    def hash(self) -> str:
        return hasher.hash_list([self._name, self._ruuid, self._key, self._type])


class Cloud_Output_Dynamic(Cloud_Output):
    """
    Mutable Class that can used during the creation phases to represent a desired cloud output model. Allows the user to define
    a list of operations that should be applied to the retrieved value.
    """

    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        super().__init__(name, ruuid, key, type)
        self._operations: List[output_operation] = []

    def render(self) -> cloud_output_dynamic_model:
        operations = tuple(
            [(x[0], tuple(x[1]), frozendict(x[2])) for x in self._operations]
        )

        return cloud_output_dynamic_model(
            name=self._name,
            ruuid=self._ruuid,
            key=self._key,
            type=self._type,
            id="cdev_cloud_output",
            output_operations=operations,
        )

    def hash(self) -> str:
        return hasher.hash_list(
            [
                super().hash(),
                self.render().output_operations if self._operations else "",
            ]
        )


########################
##### Types of Output
########################


class Cloud_Output_Bool(Cloud_Output_Dynamic):
    """
    Cloud Output that will resolve to a Boolean value after being retrieve or after all the operations have been executed
    """

    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        super().__init__(name, ruuid, key, type)

    def and_(self, x: bool) -> "Cloud_Output_Bool":
        """And against x

        Args:
            x (bool)

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "**and",
                tuple([x]),
                {},
            )
        )

        return self

    def or_(self, x: bool) -> "Cloud_Output_Bool":
        """Or against x

        Args:
            x (bool)

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "**or",
                tuple([x]),
                {},
            )
        )

        return self

    def xor_(self, x: bool) -> "Cloud_Output_Bool":
        """Xor against x

        Args:
            x (bool)

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "**xor",
                tuple([x]),
                {},
            )
        )

        return self

    def not_(self) -> "Cloud_Output_Bool":
        """Not against self

        Returns:
            Cloud_Output_Bool
        """
        # Special case because there is not underlying method to call for not so pass this hardcoded
        # value and make sure that the operation interpreter respects this token as the 'not' operator.
        self._operations.append(
            (
                "**not",
                (),
                {},
            )
        )

        return self


class Cloud_Output_Int(Cloud_Output_Dynamic):
    """
    Cloud Output that will resolve to a Integer value after being retrieve or after all the operations have been executed
    """

    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        super().__init__(name, ruuid, key, type)

    def add(self, x: int) -> "Cloud_Output_Int":
        """Add x

        Args:
            x (int)

        Returns:
            Cloud_Output_Int
        """
        self._operations.append(
            (
                "__add__",
                tuple([x]),
                {},
            )
        )

        return self

    def subtract(self, x: int) -> "Cloud_Output_Int":
        """Subtract x

        Args:
            x (int)

        Returns:
            Cloud_Output_Int
        """
        self._operations.append(
            (
                "__add__",
                tuple([x * -1]),
                {},
            )
        )

        return self

    def multiply(self, x: int) -> "Cloud_Output_Int":
        """Multiply x

        Args:
            x (int)

        Returns:
            Cloud_Output_Int
        """
        self._operations.append(
            (
                "__mul__",
                tuple([x]),
                {},
            )
        )

        return self

    def divide_mod(self, x: int) -> Tuple["Cloud_Output_Int", "Cloud_Output_Int"]:
        """Return the pair (i // x, i % x)

        Returns:
            Tuple["Cloud_Output_Int", "Cloud_Output_Int"]
        """
        self._operations.append(
            (
                "__divmod__",
                tuple([x]),
                {},
            )
        )

        return self


class Cloud_Output_Str(Sequence, Cloud_Output_Dynamic):
    """
    Cloud Output that will resolve to a String value after being retrieve or after all the operations have been executed
    """

    def __init__(self, name: str, ruuid: str, key: str, type: OutputType) -> None:
        super().__init__(name, ruuid, key, type)

    def __len__(self):
        raise Exception

    def __getitem__(self, key) -> "Cloud_Output_Str":
        self._operations.append(("__getitem__", [key], {}))

        return self

    def __contains__(self, _o: str) -> Cloud_Output_Bool:
        self._operations.append(("__contains__", [_o], {}))

        return self

    def capitalize(self) -> "Cloud_Output_Str":
        """Make the first character have upper case and the rest lower case.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "capitalize",
                (),
                {},
            )
        )
        return self

    def casefold(self) -> "Cloud_Output_Str":
        """Make S suitable for caseless comparisons.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "casefold",
                (),
                {},
            )
        )
        return self

    def center(self, width: SupportsIndex, fillchar: str = None) -> "Cloud_Output_Str":
        """S centered in a string of length width. Padding is done using the specified fill character (default is a space)

        Args:
            width (SupportsIndex)
            fillchar (str, optional)

        Returns:
            Cloud_Output_Str
        """

        if fillchar:
            args = (width, fillchar)
        else:
            args = width

        self._operations.append(
            (
                "center",
                args,
                {},
            )
        )
        return self

    def count(
        self,
        x: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Int:
        """The number of non-overlapping occurrences of substring sub in string S[start:end].

        Args:
            x (str)
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Int
        """

        if start and end:
            args = (x, start, end)
        elif start and (not end):
            args = (x, start, None)

        elif (not start) and end:
            args = (x, None, end)

        else:
            args = (x, None, None)

        self._operations.append(
            (
                "count",
                args,
                {},
            )
        )

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def endswith(
        self,
        suffix: Union[str, Tuple[str, ...]],
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Bool:
        """Return True if S ends with the specified suffix, False otherwise.

        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        suffix can also be a tuple of strings to try.

        Args:
            suffix (Union[str, Tuple[str, ...]]):
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Bool
        """

        args = []

        if suffix:
            args.append(suffix)

        if start:
            args.append(start)

        if end:
            args.append(end)

        self._operations.append(
            (
                "endswith",
                tuple(args),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def expandtabs(self, tabsize=8) -> "Cloud_Output_Str":
        """S where all tab characters are expanded using spaces.

        If tabsize is not given, a tab size of 8 characters is assumed.

        Args:
            tabsize (int, optional): Defaults to 8.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "expandtabs",
                (),
                {"tabsize": tabsize},
            )
        )
        return self

    def find(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Int:
        """Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

        Optional arguments start and end are interpreted as in slice notation.

        Args:
            sub (str)
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Int
        """

        args = [sub]

        if start:
            args.append(start)

        if end:
            args.append(end)

        self._operations.append(
            (
                "find",
                tuple(args),
                {},
            )
        )

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def format(self, *args, **kwargs) -> "Cloud_Output_Str":
        """Format S, using substitutions from args and kwargs.

        The substitutions are identified by braces ('{' and '}').

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "format",
                args,
                kwargs,
            )
        )
        return self

    def format_map(self, mapping: Dict) -> "Cloud_Output_Str":
        """Format S, using substitutions from mapping.

        The substitutions are identified by braces ('{' and '}').

        Args:
            mapping (Dict)

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "format_map",
                (),
                {"mapping": mapping},
            )
        )
        return self

    def index(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Int:
        """Return the lowest index in S where substring sub is found, such that sub is contained within S[start:end].

        Optional arguments start and end are interpreted as in slice notation.

        When evaluating, raises ValueError if the substring is not found.

        Args:
            sub (str)
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Int
        """

        args = [sub]

        if start:
            args.append(start)

        if end:
            args.append(end)

        self._operations.append(
            (
                "index",
                tuple(args),
                {},
            )
        )

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isalnum(self) -> Cloud_Output_Bool:
        """Return True if all characters in S are alphanumeric and there is at least one character in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isalnum",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isalpha(self) -> Cloud_Output_Bool:
        """Return True if all characters in S are alphabetic and there is at least one character in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isalpha",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isdecimal(self) -> Cloud_Output_Bool:
        """Return True if there are only decimal characters in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isdecimal",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isdigit(self) -> Cloud_Output_Bool:
        """Return True if all characters in S are digits and there is at least one character in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isdigit",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isidentifier(self) -> Cloud_Output_Bool:
        """Return True if S is a valid identifier according to the language definition.

        Use keyword.iskeyword() to test for reserved identifiers
        such as "def" and "class".

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isidentifier",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def islower(self) -> Cloud_Output_Bool:
        """Return True if all cased characters in S are lowercase and there is at least one cased character in S, False otherwise.


        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "islower",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isnumeric(self) -> Cloud_Output_Bool:
        """Return True if there are only numeric characters in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isnumeric",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isprintable(self) -> Cloud_Output_Bool:
        """Return True if all characters in S are considered printable in repr() or S is empty, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isprintable",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isspace(self) -> Cloud_Output_Bool:
        """Return True if all characters in S are whitespace and there is at least one character in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isspace",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def istitle(self) -> Cloud_Output_Bool:
        """Return True if S is a titlecased string and there is at least one
        character in S, i.e. upper- and titlecase characters may only
        follow uncased characters and lowercase characters only cased ones.
        Return False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "istitle",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def isupper(self) -> Cloud_Output_Bool:
        """Return True if all cased characters in S are uppercase and there is
        at least one cased character in S, False otherwise.

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(
            (
                "isupper",
                (),
                {},
            )
        )

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def join(self, iterable: Iterable[str]) -> "Cloud_Output_Str":
        """Return a string which is the concatenation of the strings in the iterable with S being the separator.

        Args:
            iterable (Iterable[str])

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "join",
                iterable,
                {},
            )
        )
        return self

    def ljust(self, width: SupportsIndex, __fillchar: str = "") -> "Cloud_Output_Str":
        """Return S left-justified in a Unicode string of length __width.

        Padding is done using the specified fill character (default is a space).

        Args:
            width (SupportsIndex)
            __fillchar (str, optional): Defaults to "".

        Returns:
            Cloud_Output_Str
        """

        args = [width]

        if __fillchar:
            args.append(__fillchar)

        self._operations.append(
            (
                "ljust",
                tuple(args),
                {},
            )
        )
        return self

    def lower(self) -> "Cloud_Output_Str":
        """Return a copy of the string S converted to lowercase.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "lower",
                (),
                {},
            )
        )
        return self

    def lstrip(self, chars: Optional[str] = None) -> "Cloud_Output_Str":
        """Return a copy of the string S with leading whitespace removed.

        If chars is given and not None, remove characters in chars instead.

        Args:
            chars (Optional[str], optional): Defaults to None.

        Returns:
            Cloud_Output_Str
        """

        args = []

        if chars:
            args.append(chars)
        self._operations.append(
            (
                "lstrip",
                tuple(args),
                {},
            )
        )

        return self

    def replace(
        self, old: str, new: str, count: SupportsIndex = None
    ) -> "Cloud_Output_Str":
        """Change all occurrences of substring old replaced by new.

        If the optional argument count is given, only the first count occurrences are replaced.

        Args:
            old (str)
            new (str)
            count (SupportsIndex, optional): Defaults to None.

        Returns:
            Cloud_Output_Str
        """

        if count:
            args = (old, new, count)
        else:
            args = (old, new)

        self._operations.append(
            (
                "replace",
                args,
                {},
            )
        )

        return self

    def rfind(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Int:
        """Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

        Optional arguments start and end are interpreted as in slice notation.

        Return -1 on failure.

        Args:
            sub (str)
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Int
        """
        args = [sub]

        if start:
            args.append(start)

        if end:
            args.append(end)

        self._operations.append(
            (
                "rfind",
                tuple(args),
                {},
            )
        )

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def rindex(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Int:
        """Return the highest index in S where substring sub is found, such that sub is contained within S[start:end].

        Optional arguments start and end are interpreted as in slice notation.

        When evaluating, raises ValueError if the substring is not found.

        Args:
            sub (str)
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Int
        """

        args = [sub]

        if start:
            args.append(start)

        if end:
            args.append(end)

        self._operations.append(
            (
                "rindex",
                (),
                {
                    "__sub": sub,
                    "__start": start,
                    "__end": end,
                },
            )
        )

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def rjust(self, width: SupportsIndex, fillchar: str = None) -> "Cloud_Output_Str":
        """Right-justify S in a string of length width. Padding is
        done using the specified fill character (default is a space).


        Args:
            width (SupportsIndex):
            fillchar (str, optional): Defaults to None.

        Returns:
            Cloud_Output_Str
        """
        args = [width]

        if fillchar:
            args.append(fillchar)

        print(args)
        self._operations.append(
            (
                "rjust",
                tuple(args),
                {},
            )
        )

        return self

    # def rsplit(
    #    self,
    #    sep: Optional[str] = None,
    #    maxsplit: Optional[SupportsIndex] = None) -> List['Cloud_Output_Str']:
    #    """Return a list of the words in S, using sep as the
    #    delimiter string, starting at the end of the string and
    #    working to the front.
    #
    #    Append the operation to the Cloud Output Object and return the same Cloud Output String object for any further operations.
    #
    #    If maxsplit is given, at most maxsplit splits are done.
    #
    #    If sep is not specified, any whitespace string is a separator.
    #    """
    #    args = []
    #
    #    if sep:
    #        args.append(sep)
    #
    #    if maxsplit:
    #        args.append(maxsplit)
    #
    #
    #    self._operations.append(
    #        (
    #            'rsplit',
    #            tuple(args),
    #            {},
    #        )
    #    )
    #    return self

    def rstrip(self, chars: Optional[str] = None) -> "Cloud_Output_Str":
        """Return S with trailing whitespace removed.

        If chars is given and not None, remove characters in chars instead.

        Args:
            chars (Optional[str], optional): Defaults to None.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(
            (
                "rstrip",
                (chars),
                {},
            )
        )

    # def split(
    #    self,
    #    sep=None,
    #    maxsplit=-1) -> List['Cloud_Output_Str']:
    #    """Return a list of the words in S, using sep as the delimiter string.
    #
    #    ## TODO Sequence type
    #
    #    If maxsplit is given, at most maxsplit splits are done.
    #
    #    If sep is not specified or is None, any whitespace string is a separator and empty strings are
    #    removed from the result.
    #    """
    #    self._operations.append(
    #        (
    #            'split',
    #            (sep, maxsplit),
    #            {},
    #        )
    #    )
    #
    # def splitlines(
    #    self,
    #    keepends: bool = False) -> List['Cloud_Output_Str']:
    #    """
    #    Return a list of the lines in S, breaking at line boundaries.
    #
    #    ## TODO Sequence type
    #
    #    Line breaks are not included in the resulting list unless keepends is given and true.
    #    """
    #    self._operations.append(
    #        (
    #            'splitlines',
    #            (keepends),
    #            {},
    #        )
    #    )
    #
    def startswith(
        self,
        prefix: Union[str, Tuple[str, ...]],
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> Cloud_Output_Int:
        """Return True if S starts with the specified prefix, False otherwise.

        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        prefix can also be a tuple of strings to try.

        Args:
            prefix (Union[str, Tuple[str, ...]]):
            start (Optional[SupportsIndex], optional): Defaults to None.
            end (Optional[SupportsIndex], optional): Defaults to None.

        Returns:
            Cloud_Output_Int
        """

        args = [prefix]

        if start:
            args.append(start)

        if end:
            args.append(end)

        self._operations.append(
            (
                "startswith",
                tuple(args),
                {},
            )
        )

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def strip(self, chars: Optional[str] = ...) -> "Cloud_Output_Str":
        """S with leading and trailing whitespace removed.

        If chars is given and not None, remove characters in chars instead.

        Args:
            chars (Optional[str], optional): Defaults to ....

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(("strip", (chars), {}))
        return self

    def swapcase(self) -> "Cloud_Output_Str":
        """S with uppercase characters converted to lowercase and vice versa.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(("swapcase", (), {}))

        return self

    def title(self) -> "Cloud_Output_Str":
        """Titlecased version of S

        i.e. words start with title case characters, all remaining cased characters have lower case.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(("title", (), {}))
        return self

    def translate(
        self,
        table: Mapping[int, Union[Union[int, str, None], List[Union[int, str, None]]]],
    ) -> "Cloud_Output_Str":
        """S in which each character has been mapped through the given translation table.

        The table must implement
        lookup/indexing via __getitem__, for instance a dictionary or list,
        mapping Unicode ordinals to Unicode ordinals, strings, or None. If
        this operation raises LookupError, the character is left untouched.
        Characters mapped to None are deleted.

        Args:
            table (Mapping[int, Union[Union[int, str, None], List[Union[int, str, None]]]]):

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(("translate", (table), {}))

    def upper(self) -> "Cloud_Output_Str":
        """Return a copy of S converted to uppercase.

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(("upper", (), {}))

        return self

    def zfill(self, width: SupportsIndex) -> "Cloud_Output_Str":
        """Pad a numeric string S with zeros on the left, to fill a field of the specified width.

        The string S is never truncated.

        Args:
            width (SupportsIndex)

        Returns:
            Cloud_Output_Str
        """
        self._operations.append(("zfill", tuple([width]), {}))

        return self


# Wrapper type to denote all the possible single value outputs
T = TypeVar(
    "T", Cloud_Output_Dynamic, Cloud_Output_Str, Cloud_Output_Int, Cloud_Output_Bool
)


class Cloud_Output_Sequence(Sequence, Cloud_Output_Dynamic, Generic[T]):
    """
    Cloud Output that will resolve to a Sequence of values after being retrieve or after all the operations have been executed
    """

    def __init__(
        self, name: str, ruuid: str, key: str, type: OutputType, _member_class
    ) -> None:
        super().__init__(name, ruuid, key, type)

        self._member_class = _member_class

    def __len__(self):
        raise Exception

    # Use these stub methods to define the typing signature so that the output is correct based on the input given
    @overload
    def __getitem__(self, key: slice) -> "Cloud_Output_Sequence[T]":
        pass

    @overload
    def __getitem__(self, key: int) -> T:
        pass

    # implementation
    def __getitem__(self, key):
        """Provides API for lazy evaluating __getitem__

        Args:
            key (_type_)

        Raises:
            Exception

        Returns:
            _type_
        """
        self._operations.append(("__getitem__", [key], {}))

        if isinstance(key, slice):
            return self

        elif isinstance(key, int):
            rv = self._member_class(self._name, self._ruuid, self._key, self._type)

            rv._operations = self._operations.copy()

            return rv

        else:
            raise Exception

    def __contains__(self, o: Any) -> Cloud_Output_Bool:
        """Provides API for lazy evaluating __contains__

        Args:
            o (Any)

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(("__contains__", [o], {}))

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def __len__(self) -> Cloud_Output_Int:
        """Provides API for lazy evaluating __len__

        Returns:
            Cloud_Output_Int
        """
        self._operations.append(("__len__", [], {}))

        rv = Cloud_Output_Int(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv


class Cloud_Output_Mapping(Sequence, Cloud_Output_Dynamic, Generic[T]):
    """
    Cloud Output that will resolve to a Mapping of string to values (after being retrieved or after all the operations have been executed).
    """

    def __init__(
        self, name: str, ruuid: str, key: str, type: OutputType, _member_class
    ) -> None:
        super().__init__(name, ruuid, key, type)

        self._member_class = _member_class

    def __len__(self):
        raise Exception

    # implementation
    def __getitem__(self, key: str) -> T:
        """Provides API for lazy evaluating __getitem__

        Args:
            key (str)

        Raises:
            Exception

        Returns:
            T
        """
        if not isinstance(key, str):
            raise Exception

        self._operations.append(("__getitem__", [key], {}))

        rv = self._member_class(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv

    def __contains__(self, _o: str) -> Cloud_Output_Bool:
        """Provides API for lazy evaluating __contains__

        Args:
            _o (str)

        Returns:
            Cloud_Output_Bool
        """
        self._operations.append(("__contains__", [_o], {}))

        rv = Cloud_Output_Bool(self._name, self._ruuid, self._key, self._type)

        rv._operations = self._operations.copy()

        return rv
