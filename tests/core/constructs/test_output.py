from core.constructs.output import *

# contents of test_append.py
import pytest


@pytest.fixture
def simple_str_examples() -> List[Tuple[str, Cloud_Output_Str, str]]:
    return [
        ("demo", _cloud_output_str_factory().capitalize(), "demo".capitalize()),
        ("belligerent", _cloud_output_str_factory().casefold(),"belligerent"),
        ("classy", _cloud_output_str_factory().center(3, "w"),"classy".center(3,"w")),
        ("gold",_cloud_output_str_factory().count('go'),"gold".count('go')),
        ("downtown",_cloud_output_str_factory().endswith('town'),"downtown".endswith('town')),
        ("cold",_cloud_output_str_factory().expandtabs(),"cold".expandtabs()),
        ("twig",_cloud_output_str_factory().find('wig'),"twig".find('wig')),
        ("{} a {}",_cloud_output_str_factory().format('cook', "cake"),"{} a {}".format("cook", "cake")),
        ("outrageous",_cloud_output_str_factory().index('out'),"outrageous".index('out')),
        ("fly",_cloud_output_str_factory().isalnum(),"fly".isalnum()),
        ("scene",_cloud_output_str_factory().isalpha(),"scene".isalpha()),
        ("spiky",_cloud_output_str_factory().isdecimal(),"spiky".isdecimal()),
        ("precede",_cloud_output_str_factory().isdigit(),"precede".isdigit()),
        ("attend", _cloud_output_str_factory().isidentifier(), "attend".isidentifier()),
        ("fresh", _cloud_output_str_factory().isnumeric(), "fresh".isnumeric()),
        ("cup", _cloud_output_str_factory().islower(), "cup".islower()),
        ("malicious", _cloud_output_str_factory().isprintable(), "malicious".isprintable()),
        ("frighten", _cloud_output_str_factory().isspace(), "frighten".isspace()),
        ("match", _cloud_output_str_factory().istitle(), "match".istitle()),
        ("murder", _cloud_output_str_factory().isupper(), "murder".isupper()),
        ("impartial", _cloud_output_str_factory().join(['judge']), "impartial".join('judge')),
        ("knock", _cloud_output_str_factory().ljust(3), "knock".ljust(3)),
        ("    smash", _cloud_output_str_factory().lstrip(), "    smash".lstrip()),
        ("wretchED", _cloud_output_str_factory().lower(), "wretchED".lower()),
        ("popcorn", _cloud_output_str_factory().rjust(3), "popcorn".rjust(3)),
        #("observant", _cloud_output_str_factory().rsplit('s'), "observant".rsplit('s')),
        ("superficial", _cloud_output_str_factory().replace('sup', 'soup'), "superficial".replace('sup', 'soup')),
        ("curve", _cloud_output_str_factory().startswith('cur'), "curve".startswith('cur')),
        ("arithmetic", _cloud_output_str_factory().swapcase(), "arithmetic".swapcase()),
        ("shiny", _cloud_output_str_factory().title(), "shiny".title()),
        ("wrench", _cloud_output_str_factory().upper(), "wrench".upper()),
        ("wandering", _cloud_output_str_factory().zfill(5), "wandering".zfill(5)),
    ]

@pytest.fixture
def simple_int_examples() -> List[Tuple[int, Cloud_Output_Str, int]]:
    return [
        (1, _cloud_output_int_factory().add(2), 1+2),
        (2, _cloud_output_int_factory().multiply(3), 2*3),
        (3, _cloud_output_int_factory().subtract(1), 3-1),
        #(-4, _cloud_output_int_factory().abs(), -4),
    ]


def _cloud_output_str_factory() -> Cloud_Output_Str:
    return Cloud_Output_Str(
        'r1',
        'r',
        'k',
        OutputType.RESOURCE
    )

def _cloud_output_int_factory() -> Cloud_Output_Int:
    return Cloud_Output_Int(
        'r1',
        'r',
        'k',
        OutputType.RESOURCE
    )

def _cloud_output_bool_factory() -> Cloud_Output_Bool:
    return Cloud_Output_Bool(
        'r1',
        'r',
        'k',
        OutputType.RESOURCE
    )

def _cloud_output_list_factory() -> Cloud_Output_Sequence[Cloud_Output_Str]:
    return Cloud_Output_Sequence(
        'r1',
        'r',
        'k',
        OutputType.RESOURCE
    )



def test_cloud_output_str(simple_str_examples):
    for test in simple_str_examples:
        input_str = test[0]
        cloud_output: Cloud_Output_Str = test[1]
        final_result = test[2]

        assert final_result == evaluate_dynamic_output(input_str, cloud_output.render())



def test_cloud_output_int(simple_int_examples):
    for test in simple_int_examples:
        input_int = test[0]
        cloud_output: Cloud_Output_Int = test[1]
        final_result = test[2]

        print(cloud_output._operations)
        assert final_result == evaluate_dynamic_output(input_int, cloud_output.render())


