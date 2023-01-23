# LATIN TOAQ MODULE

# ==================================================================== #

import std/sets
from std/sequtils import mapIt
from std/tables import contains
import std/nre
from std/strutils import contains, find, join
from std/strformat import fmt
from std/unicode import
  `==`, `$`, Rune, toRunes, toUTF8, runeLen, runeAtPos
from std/enumerate import enumerate
from std/sugar import `=>`

proc `@&`[T](keys: openArray[T]): HashSet[T] =
  return sets.toHashSet(keys)


# ==================================================================== #

const vowel_str* = "aeiıouáéíóúäëïöüâêîôûạẹịı̣ọụạ́ẹ́ị́ọ́ụ́ạ̈ẹ̈ị̈ọ̈ụ̈ậệị̂ộụ̂"
const std_vowel_str* = "aeıouáéíóúäëïöüâêîôûạẹı̣ọụạ́ẹ́ị́ọ́ụ́ạ̈ẹ̈ị̈ọ̈ụ̈ậệị̂ộụ̂"
const vowels* = vowel_str
const std_vowels* = std_vowel_str
const consonant_str* = "'bcdfghjȷklmnprstzqꝡ"
const initial_str* = "'bcdfghjȷklmnprstzꝡ"
const word_initial_str* = "bcdfghjȷklmnprstzꝡ"
const std_consonant_str* = "'bcdfghjklmnprstzqꝡ"
const std_initial_str* = "'bcdfghjklmnprstzꝡ"
const std_word_initial_str* = "bcdfghjklmnprstzꝡ"
const charset* = vowel_str & consonant_str
const std_charset* = std_vowel_str & std_consonant_str

const initials* = @["m", "b", "p", "f", "n", "d", "t", "z", "c", "s", "r", "l", "nh", "j", "ȷ", "ch", "sh", "ꝡ", "g", "k", "'", "h"]
const finals* = @["m", "q"]
const consonants* = initials & @["q"]
const std_initials* = @["m", "b", "p", "f", "n", "d", "t", "z", "c", "s", "r", "l", "nh", "j", "ch", "sh", "ꝡ", "g", "k", "'", "h"]
const std_consonants* = std_initials & @["q"]

# ==================================================================== #

const matrix_subordinators* = @&["ꝡa", "ma", "tıo"]
const nominal_subordinators* =
   @&["ꝡä", "mä", "tïo", "lä", "ꝡé", "ná", "é"]
const adnominal_subordinators* = @&["ꝡë", "ë", "jü"]
const predicatizers* = @&["jeı", "mea", "po"]
const determiners* = @&[
  "ló", "ké", "sá", "sía", "tú", "túq", "báq", "já", "hí", "ní", "hú"]
const type_1_conjunctions* = @&["róı", "rú", "rá", "ró", "rí", "kéo"]
const type_2_conjunctions* = @&["roı", "ru", "ra", "ro", "rı", "keo"]
const type_3_conjunctions* = @&["rôı", "rû", "râ", "rô", "rî", "kêo"]
const conjunctions* = (
  type_1_conjunctions + type_2_conjunctions + type_3_conjunctions)
const falling_tone_illocutions* =
  @&["ka", "da", "ba", "nha", "doa", "ꝡo"]
const peaking_tone_illocutions* = @&["dâ", "môq"]
const raising_tone_illocutions* = @&["móq"]
const illocutions* = (
  falling_tone_illocutions + raising_tone_illocutions +
  peaking_tone_illocutions)
const focus_markers* = @&["kú", "tóu", "béı"]
const preverbals* = @&["bï", "nä"]
const vocative* = @&["hóı"]
const terminators* = @&["teo", "kı"]
const exophoric_pronouns* = @&[
  "jí", "súq", "nháo", "súna", "nhána", "úmo", "íme", "súho", "áma", "há"
]
const endophoric_pronouns* =
  @&["hóa", "hó", "máq", "tá", "hóq", "róu", "zé", "bóu", "áq", "chéq"]
const pronouns* = exophoric_pronouns + endophoric_pronouns

