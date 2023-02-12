#!/usr/bin/env python3

import sondehub
import json

def on_message(message):
    print(type(message))
    print(json.dumps(message, indent = 2))
    print(type(message), len(message))

test = sondehub.Stream(on_message=on_message, sondes=["22049077"])
while 1:
    pass