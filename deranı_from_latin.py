# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: CC0 version 1.0. For reading a copy of this license, please see the text file ⟪LICENSE⟫ in the top level directory.
# SPDX-License-Identifier: CC0-1.0

import sys, unicodedata, re
import pytoaq.latin as pytoaq

def entrypoint(self_path, latin_toaq):
  assert(isinstance(latin_toaq, str))
  sys.stdout.write(f"{deranı_from_latin(latin_toaq)}\n")
  return

def deranı_from_latin(lt):
  lt = lt.lower()
  lt = unicodedata.normalize("NFD", lt)
  lt = lt.replace("i", "ı")
  lt = re.sub(
    f"(^|[^{pytoaq.std_consonant_str}])([aeıou](aı|ao|eı|oı))",
    r"\1'\2", lt)
  CUD = "̣" # Combining underdot
  CAA = "́" # Combinite acute accent
  CS = pytoaq.std_consonant_str + "aeıou" + CUD
  r = f"[{pytoaq.word_initial_str}]h?[aeıou][{CUD}]?[{CAA}][{CS}]*"
  lt = re.sub(r, add_cartouche, lt)
  lt = re.sub(
    f"̣([́̂{CUD}]?[aeıou]?[mq]?)([{pytoaq.std_consonant_str}])", r"\1\2",
    lt)
  lt = re.sub("([aeıou])([́̈̂])", r"\2\1", lt)
  lt = re.sub(
    "(?!(aı|ao|eı|oı))([aeıou])((?!(aı|ao|eı|oı))[aeıou])", r"\2\3", lt)
  lt = re.sub("([aeıou])m", r"\1", lt)
  lt = re.sub(" (da)[.…]", r" \1 ", lt)
  lt = re.sub(" (ka|ba|nha|doa|ꝡo|dâ|môq)[.…]", r" \1 ", lt)
  lt = re.sub(" (móq)[.…?]", r" \1 ", lt)
  i = 0
  while i < len(lt):
    lt = deranı_from_latin_2(lt, i, deranı_from_latin.map2, 2)
    lt = deranı_from_latin_2(lt, i, deranı_from_latin.map1, 1)
    i += 1
  return lt
  # TODO:
  #   ◆ Cartouches : handle PO, SHU, MO…
  #   ◆ Cartouches : t1 words following determiners.
  #   ◆ Empty cartouche
  #   ◆ ⟪▓▓⟫: shu-names, onomastics

def deranı_from_latin_2(lt, i, m, l):
  l = min(l, len(lt) - i)
  r = m.get(lt[i : i + l])
  if r is not None:
    lt = with_replaced_interval(lt, i, i + l, r)
  return lt

def with_replaced_interval(s1, i, j, s2):
  assert isinstance(s1, str)
  assert isinstance(s2, str)
  assert isinstance(i, int)
  assert isinstance(j, int)
  assert i < j
  return s2.join([s1[:i], s1[j:]])

NFD_cartoucheless_words = {
  unicodedata.normalize("NFD", p).replace("i", "ı")
  for p in (
    pytoaq.pronouns | pytoaq.determiners
    | pytoaq.functors_with_lexical_tone
    | {
      pytoaq.inflected_from_lemma(l, "´")
      for l in pytoaq.functors_with_grammatical_tone
    }
  )
}

def add_cartouche(m):
  w = m.group(0)
  if w not in NFD_cartoucheless_words:
    if all([s not in w for s in ("hụ́", "hụ́")]):
      w = "" + w + ""
  return w

deranı_from_latin.map1 = {
  "m": "",
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

