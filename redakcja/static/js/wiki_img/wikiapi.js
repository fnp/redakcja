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
			var path = "/" + arguments[1] + "/text";

		    if (arguments[2] !== undefined)
				path += "/" + arguments[2];

			return base_path + path;
		}

		/*if (vname == "ajax_document_history") {

			return base_path + "/" + arguments[1] + "/history";
		}
*/
		if (vname == "ajax_document_gallery") {

			return base_path + "/" + arguments[1] + "/gallery";
		}
/*
		if (vname == "ajax_document_diff")
			return base_path + "/" + arguments[1] + "/diff";

        if (vname == "ajax_document_rev")
            return base_path + "/" + arguments[1] + "/rev";

		if (vname == "ajax_document_addtag")
			return base_path + "/" + arguments[1] + "/tags";

		if (vname == "ajax_publish")
			return base_path + "/" + arguments[1] + "/publish";*/

		console.log("Couldn't reverse match:", vname);
		return "/404.html";
	};

	/*
	 * Document Abstraction
	 */
	function WikiDocument(element_id) {
		var meta = $('#' + element_id);
		this.id = meta.attr('data-document-name');

		this.revision = $("*[data-key='revision']", meta).text();
        this.commit = $("*[data-key='commit']", meta).text();
		this.readonly = !!$("*[data-key='readonly']", meta).text();

		this.galleryLink = $("*[data-key='gallery']", meta).text();
		this.galleryImages = [];
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
					    self.text = '<obraz></obraz>';
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

	WikiDocument.prototype.publish = function(params) {
		params = $.extend({}, noops, params);
		var self = this;
		$.ajax({
			url: reverse("ajax_publish", self.id),
			type: "POST",
			dataType: "json",
			success: function(data) {
				params.success(self, data);
			},
			error: function(xhr) {
				if (xhr.status == 403 || xhr.status == 401) {
					params.failure(self, "Nie masz uprawnień lub nie jesteś zalogowany.");
				}
				else {
					try {
						params.failure(self, xhr.responseText);
					}
					catch (e) {
						params.failure(self, "Nie udało się - błąd serwera.");
					};
				};

			}
		});
	};
	WikiDocument.prototype.setTag = function(params) {
		params = $.extend({}, noops, params);
		var self = this;
		var data = {
			"addtag-id": self.id,
		};

		/* unpack form */
		$.each(params.form.serializeArray(), function() {
			data[this.name] = this.value;
		});

		$.ajax({
			url: reverse("ajax_document_addtag", self.id),
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
        $(tag, doc).each(function(i, e) {
            var $e = $(e);
            a.push([
                $e.text(),
                $e.attr('x1'),
                $e.attr('y1'),
                $e.attr('x2'),
                $e.attr('y2')
            ]);
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

        $(tag, doc).remove();
        $root = $(doc.firstChild);
        $.each(items, function(i, e) {
            var el = $(doc.createElement(tag));
            el.text(e[0]);
            if (e[1] !== null) {
                el.attr('x1', e[1]);
                el.attr('y1', e[2]);
                el.attr('x2', e[3]);
                el.attr('y2', e[4]);
            }
            $root.append(el);
        });
        self.setText(serializer.serializeToString(doc));
    }


	$.wikiapi.WikiDocument = WikiDocument;
})(jQuery);
