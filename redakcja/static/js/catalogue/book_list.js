(function($) {
    $(function() {
	// clicking on book checks chunks, too
	$("input[name=select_book]").change(function(ev) {
	    $book = $(this);
	    $book.closest("table").find("input[name=select_chunk][data-book-id=" + $book.val() + "]").attr("checked", $book.is(':checked'));
	    });

	// initialize context menu

	var get_ids = function() {
	    return $.map($("input[name=select_chunk]:checked"), function(ele, idx) {
		return ele.value;
		}).join();
	};

	var set_stage = function(key, opt) {
	    var stage = $("select[name=stage] option[value!=]").eq(key).val();
	    $.post($('input[name=chunk_mass_edit_url]').val(),
		   {
		       ids: get_ids(),
		       stage: stage,
		   },
		   function(data, status) {
		       location.reload(true);
		   }
		  );
	};

	$.contextMenu({
	    selector: '#file-list',
	    items: {
		"stage": { 
		    name: "Set stage",
		    items: $.map($("select[name=stage] option[value!=]"),
				 function(ele, idx) {
				     return { 
					 name: $(ele).text(),
					 callback: set_stage,
				     };
				 }),
		},
/*		"user": { 
		    name: "Set user",

			  },
		"status": { 
		    name: "Set status",
		    items: 
			  },*/

	    },
	});
	
    });
})(jQuery);
