(function($) {

    	/*
	 * Basic perspective.
	 */
	$.wiki.Perspective = function(options) {
		if(!options) return;

		this.doc = options.doc;
		if (options.id) {
			this.perspective_id = options.id;
		}
		else {
			this.perspective_id = '';
		}

		if(options.callback)
			options.callback.call(this);
	};

	$.wiki.Perspective.prototype.config = function() {
		return $.wiki.state.perspectives[this.perspective_id];
	}

	$.wiki.Perspective.prototype.toString = function() {
	    return this.perspective_id;
	};

	$.wiki.Perspective.prototype.dirty = function() {
		return true;
	};

	$.wiki.Perspective.prototype.onEnter = function () {
		// called when perspective in initialized
		if (!this.noupdate_hash_onenter) {
			document.location.hash = '#' + this.perspective_id;
		}
	};

	$.wiki.Perspective.prototype.onExit = function () {
		// called when user switches to another perspective
		if (!this.noupdate_hash_onenter) {
			document.location.hash = '';
		}
	};

	$.wiki.Perspective.prototype.destroy = function() {
		// pass
	};

	$.wiki.Perspective.prototype.freezeState = function () {
		// free UI state (don't store data here)
	};

	$.wiki.Perspective.prototype.unfreezeState = function (frozenState) {
		// restore UI state
	};

		});

		$elem.show();
		return $elem;
	};

	/*
