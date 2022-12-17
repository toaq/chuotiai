# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: CC0 version 1.0. For reading a copy of this license, please see the text file ⟪LICENSE⟫ in the top level directory.
# SPDX-License-Identifier: CC0-1.0

import sys, unicodedata, re

def entrypoint(self_path, latin_toaq):
  assert(isinstance(latin_toaq, str))
  sys.stdout.write(f"{deranı_from_latin(latin_toaq)}\n")
  return

def with_replaced_interval(s, i, j, s2):
  assert isinstance(s, str)
  assert isinstance(s2, str)
  assert isinstance(i, int)
  assert isinstance(j, int)
  assert i < j
  return s2.join([s[:i], s[j:]])

def deranı_from_latin(lt):
  lt = lt.lower()
  lt = unicodedata.normalize("NFD", lt)
  lt = lt.replace("i", "ı")
  lt = re.sub("([aeıou])([́̈̂])", r"\2\1", lt)
  lt = re.sub("(?!(aı|ao|eı|oı))([aeıou])([aeıou])", r"\2\3", lt)
  i = 0
  while i < len(lt):
    lt = deranı_from_latin_2(lt, i, deranı_from_latin.map2, 2)
    lt = deranı_from_latin_2(lt, i, deranı_from_latin.map1, 1)
    i += 1
  return lt

def deranı_from_latin_2(lt, i, m, l):
  l = min(l, len(lt) - i)
  r = m.get(lt[i : i + l])
  if r is not None:
    lt = with_replaced_interval(lt, i, i + l, r)
  return lt

deranı_from_latin.map1 = {
  "m": "",
  "w": "",
  "b": "",
  "u": "",
  "p": "",
  "f": "",
  "e": "",
  "n": "",
  "d": "",
  "t": "",
  "z": "",
  "c": "",
  "ı": "",
  "s": "",
  "a": "",
  "r": "",
  "l": "",
  "j": "",
  "ꝡ": "",
  "q": "",
  "g": "",
  "o": "",
  "k": "",
  "ʼ": "",
  "'": "",
  "h": "",
  "́": "",
  "̈": "",
  "̂": "",
  "-": "",
#  "̣": "",
  ":": "",
  ",": " ",
  "[": "",
  "]": "",
  ".": " ",
  ";": " ",
  "?": " "
}

deranı_from_latin.map2 = {
  "nh": "",
  "ch": "",
  "sh": "",
  "aı": "",
  "ao": "",
  "oı": "",
  "eı": "",
  "[]": ""
}


# === ENTRY POINT === #

entrypoint(*sys.argv)

