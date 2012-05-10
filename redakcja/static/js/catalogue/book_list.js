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
		}).concat(
		    $.map($("input[name=select_book][data-chunk-id!=]:checked"), function(ele, idx) {
			return $(ele).attr("data-chunk-id");
			})).join();
	};
    

	var set_field = function(key, ops) {
            var fds = {}
            fds.stage = "";
            fds.user = "";
            fds.status = "";

	    if (key == "publish" || key == "unpublish") {
		fds["status"] = key;
	    } else {
		var kp = key.split('_');
		var field = kp[0];
		var idx = parseInt(kp[1]);

    		fds[field] = $("select[name="+field+"] option[value!=]").eq(idx).val();
	    }
	    /* fill in the form */
            $("#chunk_mass_edit [name=ids]").val(get_ids());
            for (var fn in fds) {
                $("#chunk_mass_edit [name="+fn+"]").val(fds[fn]);
            }

            $.post($("#chunk_mass_edit").attr("action"),
                   $("#chunk_mass_edit").serialize(),
                   function(data, status) {
                       location.reload(true);
                   }
                  );
            return true;

	    
	};

        var get_items = function(field) {
	    var d = {};
            $.each($("select[name="+field+"] option[value!=]"),
                         function(idx, ele) {
			     d[field+"_"+idx] = { name: $(ele).text() };
			 });
	    return d;
        };


	$.contextMenu({
	    selector: '#file-list',
	    items: {
		"stage": { 
		    name: "Set stage",
		    items: get_items("stage"),
		    icon: "clock",
		},
		"user": { 
		    name: "Set user",
                    items: get_items("user"),
		    icon: "user",
                },
                "publish": {
                    name: "Mark publishable",
		    icon: "ok",
                },
		"unpublish": {
		    name: "Mark not publishable",
		    icon: "stop",
		},
	    },
	    callback: set_field,
	});
	
    });
})(jQuery);
