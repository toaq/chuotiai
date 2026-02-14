
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
  key = language + "_definition";
  if (!is_undefined(entry[key])) {
    return entry[key];
  } else {
    return ""; // Definition not found.
  }
}

function with_combining_underdots(s) {
  return s.replace(/[ạẹịọụ]/ig, (m) => m.normalize('NFD'));
}

function with_hyphenated_prefixes(s) {
  // ⟪\u0323⟫ ↦ Combining dot below
  s = s.replace(
    /(?<=\b)((?:['bcdfghjklmnprstvwxyzꝡ]h?[aeıiouáéíóúâêîôû\u0323]+[mq]?[\-]?)*)(?=\u0091)/ig,
    (m) => m.replace(
      /([bcdfghjklmnpqrstvwxyzꝡ]?h?[aeıiouáéíóúâêîôû\u0323]+[mq]?)(?=['bcdfghjklmnprstvwxyzꝡ\u0091][^-])/ig, "$1-"
    )
  );
  s = s.replace(/-m(?=\u0091)/g, "m-");
  s = s.replace(/(?<![\-])\u0091/g, "-\u0091");
  return s
}

function html_from_entry(entry) {
  // Now we fetch its definition and check if it isn't empty.
  var def = get_definition(entry, "eng");
  if (def) {
    def = with_escaped_html(def);
    var c = entry.is_official ?
      '' : ' style="color: #f2cf8c"';
    return (
      '<span' + c + '>➤ ' + entry.lemma + '<sub>' + entry.discriminator
      + '</sub>: ' + def + '</span><br />');
  } else return "";
}

function tooltip_html_from_toaq_text(dictionary, text) {
  /*** AUTOMATIC WORD DEFINITION TOOLTIPS FOR TOAQ TEXTS ***/
  text = text.replace(/-(?=[aeiıou])/ig, "-'");
  text = text.replace(/(?<![aeıiouáéíóúâêîôû])([aeıiouáéíóúâêîôû])([aeıiouáéíóúâêîôû]*[mq]?-)(['bcdfghjklmnprstvwxyzꝡaeiıou]+)(?![\-])/ig, "$1\u0323$2\u0091$3");
  text = with_combining_underdots(text);
  text = text.replace(/([aeıiouáéíóúâêîôû]\u0323([mq](?=['bcdfghjklmnprstvwxyzꝡ-])))/ig, "$1\u0091");
  text = text.replace(/([aeıiouáéíóúâêîôû]\u0323[iıou]?)(?![\-])(?![mq]\u0091)/ig, "$1\u0091");
  text = text.replace(/\u0091(?=-\u0091)/g, "");
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
    tooltip_content = "";
    // For each item in `content`, we check whether it's a Toaq word:
    if (item != "" && tooltip_html_from_toaq_text.toaq_re.test(item)) {
      /* It is a Toaq word, so we get a normalized form of it
        (removing diacritics and having dotless i's: */
      var normalized_word = normalized(item);
      if (normalized_word[0] == "'")
        normalized_word = normalized_word.slice(1);
      // Now we look up the dictionary for the word:
      shall_exit = false;
      the_word_has_been_found = false;
      dictionary.every(function (entry, i, arr) {
        console.assert(
          'lemma' in entry && is_string(entry.lemma),
          "ERROR: No valid `lemma` field in the dictionary entry!");
        if (normalized(entry.lemma) == normalized_word) {
	       // We have found the word in the dictionary.
          the_word_has_been_found = true;
          tooltip_content += html_from_entry(entry);
        } else if (the_word_has_been_found) {
          shall_exit = true;
        }
        /* If we don't find the word in the dictionary, no tooltip
           is created. Nothing will happen when hovering the word
           with the mouse pointer. */
        return !shall_exit;
      });
      if (tooltip_content.length > 0) {
        array[index] = '<div class="tip">'
          + item.replace(/-/g, "") + '<span class="tiptext">'
          + tooltip_content + '</span></div>';
	   }
    }
  });
  return content.join("").replace(/\u0091/g, "");
}


