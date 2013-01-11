
$ = jQuery

class Binding
  constructor: (@handler, @element) ->
    $(@element).data(@handler, this)


class EduModule extends Binding
  constructor: (element) ->
    super 'edumodule', element

    $("[name=teacher-toggle]").change (ev) =>
      if $(ev.target).is(":checked")
        $(".teacher", @element).addClass "show"
      else
        $(".teacher", @element).removeClass "show"


class Excercise extends Binding
  constructor: (element) ->
    super 'excercise', element

    $(".check", @element).click =>
      @check()
    $('.solutions', @element).click =>
      @show_solutions()

  piece_correct: (qpiece) ->
    $(qpiece).removeClass('incorrect').addClass('correct')

  piece_incorrect: (qpiece) ->
    $(qpiece).removeClass('correct').addClass('incorrect')

  check: ->
    scores = []
    $(".question", @element).each (i, question) =>
      scores.push(@check_question question)

    score = [0, 0]
    $.each scores, (i, s) ->
      score[0] += s[0]
      score[1] += s[1]
    @show_score(score)

  get_value_list: (elem, data_key, numbers) ->
    vl = $(elem).attr("data-" + data_key).split(/[ ,]+/).map($.trim) #.map((x) -> parseInt(x))
    if numbers
      vl = vl.map((x) -> parseInt(x))
    return vl

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
    $(".message", @element).text("Wynik: #{score[0]} / #{score[1]}")


class Wybor extends Excercise
  constructor: (element) ->
    super element


  check_question: (question) ->
    all = 0
    good = 0
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
          @piece_incorrect qpiece
      else
        $(qpiece).removeClass("correct,incorrect")

    return [good, all]

  show_solutions: ->


class Uporzadkuj extends Excercise
  constructor: (element) ->
    super element
    $('ol, ul', @element).sortable({ items: "> li" })

  check_question: (question) ->
    positions = @get_value_list(question, 'original', true)
    sorted = positions.sort()
    pkts = $('.question-piece', question)

    correct = 0
    all = 0

    for pkt in [0...pkts.length]
      all +=1
      if pkts.eq(pkt).data('pos') == sorted[pkt]
        correct += 1
        @piece_correct pkts.eq(pkt)
      else
        @piece_incorrect pkts.eq(pkt)
    return [correct, all]


# XXX propozycje="1/0"
class Luki extends Excercise
  constructor: (element) ->
    super element

  check: ->
    all = 0
    correct = 0
    $(".question-piece", @element).each (i, qpiece) =>
      if $(qpiece).data('solution') == $(qpiece).val()
        @piece_correct qpiece
        correct += 1
      else
        @piece_incorrect qpiece
      all += 1

    @show_score [correct, all]


class Zastap extends Excercise
  constructor: (element) ->
    super element
    $(".paragraph", @element).each (i, par) =>
      @wrap_words $(par), $('<span class="zastap question-piece"/>')
      spans = $("> span", par).attr("contenteditable", "true")
      spans.click (ev) =>
        spans.filter(':not(:empty)').removeClass('editing')
        $(ev.target).addClass('editing')


  check: ->
    all = 0
    correct = 0
    $(".question-piece", @element).each (i, qpiece) =>
      txt = $(qpiece).data('original')
      should_be_changed = false
      if not txt?
        txt = $(qpiece).data('solution')
        should_be_changed = true
      if not txt?
        return

      if should_be_changed
        all += 1

      if txt != $(qpiece).text()
        @piece_incorrect qpiece
      else
        if should_be_changed
          @piece_correct qpiece
          correct += 1

    @show_score [correct, all]

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


class Przyporzadkuj extends Excercise
  is_multiple: ->
    for qp in $(".question-piece", @element)
      if $(qp).data('solution').split(/[ ,]+/).length > 1
        return true
    return false

  constructor: (element) ->
    super element

    @multiple = @is_multiple()

    $(".question", @element).each (i, question) =>
      draggable_opts =
        revert: 'invalid'
      if @multiple
        helper_opts = { helper: "clone" }
      else helper_opts = {}

      $(".draggable", question).draggable($.extend({}, draggable_opts,
        helper_opts))

      $(".predicate .droppable", question).droppable
        accept: (draggable) ->
          $draggable = $(draggable)
          if not $draggable.is(".draggable")
            return false
          $predicate = $(this)

          for added in $predicate.find("li")
            if $(added).text() == $draggable.text()
              return false
          return true

        drop: (ev, ui) =>
          added = ui.draggable.clone()

          added.attr('style', '')
          $(ev.target).append(added)
          added.draggable(draggable_opts)

          if not @multiple or ui.draggable.closest(".predicate").length > 0
            ui.draggable.remove()


      $(".subject", question).droppable
        accept: ".draggable"
        drop: (ev, ui) =>
          # this is to prevent a situation of dragging out and
          # dropping back to the same place
          if $(ui.draggable).closest(".subject").length > 0
            return


          added = ui.draggable.clone()

          added.attr('style', '')
          if not @multiple
            $(ev.target).append(added)
            added.draggable($.extend({}, draggable_opts, helper_opts))

          ui.draggable.remove()

  check_question: (question) ->
    # subjects placed in predicates
    count = 0
    all = 0
    all_multiple = 0
    for qp in $(".predicate .question-piece", question)
      pred = $(qp).closest("[data-predicate]")
      v = @get_value_optional_list qp, 'solution'
      mandatory = v[0]
      optional = v[1]
      all_multiple += mandatory.length + optional.length
      pn = pred.data('predicate')
      if mandatory.indexOf(pn) >= 0 or optional.indexOf(pn) >= 0
        count += 1
        @piece_correct qp
      else
        @piece_incorrect qp
      all += 1

    if @multiple
      for qp in $(".subject .question-piece", question)
        v = @get_value_optional_list qp, 'solution'
        mandatory = v[0]
        optional = v[1]
        all_multiple += mandatory.length + optional.length
      return [count, all_multiple]
    else
      return [count, all]






##########

excercise = (ele) ->
  es =
    wybor: Wybor
    uporzadkuj: Uporzadkuj
    luki: Luki
    zastap: Zastap
    przyporzadkuj: Przyporzadkuj


  cls = es[$(ele).attr('data-type')]
  new cls(ele)


window.edumed =
  'EduModule': EduModule




$(document).ready () ->
  new EduModule($("#book-text"))

  $(".excercise").each (i, el) ->
    excercise(this)