const functors_with_grammatical_tone* =
  predicatizers + @&["mı", "shu", "mo"]

const functors_with_lexical_tone* = (
  matrix_subordinators + nominal_subordinators +
  adnominal_subordinators + determiners + conjunctions + illocutions +
  focus_markers + preverbals + vocative + terminators + @&["gö", "kïo"]
)

const functor_lemmas* = (
  functors_with_grammatical_tone + functors_with_lexical_tone)

const toneless_particles* = (
  matrix_subordinators + falling_tone_illocutions + terminators)

const interjections* = @&[
  "m̄", "ḿ", "m̈", "m̉", "m̂", "m̀", "m̃"
]

# ==================================================================== #

func is_a_contentive_lemma*(s: string): bool =
  return isSome(nre.match(s, re(
    "(*UTF8)" &
    fmt"([{std_word_initial_str}]h?)?[aeıouạẹı̣ọụ]+[mq]?" &
    fmt"(([{std_consonant_str}]h?)[aeıouạẹı̣ọụ]+[mq]?)*$"
  )))

func is_a_lemma*(s: string): bool =
  return (
    is_a_contentive_lemma(s) or
    (toneless_particles + functors_with_lexical_tone + interjections)
    .contains(s)
  )

func with_replaced_interval[T](s1: T, i: int, j: int, s2: T): T
func first[T](
  s: seq[T], has_property: proc (e: T): bool {.noSideEffect.}): int
func inflected_vowel(vowel: string, tone: string): string
func utf8_with_replaced_characters[T: seq[Rune] or string](
  str: T,
  src_chars: string,
  rep_chars: string
): string

func inflected_from_lemma*(lemma: string, tone: string): string =
  assert(runeLen(tone) == 1)
  assert(is_a_lemma(lemma))
  assert(
    not (functors_with_lexical_tone + interjections).contains(lemma))
  let lemma_rs = toRunes(lemma)
  const vowels = toRunes("aeıou")
  let i = first(lemma_rs, (rune: Rune) => vowels.contains(rune))
  return (
    with_replaced_interval(
    lemma_rs, i, i + 1, toRunes(
      inflected_vowel(lemma_rs[i].toUTF8(), tone)))
  ).mapIt(it.toUTF8()).join()

func inflected_vowel(vowel: string, tone: string): string =
  assert("aeıou".contains(vowel))
  var targets: string
  if @["´", "́"].contains(tone):
    targets = "áéíóú"
  elif @["^", "̂"].contains(tone):
    targets = "âêîôû"
  elif @["¨", "̈"].contains(tone):
    targets = "äëïöü"
  else:
    raise newException(ValueError, fmt"Invalid tone: ⟪{tone}⟫")
  return utf8_with_replaced_characters(vowel, "aeıou", targets)

func first[T](
  s: seq[T],
  has_property: proc (e: T): bool {.noSideEffect.}
): int =
  for i, e in enumerate(s):
    if has_property(e):
      return i
  return -1

func first_rune(
  s: string,
  has_property: proc (rune: Rune): bool {.noSideEffect.}
): int =
  let l = runeLen(s)
  for i in 0 ..< l:
    if has_property(runeAtPos(s, i)):
      return i
  return -1

func with_replaced_interval[T](s1: T, i: int, j: int, s2: T): T =
  assert(i < j)
  return s1[ 0..< i] & s2 & s1[j .. ^1]

func utf8_with_replaced_characters[T: seq[Rune] or string](
  str: T,
  src_chars: string,
  rep_chars: string
): string =
  let src_l = toRunes(src_chars)
  let rep_l = toRunes(rep_chars)
  when T is string:
    var str_l = str
  else: # T is seq[Rune]
    var str_l = toRunes(str)
  var i = 0
  while i < str_l.len:
    if src_l.contains(str_l[i]):
      var k = first(src_l, (r: Rune) => r == str_l[i])
      str_l = str_l[0 ..< i] & rep_l[k] & str_l[i + 1 .. ^1]
    i += 1
  return str_l.mapIt($it).join("")

