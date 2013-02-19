
$ = jQuery

class Binding
  constructor: (@handler, @element) ->
    $(@element).data(@handler, this)


class EduModule extends Binding
  constructor: (element) ->
    super 'edumodule', element

    # $("[name=teacher-toggle]").change (ev) =>
    #   if $(ev.target).is(":checked")
    #     $(".teacher", @element).addClass "show"
    #   else
    #     $(".teacher", @element).removeClass "show"


class Exercise extends Binding
  constructor: (element) ->
    super 'exercise', element
    # just save the html to reset the exercise
    $(@element).data("exercise-html", $(@element).html())

    $(".check", @element).click (ev) =>
      @check()
      $(".retry", @element).show()
      $(".check", @element).hide()
    $(".retry", @element).click (ev) =>
      @retry()
    $('.solutions', @element).click =>
      @show_solutions()
      $(".comment", @element).show()
    $('.reset', @element).click =>
      @reset()

  retry: ->
    $(".correct, .incorrect", @element).removeClass("correct incorrect")
    $(".check", @element).show()
    $(".retry", @element).hide()

  reset: ->
    $(@element).html($(@element).data('exercise-html'))
    exercise @element

  piece_correct: (qpiece) ->
    $(qpiece).removeClass('incorrect').addClass('correct')

  piece_incorrect: (qpiece) ->
    $(qpiece).removeClass('correct').addClass('incorrect')

  check: ->
    scores = []
    $(".question", @element).each (i, question) =>
      scores.push(@check_question question)

    score = [0, 0, 0]
    $.each scores, (i, s) ->
      score[0] += s[0]
      score[1] += s[1]
      score[2] += s[2]
    @show_score(score)

  show_solutions: ->
    @reset()
    $(".question", @element).each (i, question) =>
      @solve_question question

  # Parses a list of values, separated by space or comma.
  # The list is read from data attribute of elem using data_key
  # Returns a list with elements
  # eg.: things_i_need: "house bike tv playstation"
  # yields ["house", "bike", "tv", "playstation"]
  # If optional numbers argument is true, returns list of numbers
  # instead of strings
  get_value_list: (elem, data_key, numbers) ->
    vl = $(elem).attr("data-" + data_key).split(/[ ,]+/).map($.trim) #.map((x) -> parseInt(x))
    if numbers
      vl = vl.map((x) -> parseInt(x))
    return vl

  # Parses a list of values, separated by space or comma.
  # The list is read from data attribute of elem using data_key
  # Returns a 2-element list with mandatory and optional
  # items. optional items are marked with a question mark on the end
  # eg.: things_i_need: "house bike tv? playstation?"
  # yields [[ "house", "bike"], ["tv", "playstation"]]
  get_value_optional_list: (elem, data_key) ->
    vals = @get_value_list(elem, data_key)
    mandat = []
    opt = []
    for v in vals
      if v.slice(-1) == "?"
        opt.push v.slice(0, -1)
      else
        mandat.push v
    return [mandat, opt]

  show_score: (score) ->
    $msg = $(".message", @element)
    $msg.text("Wynik: #{score[0]} / #{score[2]}")
    if score[0] >= score[2] and score[1] == 0
      $msg.addClass("maxscore")
    else
      $msg.removeClass("maxscore")


  draggable_equal: ($draggable1, $draggable2) ->
    return false

  draggable_accept: ($draggable, $droppable) ->
    dropped = $droppable.closest("ul, ol").find(".draggable")
    for d in dropped
      if @draggable_equal $draggable, $(d)
        return false
    return true

  draggable_move: ($draggable, $placeholder, ismultiple) ->
    $added = $draggable.clone()
    $added.data("original", $draggable.get(0))
    if not ismultiple
      $draggable.addClass('disabled').draggable('disable')

    $placeholder.after($added)
    if not $placeholder.hasClass('multiple')
      $placeholder.hide()
    if $added.is(".add-li")
      $added.wrap("<li/>")

    $added.append('<span class="remove">x</span><div class="clr"></div>')
    $('.remove', $added).click (ev) =>
      @retry()
      if not ismultiple
        $($added.data('original')).removeClass('disabled').draggable('enable')

      if $added.is(".add-li")
        $added = $added.closest('li')
      $added.prev(".placeholder:not(.multiple)").show()
      $added.remove()


