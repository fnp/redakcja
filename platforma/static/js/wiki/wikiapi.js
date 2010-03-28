(function($) {
	
	$.wikiapi = {};
	
	var noop = function() {};
	var noops = {'success': noop, 'failure': noop};
	
	/*
	 * Return absolute reverse path of given named view.
	 * (at least he have it hard-coded in one place)
	 * 
	 * TODO: think of a way, not to hard-code it here ;) 
	 * 
	 */
	function reverse() {
		var vname = arguments[0];
			
		if(vname == "ajax_document_text") {
			var path = "/" + arguments[1] + "/text";
			if (arguments[2] !== undefined) 
				path += "/" + arguments[2];
			return path;
		}
			
		if (vname == "ajax_document_history") {
			return "/" + arguments[1] + "/history";
		}
		
		if (vname == "ajax_document_gallery") {
			return "/gallery/" + arguments[1];
		}						
					
		if(vname == "ajax_document_diff")
			return "/" + arguments[1] + "/diff"; 
			
		console.log("Couldn't reverse match:", vname);
		return "/404.html";		
	};
	
	/*
	 * Document Abstraction  
	 */
	function WikiDocument(element_id) {
		var meta = $('#'+element_id);
		
		this.id = meta.attr('data-document-name');		
		this.revision = $("*[data-key='revision']", meta).text();
		this.galleryLink = $("*[data-key='gallery']", meta).text();
		this.galleryImages = [];
		this.text = null;
		
		this.has_local_changes = false;
		this._lock = -1;
		this._context_lock = -1;
		this._lock_count = 0; 
	}
	
//	WikiDocument.prototype.lock = function() {
//		if(this._lock < 0) {
//			this._lock = Math.random();
//			this._context_lock = this._lock;
//			this._lock_count = 1;
//			return this._lock;
//		}
//		
//		// reentrant locks 
//		if(this._context_lock === this._lock) {
//			this._lock_count += 1;
//			return this._lock;
//		}
//		
//		throw "Document operation in progress. Try again later."
//	};
//		
//	WikiDocument.prototype.unlock = function(lockNumber) {
//		if(this.locked === lockNumber) {
//			this._lock_count -= 1;
//			
//			if(this._lock_count === 0) {
//				this._lock = -1;
//				this._context_lock = -1;
//			};			
//			return;
//		}
//		throw "Trying to unlock with wrong lockNumber";
//	};
//	
//	/*
//	 * About to leave context of current lock.
//	 */
//	WikiDocument.prototype.leaveContext = function() {
//		var old = this._context_lock;
//		this._context_lock = -1;
//		return old;
//	};
	
	/*
	 * Fetch text of this document.
	 */
	WikiDocument.prototype.fetch = function(params) {		
		params = $.extend({}, noops, params);
		var self = this;
		
		$.ajax({
			method: "GET",
			url: reverse("ajax_document_text", self.id),
			dataType: 'json', 
			success: function(data) 
			{
				var changed = false;
				
				if (self.text === null || self.revision !== data.revision) {
					self.text = data.text;
					self.revision = data.revision;
					self.gallery = data.gallery;					
					changed = true;
				}
				
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
	 * from - First revision to fetch (default = 0)
	 * upto - Last revision to fetch (default = tip)
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
			data: {"from": params['from'], "upto": params['upto']},
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
		params = $.extend({
			'from': self.revision, 
			'to': self.revision
		}, noops, params);
					
		var self = this;	
					
		$.ajax({			
			method: "GET",
			url: reverse("ajax_document_diff", self.id),
			dataType: 'json',
			data: {"from": params['from'], "to": params['to']},
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
				this.galleryImages = data.images;
				params['success'](self, data);
			},
			error: function() {
				this.galleryImages = [];	
				params['failure'](self, "<p>Nie udało się wczytać gallerii pod nazwą: '"
					+ self.galleryLink + "'.</p>");
							
			}
		});				
	};	
	
	/*
	 * Set document's text
	 */
	WikiDocument.prototype.setText = function(text) {
		if (this.text != text) {
			this.text = text;
			this.has_local_changes = true;
		}			
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
	WikiDocument.prototype.save = function(params){
		params = $.extend({'comment': 'No comment.'}, noops, params);
		var self = this;
		
		/* you can't set text while some is fetching it (or saving) */
		
		if (!self.has_local_changes) {
			console.log("Abort: no changes.");
			return params['success'](self, false, "Nie ma zmian do zapisania.");
		};		
		
		var metaComment = '<!--';
		metaComment += '\n\tgallery:' + self.galleryLink;
		metaComment += '\n-->\n'
		
		var data = {
			name: self.id,
			text: metaComment + self.text,
			parent_revision: self.revision,
			comment: params['comment'],
		};
		
		$.ajax({
			url: reverse("ajax_document_text", self.id),
			type: "POST",
			dataType: "json",
			data: data,
			success: function(data){
				var changed = false;
				if (data.text) {
					self.text = data.text;
					self.revision = data.revision;
					self.gallery = data.gallery;
					changed = true;
				}
				params['success'](self, changed, "Zapisano");
			},
			error: function() {
				params['failure'](self, "Nie udało się zapisać.");
			}
		});		
	}; /* end of save() */
	
	$.wikiapi.WikiDocument = WikiDocument;
	
})(jQuery);
