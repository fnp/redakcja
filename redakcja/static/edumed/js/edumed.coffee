
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
    $(".question").each (i, question) =>
      scores.push(@check_question question)

    score = [0, 0]
    $.each scores, (i, s) ->
      score[0] += s[0]
      score[1] += s[1]
    @show_score(score)

  get_value_list: (elem, data_key) ->
    $(elem).data(data_key).split(',').map($.trim).map((x) -> parseInt(x))


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
      piece_no = parseInt $(qpiece).attr 'data-no'
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
    positions = @get_value_list(question, 'original')
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



##########

excercise = (ele) ->
  es =
    wybor: Wybor
    uporzadkuj: Uporzadkuj
    luki: Luki
    zastap: Zastap


  cls = es[$(ele).attr('data-type')]
  new cls(ele)


window.edumed =
  'EduModule': EduModule




$(document).ready () ->
  new EduModule($("#book-text"))

  $(".excercise").each (i, el) ->
    excercise(this)