## XXX co z issortable?
  dragging: (ismultiple, issortable) ->
    $(".question", @element).each (i, question) =>
      draggable_opts =
        revert: 'invalid'
        helper: 'clone'
        start: @retry

      $(".draggable", question).draggable(draggable_opts)
      self = this
      $(".placeholder", question).droppable
        accept: (draggable) ->
          $draggable = $(draggable)
          is_accepted = true

          if not $draggable.is(".draggable")
            is_accepted = false

          if is_accepted
            is_accepted= self.draggable_accept $draggable, $(this)

          if is_accepted
            $(this).addClass 'accepting'
          else
            $(this).removeClass 'accepting'
          return is_accepted

        drop: (ev, ui) =>
          $(ev.target).removeClass 'accepting dragover'

          @draggable_move $(ui.draggable), $(ev.target), ismultiple

          # $added = $(ui.draggable).clone()
          # $added.data("original", ui.draggable)
          # if not ismultiple
          #   $(ui.draggable).addClass('disabled').draggable('disable')

          # $(ev.target).after(added)
          # if not $(ev.target).hasClass('multiple')
          #   $(ev.target).hide()
          # $added.append('<span class="remove">x</span>')
          # $('.remove', added).click (ev) =>
          #   $added.prev(".placeholder:not(.multiple)").show()
          #   if not ismultiple
          #     $added.data('original').removeClass('disabled').draggable('enable')
          #   $(added).remove()

        over: (ev, ui) ->
          $(ev.target).addClass 'dragover'


        out: (ev, ui) ->
          $(ev.target).removeClass 'dragover'



class Wybor extends Exercise
  constructor: (element) ->
    super element
    $(".question-piece input", element).change(@retry);


  check_question: (question) ->
    all = 0
    good = 0
    bad = 0
    solution = @get_value_list(question, 'solution')
    $(".question-piece", question).each (i, qpiece) =>
      piece_no = $(qpiece).attr 'data-no'
      piece_name = $(qpiece).attr 'data-name'
      if piece_name
        should_be_checked = solution.indexOf(piece_name) >= 0
      else
        should_be_checked = solution.indexOf(piece_no) >= 0
      is_checked = $("input", qpiece).is(":checked")

      if should_be_checked
        all += 1

      if is_checked
        if should_be_checked
          good += 1
          @piece_correct qpiece
        else
          bad += 1
          @piece_incorrect qpiece
      else
        $(qpiece).removeClass("correct,incorrect")

    return [good, bad, all]

  solve_question: (question) ->
    solution = @get_value_list(question, 'solution')
    $(".question-piece", question).each (i, qpiece) =>
      piece_no = $(qpiece).attr 'data-no'
      piece_name = $(qpiece).attr 'data-name'
      if piece_name
        should_be_checked = solution.indexOf(piece_name) >= 0
      else
        should_be_checked = solution.indexOf(piece_no) >= 0
      console.log("check " + $("input[type=checkbox]", qpiece).attr("id") + " -> " + should_be_checked)
      $("input[type=checkbox],input[type=radio]", qpiece).prop 'checked', should_be_checked



class Uporzadkuj extends Exercise
  constructor: (element) ->
    super element
    $('ol, ul', @element).sortable({ items: "> li", start: @retry })

  check_question: (question) ->
    positions = @get_value_list(question, 'original', true)
    sorted = positions.sort()
    pkts = $('.question-piece', question)

    correct = 0
    bad = 0
    all = 0

    for pkt in [0...pkts.length]
      all += 1
      if pkts.eq(pkt).data('pos') == sorted[pkt]
        correct += 1
        @piece_correct pkts.eq(pkt)
      else
        bad += 1
        @piece_incorrect pkts.eq(pkt)
    return [correct, bad, all]

  solve_question: (question) ->
    positions = @get_value_list(question, 'original', true)
    sorted = positions.sort()
    pkts = $('.question-piece', question)
    pkts.sort (a, b) ->
      q = $(a).data('pos')
      w = $(b).data('pos')
      return 1 if q < w
      return -1 if q > w
      return 0

    parent = pkts.eq(0).parent()
    for p in pkts
      parent.prepend(p)


# XXX propozycje="1/0"
class Luki extends Exercise
  constructor: (element) ->
    super element
    @dragging false, false

  check: ->
    all = $(".placeholder", @element).length
    correct = 0
    bad = 0
    $(".placeholder + .question-piece", @element).each (i, qpiece) =>
      $placeholder = $(qpiece).prev(".placeholder")
      if $placeholder.data('solution') == $(qpiece).data('no')
        @piece_correct qpiece
        correct += 1
      else
        bad += 1
        @piece_incorrect qpiece

    @show_score [correct, bad, all]

  solve_question: (question) ->
    $(".placeholder", question).each (i, placeholder) =>
      $qp = $(".question-piece[data-no=" + $(placeholder).data('solution') + "]", question)
      @draggable_move $qp, $(placeholder), false


class Zastap extends Exercise
  constructor: (element) ->
    super element
    $(".paragraph", @element).each (i, par) =>
      @wrap_words $(par), $('<span class="placeholder zastap"/>')
    @dragging false, false

  check: ->
    all = 0
    correct = 0
    bad = 0

    $(".paragraph", @element).each (i, par) =>
      $(".placeholder", par).each (j, qpiece) =>
        $qp = $(qpiece)
        $dragged = $qp.next(".draggable")
        if $qp.data("solution")
          if $dragged and $qp.data("solution") == $dragged.data("no")
            @piece_correct $dragged
            correct += 1
