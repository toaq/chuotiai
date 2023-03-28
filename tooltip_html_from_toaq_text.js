
function is_string(v) {
  return Object.prototype.toString.call(v) === '[object String]';
}

function is_array(v) {
  return Object.prototype.toString.call(v) === '[object Array]';
}

function is_undefined(v) {
  return Object.prototype.toString.call(v) === '[object Undefined]';
}

function with_escaped_html(text) {
  return text.replace(/[&<>"']/g, function(ch) {
    switch (ch) {
      case '&':
        return '&amp;';
      case '<':
        return '&lt;';
      case '>':
        return '&gt;';
      case '"':
        return '&quot;';
      default:
        return '&#039;';
        /* '&apos;' in another option in HTML5, but is absent from
           HTML4. */
    }
  });
};

function normalized(toa) {
  console.assert(
    is_string(toa),
    "ERROR: normalized(): The argument is not a string!");
  return toa.normalize('NFD')
            .toLowerCase()
            .replace(/i/g, 'ı')
            .replace(/[\u0300-\u030f\u0323]/g, '')
            .replace(/[^0-9A-ZꝠa-zıꝡ'\u0323_\-]+/g, ' ')
            .replace(/ +/g, ' ')
            .trim();
}

function get_definition(entry, language) {
  if (language == "eng" && !is_undefined(entry.english)) {
    return entry.english;
  }
  if (!is_undefined(entry.translations)) {
    for (const item of entry.translations) {
      if (item.language === language)
        return item.definition;
    }
  }
  return ""; // Definition not found.
}

function with_combining_underdots(s) {
  return s.replace(/[ạẹịọụ]/ig, (m) => m.normalize('NFD'));
}

function  with_hyphenated_prefixes(s) {
  s = s.replace(/\u0323/g, "\u0323");
  s = s.replace(/m(['bcdfghjklmnprstvwxyzꝡ])/ig, "m-$1");
  s = s.replace(
    /(?<=\b)((?:['bcdfghjklmnprstvwxyzꝡ]h?[aeıiouáéíóúâêîôû\u0323]+q?[\-]?)*)(?=\u0091)/ig,
    (m) => m.replace(
      /([bcdfghjklmnpqrstvwxyzꝡ]?h?[aeıiouáéíóúâêîôû\u0323]+[mq]?)(?=['bcdfghjklmnprstvwxyzꝡ\u0091])/ig, "$1-"
    )
  );
  s = s.replace(/(?![\-])\u0091/g, "-\u0091");
  return s
}

function tooltip_html_from_toaq_text(dictionary, text) {
  /*** AUTOMATIC WORD DEFINITION TOOLTIPS FOR TOAQ TEXTS ***/
  text = text.replace(/-(?=[aeiıou])/ig, "-'");
  text = text.replace(/(?<![aeıiouáéíóúâêîôû])([aeıiouáéíóúâêîôû])([aeıiouáéíóúâêîôû]*-)(['bcdfghjklmnprstvwxyzꝡaeiıou]+)(?![\-])/ig, "$1\u0323$2\u0091$3");
  text = with_combining_underdots(text);
  text = text.replace(/([aeoáéóâêô]\u0323[iıou]?)(?![\-])/ig, "$1\u0091");
  text = with_hyphenated_prefixes(text);
  text = text.replace(/-(?!\u0091)/g, "-\u0091");
  // `dictionary` is the content of the loaded dictionary JSON.
  var hoetoalai = "\\-'’a-zA-Zıāēīōūȳáéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹꝡ"
              + "ĀĒĪŌŪȲÁÉÍÓÚÝÄËÏÖÜŸǍĚǏǑǓẢẺỈỎỦỶÂÊÎÔÛŶÀÈÌÒÙỲÃẼĨÕŨỸꝠ"
              + "ạẹịọụẠẸỊỌỤ" + "\u0300-\u030f\u0323";
  if (is_undefined(tooltip_html_from_toaq_text.content_re)) {
    tooltip_html_from_toaq_text.content_re = new RegExp(
      "<[^>]*>|[" + hoetoalai + "]+|[^<" + hoetoalai + "]", "g");
    tooltip_html_from_toaq_text.toaq_re = new RegExp(
      "[" + hoetoalai + "].*")
    /* ^ This way, the regexp objects will be generated only
      once and not upon each call of the function. */
  }
  // Loading the Toaq text from the elements of class `with_tooltip_definitions`:
  /* Splitting the content into an array of things that are either
     Toaq words or are other stuff (blanks, HTML tags…): */
  var content = text.match(tooltip_html_from_toaq_text.content_re);
  if (content === null)
    return;
  content.forEach(function (item, index, array) {
    // For each item in `content`, we check whether it's a Toaq word:
    if (item != "" && tooltip_html_from_toaq_text.toaq_re.test(item)) {
      /* It is a Toaq word, so we get a normalized form of it
        (removing diacritics and having dotless i's: */
      var normalized_word = normalized(item);
      if (normalized_word[0] == "'")
        normalized_word = normalized_word.slice(1);
      // Now we look up the dictionary for the word:
      dictionary.every(function (entry, i, arr) {
        function f(toaq, is_official) {
          normalized_toaq = normalized(toaq);
          if (normalized_toaq == normalized_word || (
            '-' == normalized_word[normalized_word.length - 1]
            && normalized_toaq == normalized_word.slice(
              0, normalized_word.length - 1)
          )) {
            // We have found the word in the dictionary.
            // Now we fetch its definition and check if it isn't empty.
            var def = get_definition(entry, "eng");
            if (def) {
              def = with_escaped_html(def);
              // Now we create a tooltip containing its definition:
              var tip = is_official ? "tip" : "tip-unofficial tip";
              var tiptext = is_official ?
                "tiptext" : "tiptext-unofficial tiptext";
              array[index] = '<div class="' + tip + '">'
                 + item.replace(/-/g, "") + '<span class="' + tiptext + '">'
                 + toaq + ' : ' + def + '</span></div>';
            }
            return true;
          } else return false
        }
        console.assert(
          'toaq_forms' in entry && is_array(entry.toaq_forms),
          "ERROR: No valid `toaq_forms` field in the dictionary entries!");
        the_word_has_been_found = false;
        entry.toaq_forms.every(function (e, i, l) {
          console.assert(
            is_string(e.toaq) || is_array(e.toaq),
             "ERROR: `e.toaq` is not a string or an array but a "
             + Object.prototype.toString.call(e.toaq));
          if (!is_string(e.toaq))
            return false;
          the_word_has_been_found = f(e.toaq, e.is_official);
          return !the_word_has_been_found;
        });
        /* If we don't find the word in the dictionary, no tooltip
           is created. Nothing will happen when hovering the word
           with the mouse pointer. */
        return !the_word_has_been_found;
      });
    }
  });
  return content.join("").replace(/\u0091/g, "");
}


