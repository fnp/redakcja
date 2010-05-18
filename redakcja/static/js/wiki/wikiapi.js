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
		var base_path = "/documents";

		if (vname == "ajax_document_text") {
			var path = "/" + arguments[1] + "/text";

		if (arguments[2] !== undefined)
				path += "/" + arguments[2];

			return base_path + path;
		}

		if (vname == "ajax_document_history") {

			return base_path + "/" + arguments[1] + "/history";
		}

		if (vname == "ajax_document_gallery") {

			return base_path + "/gallery/" + arguments[1];
		}

		if (vname == "ajax_document_diff")
			return base_path + "/" + arguments[1] + "/diff";

		if (vname == "ajax_document_addtag")
			return base_path + "/" + arguments[1] + "/tags";

		if (vname == "ajax_publish")
			return base_path + "/" + arguments[1] + "/publish";

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
			error: function() {
				self.galleryImages = [];
				params['failure'](self, "<p>Nie udało się wczytać gallerii pod nazwą: '" + self.galleryLink + "'.</p>");
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
	 * Set document's gallery link
	 */
	WikiDocument.prototype.setGalleryLink = function(gallery) {
		this.galleryLink = gallery;
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

		var metaComment = '<!--';
		metaComment += '\n\tgallery:' + self.galleryLink;
		metaComment += '\n-->\n'

		data['textsave-text'] = metaComment + self.text;

		$.ajax({
			url: reverse("ajax_document_text", self.id),
			type: "POST",
			dataType: "json",
			data: data,
			success: function(data) {
				var changed = false;

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
				try {
					params['failure'](self, $.parseJSON(xhr.responseText));
				}
				catch (e) {
					params['failure'](self, {
						"__message": "<p>Nie udało się zapisać - błąd serwera.</p>"
					});
				};

			}
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

	$.wikiapi.WikiDocument = WikiDocument;
})(jQuery);
