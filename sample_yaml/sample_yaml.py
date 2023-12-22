#!/usr/bin/env python3

import yaml
import sys

try:
    with open('sample.yaml') as file:
        ctl = yaml.safe_load(file)
        print(ctl)
except Exception as e:
    print('Exception occurred while loading YAML...', file=sys.stderr)
    print(e, file=sys.stderr)
    sys.exit(1)

test1=ctl['y']
test2=ctl['z']
print(ctl['x'],test1+test2[0])
