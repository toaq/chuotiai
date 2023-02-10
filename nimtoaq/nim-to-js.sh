#!/bin/bash
nim js -d:nodejs -d:release --opt:speed deranı_from_latin.nim
mv deranı_from_latin.js deranı_from_latin_node.js
nim js -d:release --opt:speed deranı_from_latin.nim


