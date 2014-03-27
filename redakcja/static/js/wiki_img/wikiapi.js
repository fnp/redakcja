(function($) {
	$.wikiapi = {};
	var noop = function() {
	};
	var noops = {
		success: noop,
		failure: noop
	};
	/*
	 * Return absolute reverse path of given named view. (at least he have it
	 * hard-coded in one place)
	 *
	 * TODO: think of a way, not to hard-code it here ;)
	 *
	 */
	function reverse() {
		var vname = arguments[0];
		var base_path = "/images";

		if (vname == "ajax_document_text") {
			return base_path + "/text/" + arguments[1] + "/";
		}

        if (vname == "ajax_document_revert") {
            return base_path + "/revert/" + arguments[1] + '/';
        }

		if (vname == "ajax_document_history") {
			return base_path + "/history/" + arguments[1] + '/';
		}

		if (vname == "ajax_document_diff")
			return base_path + "/diff/" + arguments[1] + '/';

		if (vname == "ajax_document_pubmark")
			return base_path + "/pubmark/" + arguments[1] + '/';

		console.log("Couldn't reverse match:", vname);
		return "/404.html";
	};

	/*
	 * Document Abstraction
	 */
	function WikiDocument(element_id) {
		var meta = $('#' + element_id);
		this.id = meta.attr('data-object-id');

		this.revision = $("*[data-key='revision']", meta).text();
		this.readonly = !!$("*[data-key='readonly']", meta).text();

        var diff = $("*[data-key='diff']", meta).text();
        if (diff) {
            diff = diff.split(',');
            if (diff.length == 2 && diff[0] < diff[1])
                this.diff = diff;
            else if (diff.length == 1) {
                diff = parseInt(diff);
                if (diff != NaN)
                    this.diff = [diff - 1, diff];
            }
        }

		this.text = null;
		this.has_local_changes = false;
		this._lock = -1;
		this._context_lock = -1;
		this._lock_count = 0;
	};

	WikiDocument.prototype.triggerDocumentChanged = function() {
		$(document).trigger('wlapi_document_changed', this);
	};
	/*
	 * Fetch text of this document.
	 */
	WikiDocument.prototype.fetch = function(params) {
		params = $.extend({}, noops, params);
		var self = this;
		$.ajax({
			method: "GET",
			url: reverse("ajax_document_text", self.id),
			data: {"commit": self.commit},
			dataType: 'json',
			success: function(data) {
				var changed = false;

				if (self.text === null || self.commit !== data.commit) {
					self.text = data.text;
					if (self.text === '') {
					    self.text = '<picture></picture>';
					}
					self.revision = data.revision;
                    self.commit = data.commit;
					changed = true;
					self.triggerDocumentChanged();
				};

				self.has_local_changes = false;
				params['success'](self, changed);
			},
			error: function() {
				params['failure'](self, "Nie udało się wczytać treści dokumentu.");
			}
		});
	};
	/*
	 * Fetch history of this document.
	 *
	 * from - First revision to fetch (default = 0) upto - Last revision to
	 * fetch (default = tip)
	 *
	 */
	WikiDocument.prototype.fetchHistory = function(params) {
		/* this doesn't modify anything, so no locks */
		params = $.extend({}, noops, params);
		var self = this;
		$.ajax({
			method: "GET",
			url: reverse("ajax_document_history", self.id),
			dataType: 'json',
			data: {
				"from": params['from'],
				"upto": params['upto']
			},
			success: function(data) {
				params['success'](self, data);
			},
			error: function() {
				params['failure'](self, "Nie udało się wczytać historii dokumentu.");
			}
		});
	};
	WikiDocument.prototype.fetchDiff = function(params) {
		/* this doesn't modify anything, so no locks */
		var self = this;
		params = $.extend({
			'from': self.revision,
			'to': self.revision
		}, noops, params);
		$.ajax({
			method: "GET",
			url: reverse("ajax_document_diff", self.id),
			dataType: 'html',
			data: {
				"from": params['from'],
				"to": params['to']
			},
			success: function(data) {
				params['success'](self, data);
			},
			error: function() {
				params['failure'](self, "Nie udało się wczytać porównania wersji.");
			}
		});
	};

	/*
	 * Set document's text
	 */
	WikiDocument.prototype.setText = function(text) {
		this.text = text;
		this.has_local_changes = true;
	};

	/*
	 * Save text back to the server
	 */
	WikiDocument.prototype.save = function(params) {
		params = $.extend({}, noops, params);
		var self = this;

		if (!self.has_local_changes) {
			console.log("Abort: no changes.");
			return params['success'](self, false, "Nie ma zmian do zapisania.");
		};

		// Serialize form to dictionary
		var data = {};
		$.each(params['form'].serializeArray(), function() {
			data[this.name] = this.value;
		});

		data['textsave-text'] = self.text;

		$.ajax({
			url: reverse("ajax_document_text", self.id),
			type: "POST",
			dataType: "json",
			data: data,
			success: function(data) {
				var changed = false;

                $('#header').removeClass('saving');

				if (data.text) {
					self.text = data.text;
					self.revision = data.revision;
                    self.commit = data.commit;
					changed = true;
					self.triggerDocumentChanged();
				};

				params['success'](self, changed, ((changed && "Udało się zapisać :)") || "Twoja wersja i serwera jest identyczna"));
			},
			error: function(xhr) {
                if ($('#header').hasClass('saving')) {
                    $('#header').removeClass('saving');
                    $.blockUI({
                        message: "<p>Nie udało się zapisać zmian. <br/><button onclick='$.unblockUI()'>OK</button></p>"
                    })
                }
                else {
                    try {
                        params['failure'](self, $.parseJSON(xhr.responseText));
                    }
                    catch (e) {
                        params['failure'](self, {
                            "__message": "<p>Nie udało się zapisać - błąd serwera.</p>"
                        });
                    };
                }

			}
		});

        $('#save-hide').click(function(){
            $('#header').addClass('saving');
            $.unblockUI();
            $.wiki.blocking.unblock();
        });
	}; /* end of save() */

    WikiDocument.prototype.revertToVersion = function(params) {
        var self = this;
        params = $.extend({}, noops, params);

        if (params.revision >= this.revision) {
            params.failure(self, 'Proszę wybrać rewizję starszą niż aktualna.');
            return;
        }

        // Serialize form to dictionary
        var data = {};
        $.each(params['form'].serializeArray(), function() {
            data[this.name] = this.value;
        });

        $.ajax({
            url: reverse("ajax_document_revert", self.id),
            type: "POST",
            dataType: "json",
            data: data,
            success: function(data) {
                if (data.text) {
                    self.text = data.text;
                    self.revision = data.revision;
                    self.gallery = data.gallery;
                    self.triggerDocumentChanged();

                    params.success(self, "Udało się przywrócić wersję :)");
                }
                else {
                    params.failure(self, "Przywracana wersja identyczna z aktualną. Anulowano przywracanie.");
                }
            },
            error: function(xhr) {
                params.failure(self, "Nie udało się przywrócić wersji - błąd serwera.");
            }
        });
    };

	WikiDocument.prototype.pubmark = function(params) {
		params = $.extend({}, noops, params);
		var self = this;
		var data = {
			"pubmark-id": self.id,
		};

		/* unpack form */
		$.each(params.form.serializeArray(), function() {
			data[this.name] = this.value;
		});

		$.ajax({
			url: reverse("ajax_document_pubmark", self.id),
			type: "POST",
			dataType: "json",
			data: data,
			success: function(data) {
				params.success(self, data.message);
			},
			error: function(xhr) {
				if (xhr.status == 403 || xhr.status == 401) {
					params.failure(self, {
						"__all__": ["Nie masz uprawnień lub nie jesteś zalogowany."]
					});
				}
				else {
					try {
						params.failure(self, $.parseJSON(xhr.responseText));
					}
					catch (e) {
						params.failure(self, {
							"__all__": ["Nie udało się - błąd serwera."]
						});
					};
				};
			}
		});
	};



    WikiDocument.prototype.getImageItems = function(tag) {
        var self = this;

        var parser = new DOMParser();
        var doc = parser.parseFromString(self.text, 'text/xml');
        var error = $('parsererror', doc);

        if (error.length != 0) {
            return null;
        }

        var a = [];
        $('sem[type="'+tag+'"]', doc).each(function(i, e) {
            var $e = $(e);
            var $div = $e.children().first()
            var value = $e.attr(tag);
            $e.find('div').each(function(i, div) {
                var $div = $(div);
                switch ($div.attr('type')) {
                    case 'rect':
                        a.push([
                            value,
                            $div.attr('x1'),
                            $div.attr('y1'),
                            $div.attr('x2'),
                            $div.attr('y2')
                        ]);
                        break;
                    case 'whole':
                        a.push([
                            value,
                            null, null, null, null
                        ]);
                        break
                }
            });
        });

        return a;
    }

    WikiDocument.prototype.setImageItems = function(tag, items) {
        var self = this;

        var parser = new DOMParser();
        var doc = parser.parseFromString(self.text, 'text/xml');
        var serializer = new XMLSerializer();
        var error = $('parsererror', doc);

        if (error.length != 0) {
            return null;
        }

        $('sem[type="'+tag+'"]', doc).remove();
        $root = $(doc.firstChild);
        $.each(items, function(i, e) {
            var $sem = $(doc.createElement("sem"));
            $sem.attr('type', tag);
            $sem.attr(tag, e[0]);
            $div = $(doc.createElement("div"));
            if (e[1]) {
                $div.attr('type', 'rect');
                $div.attr('x1', e[1]);
                $div.attr('y1', e[2]);
                $div.attr('x2', e[3]);
                $div.attr('y2', e[4]);
            }
            else {
                $div.attr('type', 'whole');
            }
            $sem.append($div);
            $root.append($sem);
        });
        self.setText(serializer.serializeToString(doc));
    }


	$.wikiapi.WikiDocument = WikiDocument;
})(jQuery);



// Wykonuje block z załadowanymi kanonicznymi motywami
function withThemes(code_block, onError)
{
    if (typeof withThemes.canon == 'undefined') {
        $.ajax({
            url: '/editor/themes',
            dataType: 'text',
            success: function(data) {
                withThemes.canon = data.split('\n');
                code_block(withThemes.canon);
            },
            error: function() {
                withThemes.canon = null;
                code_block(withThemes.canon);
            }
        })
    }
    else {
        code_block(withThemes.canon);
    }
}

