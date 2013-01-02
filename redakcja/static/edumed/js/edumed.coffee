
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

      
class Wybor extends Excercise
  constructor: (element) ->
    super element

  check: ->
    scores = []
    $(".question").each (i, question) =>
      scores.push(@check_question question)

    score = [0, 0]
    $.each scores, (i, s) ->
      score[0] += s[0]
      score[1] += s[1]
    @show_score(score)
    
  check_question: (question) ->
    all = 0
    good = 0
    solution = $(question).attr('data-solution').split(',').map($.trim).map((x)->parseInt(x))
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
         
  piece_correct: (qpiece) ->
    $(qpiece).removeClass('incorrect').addClass('correct')

  piece_incorrect: (qpiece) ->
    $(qpiece).removeClass('correct').addClass('incorrect')
    
  show_solutions: ->
    

  show_score: (score) ->
    $(".message", @element).text("Wynik: #{score[0]} / #{score[1]}")
    


##########

excercise = (ele) ->
  es =
    'wybor': Wybor

  cls = es[$(ele).attr('data-type')]
  new cls(ele)


window.edumed =
  'EduModule': EduModule




$(document).ready () ->
  new EduModule($("#book-text"))
  
  $(".excercise").each (i, el) ->
    excercise(this)