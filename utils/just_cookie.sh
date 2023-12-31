#!/bin/bash

read input

egrep -o 'session\s[^\s]+$' | sed 's/session\s//g'
