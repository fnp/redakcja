(function() {
  var $, Binding, EduModule, Excercise, Luki, Uporzadkuj, Wybor, Zastap, excercise,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  $ = jQuery;

  Binding = (function() {

    function Binding(handler, element) {
      this.handler = handler;
      this.element = element;
      $(this.element).data(this.handler, this);
    }

    return Binding;

  })();

  EduModule = (function(_super) {

    __extends(EduModule, _super);

    function EduModule(element) {
      var _this = this;
      EduModule.__super__.constructor.call(this, 'edumodule', element);
      $("[name=teacher-toggle]").change(function(ev) {
        if ($(ev.target).is(":checked")) {
          return $(".teacher", _this.element).addClass("show");
        } else {
          return $(".teacher", _this.element).removeClass("show");
        }
      });
    }

    return EduModule;

  })(Binding);

  Excercise = (function(_super) {

    __extends(Excercise, _super);

    function Excercise(element) {
      var _this = this;
      Excercise.__super__.constructor.call(this, 'excercise', element);
      $(".check", this.element).click(function() {
        return _this.check();
      });
      $('.solutions', this.element).click(function() {
        return _this.show_solutions();
      });
    }

    Excercise.prototype.piece_correct = function(qpiece) {
      return $(qpiece).removeClass('incorrect').addClass('correct');
    };

    Excercise.prototype.piece_incorrect = function(qpiece) {
      return $(qpiece).removeClass('correct').addClass('incorrect');
    };

    Excercise.prototype.check = function() {
      var score, scores,
        _this = this;
      scores = [];
      $(".question").each(function(i, question) {
        return scores.push(_this.check_question(question));
      });
      score = [0, 0];
      $.each(scores, function(i, s) {
        score[0] += s[0];
        return score[1] += s[1];
      });
      return this.show_score(score);
    };

    Excercise.prototype.get_value_list = function(elem, data_key) {
      return $(elem).data(data_key).split(',').map($.trim).map(function(x) {
        return parseInt(x);
      });
    };

    Excercise.prototype.show_score = function(score) {
      return $(".message", this.element).text("Wynik: " + score[0] + " / " + score[1]);
    };

    return Excercise;

  })(Binding);

  Wybor = (function(_super) {

    __extends(Wybor, _super);

    function Wybor(element) {
      Wybor.__super__.constructor.call(this, element);
    }

    Wybor.prototype.check_question = function(question) {
      var all, good, solution,
        _this = this;
      all = 0;
      good = 0;
      solution = this.get_value_list(question, 'solution');
      $(".question-piece", question).each(function(i, qpiece) {
        var is_checked, piece_no, should_be_checked;
        piece_no = parseInt($(qpiece).attr('data-no'));
        should_be_checked = solution.indexOf(piece_no) >= 0;
        is_checked = $("input", qpiece).is(":checked");
        if (should_be_checked) all += 1;
        if (is_checked) {
          if (should_be_checked) {
            good += 1;
            return _this.piece_correct(qpiece);
          } else {
            return _this.piece_incorrect(qpiece);
          }
        } else {
          return $(qpiece).removeClass("correct,incorrect");
        }
      });
      return [good, all];
    };

    Wybor.prototype.show_solutions = function() {};

    return Wybor;

  })(Excercise);

  Uporzadkuj = (function(_super) {

    __extends(Uporzadkuj, _super);

    function Uporzadkuj(element) {
      Uporzadkuj.__super__.constructor.call(this, element);
      $('ol, ul', this.element).sortable({
        items: "> li"
      });
    }

    Uporzadkuj.prototype.check_question = function(question) {
      var all, correct, pkt, pkts, positions, sorted, _ref;
      positions = this.get_value_list(question, 'original');
      sorted = positions.sort();
      pkts = $('.question-piece', question);
      correct = 0;
      all = 0;
      for (pkt = 0, _ref = pkts.length; 0 <= _ref ? pkt < _ref : pkt > _ref; 0 <= _ref ? pkt++ : pkt--) {
        all += 1;
        if (pkts.eq(pkt).data('pos') === sorted[pkt]) {
          correct += 1;
          this.piece_correct(pkts.eq(pkt));
        } else {
          this.piece_incorrect(pkts.eq(pkt));
        }
      }
      return [correct, all];
    };

    return Uporzadkuj;

  })(Excercise);

  Luki = (function(_super) {

    __extends(Luki, _super);

    function Luki(element) {
      Luki.__super__.constructor.call(this, element);
    }

    Luki.prototype.check = function() {
      var all, correct,
        _this = this;
      all = 0;
      correct = 0;
      $(".question-piece", this.element).each(function(i, qpiece) {
        if ($(qpiece).data('solution') === $(qpiece).val()) {
          _this.piece_correct(qpiece);
          correct += 1;
        } else {
          _this.piece_incorrect(qpiece);
        }
        return all += 1;
      });
      return this.show_score([correct, all]);
    };

    return Luki;

  })(Excercise);

  Zastap = (function(_super) {

    __extends(Zastap, _super);

    function Zastap(element) {
      var _this = this;
      Zastap.__super__.constructor.call(this, element);
      $(".paragraph", this.element).each(function(i, par) {
        var spans;
        _this.wrap_words($(par), $('<span class="zastap question-piece"/>'));
        spans = $("> span", par).attr("contenteditable", "true");
        return spans.click(function(ev) {
          spans.filter(':not(:empty)').removeClass('editing');
          return $(ev.target).addClass('editing');
        });
      });
    }

    Zastap.prototype.check = function() {
      var all, correct,
        _this = this;
      all = 0;
      correct = 0;
      $(".question-piece", this.element).each(function(i, qpiece) {
        var should_be_changed, txt;
        txt = $(qpiece).data('original');
        should_be_changed = false;
        if (!(txt != null)) {
          txt = $(qpiece).data('solution');
          should_be_changed = true;
        }
        if (!(txt != null)) return;
        if (should_be_changed) all += 1;
        if (txt !== $(qpiece).text()) {
          return _this.piece_incorrect(qpiece);
        } else {
          if (should_be_changed) {
            _this.piece_correct(qpiece);
            return correct += 1;
          }
        }
      });
      return this.show_score([correct, all]);
    };

    Zastap.prototype.wrap_words = function(element, wrapper) {
      var chld, i, ignore, insertWrapped, j, len, space, wordb, _ref, _results;
      ignore = /^[ \t.,:;()]+/;
      insertWrapped = function(txt, elem) {
        var nw;
        nw = wrapper.clone();
        return $(document.createTextNode(txt)).wrap(nw).parent().attr("data-original", txt).insertBefore(elem);
      };
      _results = [];
      for (j = _ref = element.get(0).childNodes.length - 1; _ref <= 0 ? j <= 0 : j >= 0; _ref <= 0 ? j++ : j--) {
        chld = element.get(0).childNodes[j];
        if (chld.nodeType === document.TEXT_NODE) {
          len = chld.textContent.length;
          wordb = 0;
          i = 0;
          while (i < len) {
            space = ignore.exec(chld.textContent.substr(i));
            if (space != null) {
              if (wordb < i) {
                insertWrapped(chld.textContent.substr(wordb, i - wordb), chld);
              }
              $(document.createTextNode(space[0])).insertBefore(chld);
              i += space[0].length;
              wordb = i;
            } else {
              i = i + 1;
            }
          }
          if (wordb < len - 1) {
            insertWrapped(chld.textContent.substr(wordb, len - 1 - wordb), chld);
          }
          _results.push($(chld).remove());
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };

    return Zastap;

  })(Excercise);

  excercise = function(ele) {
    var cls, es;
    es = {
      wybor: Wybor,
      uporzadkuj: Uporzadkuj,
      luki: Luki,
      zastap: Zastap
    };
    cls = es[$(ele).attr('data-type')];
    return new cls(ele);
  };

  window.edumed = {
    'EduModule': EduModule
  };

  $(document).ready(function() {
    new EduModule($("#book-text"));
    return $(".excercise").each(function(i, el) {
      return excercise(this);
    });
  });

}).call(this);
