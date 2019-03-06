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
		var base_path = "/editor";

		if (vname == "ajax_document_text") {
			var path = "/text/" + arguments[1] + '/';

		if (arguments[2] !== undefined)
				path += arguments[2] + '/';

			return base_path + path;
		}

        if (vname == "ajax_document_revert") {
            return base_path + "/revert/" + arguments[1] + '/';
        }


		if (vname == "ajax_document_history") {

			return base_path + "/history/" + arguments[1] + '/';
		}

		if (vname == "ajax_document_gallery") {

			return base_path + "/gallery/" + arguments[1] + '/';
		}

		if (vname == "ajax_document_diff")
			return base_path + "/diff/" + arguments[1] + '/';

        if (vname == "ajax_document_rev")
            return base_path + "/rev/" + arguments[1] + '/';

		if (vname == "ajax_document_pubmark")
			return base_path + "/pubmark/" + arguments[1] + '/';

		if (vname == "ajax_cover_preview")
			return "/cover/preview/";

		console.log("Couldn't reverse match:", vname);
		return "/404.html";
	};

	/*
	 * Document Abstraction
	 */
	function WikiDocument(element_id) {
		var meta = $('#' + element_id);
		this.id = meta.attr('data-chunk-id');

		this.revision = $("*[data-key='revision']", meta).text();
		this.readonly = !!$("*[data-key='readonly']", meta).text();

		this.galleryLink = $("*[data-key='gallery']", meta).text();
        this.galleryStart = parseInt($("*[data-key='gallery-start']", meta).text());

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
			data: {"revision": self.revision},
			dataType: 'json',
			success: function(data) {
				var changed = false;

				if (self.text === null || self.revision !== data.revision) {
					self.text = data.text;
					self.revision = data.revision;
					self.gallery = data.gallery;
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

    WikiDocument.prototype.checkRevision = function(params) {
        /* this doesn't modify anything, so no locks */
        var self = this;
        $.ajax({
            method: "GET",
            url: reverse("ajax_document_rev", self.id),
            dataType: 'text',
            success: function(data) {
                if (data == '') {
                    if (params.error)
                        params.error();
                }
                else if (data != self.revision)
                    params.outdated();
            }
        });
    };

	/*
	 * Fetch gallery
	 */
	WikiDocument.prototype.refreshGallery = function(params) {
		params = $.extend({}, noops, params);
		var self = this;
		$.ajax({
			method: "GET",
			url: reverse("ajax_document_gallery", self.galleryLink),
			dataType: 'json',
			// data: {},
			success: function(data) {
				self.galleryImages = data;
				params['success'](self, data);
			},
			error: function(xhr) {
                switch (xhr.status) {
                    case 403:
                        var msg = 'Galerie dostępne tylko dla zalogowanych użytkowników.';
                        break;
                    case 404:
                        var msg = "Nie znaleziono galerii o nazwie: '" + self.galleryLink + "'.";
                    default:
                        var msg = "Nie udało się wczytać galerii o nazwie: '" + self.galleryLink + "'.";
                }
				self.galleryImages = [];
				params['failure'](self, "<p>" + msg + "</p>");
			}
		});
	};

	/*
	 * Set document's text
	 */
	WikiDocument.prototype.setText = function(text) {
		return this.setDocumentProperty('text', text);
	};

	/*
	 * Set document's gallery link
	 */
	WikiDocument.prototype.setGalleryLink = function(gallery) {
		return this.setDocumentProperty('galleryLink', gallery);
	};

	/*
	 * Set document's property
	 */
	WikiDocument.prototype.setDocumentProperty = function(property, value) {
		if(this[property] !== value) {
			this[property] = value;
			this.has_local_changes = true;
		}
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
					self.gallery = data.gallery;
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

	WikiDocument.prototype.refreshCover = function(params) {
        var self = this;
		var data = {
			xml: self.text // TODO: send just DC
		};
        $.ajax({
            url: reverse("ajax_cover_preview"),
            type: "POST",
            data: data,
            success: function(data) {
                params.success(data);
            },
            error: function(xhr) {
                // params.failure("Nie udało się odświeżyć okładki - błąd serwera.");
            }
        });
 	};


    WikiDocument.prototype.getLength = function(params) {
        params = $.extend({}, noops, params);
        var xml = this.text.replace(/\/(\s+)/g, '<br />$1');
        var parser = new DOMParser();
        var doc = parser.parseFromString(xml, 'text/xml');
        var error = $('parsererror', doc);

        if (error.length > 0) {
            throw "Not an XML document.";
        }
        $.xmlns["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"; 
        $('rdf|RDF', doc).remove();
        if (params.noFootnotes) {
            $('pa, pe, pr, pt', doc).remove();
        }
	if (params.noThemes) {
	    $('motyw', doc).remove();
        }
        var text = $(doc).text();
        text = $.trim(text.replace(/\s{2,}/g, ' '));
        return text.length;
    }


	$.wikiapi.WikiDocument = WikiDocument;
})(jQuery);