#          else -- we dont mark enything here, so not to hint user about solution. He sees he hasn't used all the draggables

          all += 1

    @show_score [correct, bad, all]

  show_solutions: ->
    @reset()
    $(".paragraph", @element).each (i, par) =>
      $(".placeholder[data-solution]", par).each (j, qpiece) =>
        $qp = $(qpiece)
        $dr = $(".draggable[data-no=" + $qp.data('solution') + "]", @element)
        @draggable_move $dr, $qp, false


  wrap_words: (element, wrapper) ->
    # This function wraps each word of element in wrapper, but does not descend into child-tags of element.
    # It doesn't wrap things between words (defined by ignore RE below). Warning - ignore must begin with ^
    ignore = /^[ \t.,:;()]+/

    insertWrapped = (txt, elem) ->
      nw = wrapper.clone()
      $(document.createTextNode(txt))
        .wrap(nw).parent().attr("data-original", txt).insertBefore(elem)

    for j in [element.get(0).childNodes.length-1..0]
      chld = element.get(0).childNodes[j]
      if chld.nodeType == document.TEXT_NODE
        len = chld.textContent.length
        wordb = 0
        i = 0
        while i < len
          space = ignore.exec(chld.textContent.substr(i))
          if space?
            if wordb < i
              insertWrapped(chld.textContent.substr(wordb, i-wordb), chld)

            $(document.createTextNode(space[0])).insertBefore(chld)
            i += space[0].length
            wordb = i
          else
            i = i + 1
        if wordb < len - 1
          insertWrapped(chld.textContent.substr(wordb, len - 1 - wordb), chld)
        $(chld).remove()


class Przyporzadkuj extends Exercise
  is_multiple: ->
    for qp in $(".question-piece", @element)
      if $(qp).attr('data-solution').split(/[ ,]+/).length > 1
        return true
    return false

  constructor: (element) ->
    super element

    @multiple = @is_multiple()

    @dragging @multiple, true

  draggable_equal: (d1, d2) ->
    return d1.data("no") == d2.data("no")


  check_question: (question) ->
    # subjects placed in predicates
    minimum = $(question).data("minimum")
    count = 0
    bad_count = 0
    all = 0
    if not minimum
      self = this
      $(".subject .question-piece", question).each (i, el) ->
        v = self.get_value_optional_list el, 'solution'
        mandatory = v[0]
        all += mandatory.length

    for pred in $(".predicate [data-predicate]", question)
      pn = $(pred).attr('data-predicate')
      #if minimum?
      #  all += minimum

      for qp in $(".question-piece", pred)
        v = @get_value_optional_list qp, 'solution'
        mandatory = v[0]
        optional = v[1]

        if mandatory.indexOf(pn) >= 0 or (minimum and optional.indexOf(pn) >= 0)
          count += 1
          @piece_correct qp
        else
          bad_count += 1
          @piece_incorrect qp

    return [count, bad_count, all]

  solve_question: (question) ->
    minimum = $(question).data("min")

    for qp in $(".subject .question-piece", question)
      v = @get_value_optional_list qp, 'solution'
      mandatory = v[0]
      optional = v[1]

      if minimum
        draggables = mandatory.count(optional)[0...minimum]
      else
        draggables = mandatory
      for m in draggables
        $pr = $(".predicate [data-predicate=" + m + "]", question)
        $ph = $pr.find ".placeholder:visible"
        @draggable_move $(qp), $ph.eq(0), @multiple



class PrawdaFalsz extends Exercise
  constructor: (element) ->
    super element

    for qp in $(".question-piece", @element)
      $(".true", qp).click (ev) =>
        ev.preventDefault()
        @retry()
        $(ev.target).closest(".question-piece").data("value", "true")
        $(ev.target).addClass('chosen').siblings('a').removeClass('chosen')
      $(".false", qp).click (ev) =>
        ev.preventDefault()
        @retry()
        $(ev.target).closest(".question-piece").data("value", "false")
        $(ev.target).addClass('chosen').siblings('a').removeClass('chosen')


  check_question: ->
    all = 0
    good = 0
    bad = 0
    for qp in $(".question-piece", @element)
      if $(qp).data("solution").toString() == $(qp).data("value")
        good += 1
        @piece_correct qp
      else
        bad += 1
        @piece_incorrect qp

      all += 1

    return [good, bad, all]

  show_solutions: ->
    @reset()
    for qp in $(".question-piece", @element)
      if $(qp).data('solution') == true
        $(".true", qp).click()
      else
        $(".false", qp).click()


##########

exercise = (ele) ->
  es =
    wybor: Wybor
    uporzadkuj: Uporzadkuj
    luki: Luki
    zastap: Zastap
    przyporzadkuj: Przyporzadkuj
    prawdafalsz: PrawdaFalsz


  cls = es[$(ele).attr('data-type')]
  new cls(ele)


window.edumed =
  'EduModule': EduModule




$(document).ready () ->
  new EduModule($("#book-text"))

  $(".exercise").each (i, el) ->
    exercise(this)
