from core.constructs.output import Cloud_Output_Sequence, Cloud_Output_Str, OutputType, Cloud_Output_Mapping


t: Cloud_Output_Sequence[Cloud_Output_Str] = Cloud_Output_Sequence(
    "dev",
    "r",
    "k",
    OutputType.RESOURCE,
    Cloud_Output_Str
)

t.__contains__()


d = {'s': 1}

d.__contains__()