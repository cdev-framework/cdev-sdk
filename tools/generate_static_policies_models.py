import os
import json
from typing_extensions import final
from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Environment(
    loader=FileSystemLoader(os.path.join(".")),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)

with open(os.path.join(".", "aws_managed_policies.json")) as fh:
    initial_info = json.load(fh)


final_info = []

for name,obj in initial_info.items():
    final_info.append(obj)

template1 = env.get_template("static-policy-template.py.jinja")
rendered_template1 = template1.render(**{"policies": final_info})
with open(os.path.join(".","output", "managed_policies", f"managed_policies.py"), "w") as fh:
    fh.write(rendered_template1)
