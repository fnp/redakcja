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

    var get_callback = function(form_field_name) {
        var $form = $("#chunk_mass_edit");
        var $field = $("[name=" + form_field_name + "]", $form);
        var $ids_field = $("[name=ids]").val(get_ids());
        var usable_callback = function(value) {
            $field.val(value);
            $ids_field.val(get_ids());
            $.post($form.attr("action"),
               $form.serialize(),
               function(data, status) {
                   location.reload(true);
               }
            );
            return true;
        };
        return usable_callback;
    };

    var get_items = function(field, callback) {
        var d = {};
        $.each($("select[name="+field+"] option[value!=]"),
            function(idx, ele) {
                d[field + "_" + idx] = {
                    name: $(ele).text(), 
                    callback: function() {callback($(ele).attr('value'));}
                };
            });
        return d;
    };

    var user_callback = get_callback('user');
    var users = [
        get_items("user", user_callback),
        {sep: '----'},
        get_items("other-user", user_callback)
    ];
    var current_user_items = user_items = {};
    var i = 0;
    var more_label = $("label[for=mass_edit_more_users]").text();
    for (user_table in users) {
        for (user in users[user_table]) {
            if (i && i % 20 == 0) {
                var more_items = {};
                current_user_items['more'] = {
                    name: more_label,
                    items: more_items
                };
                current_user_items = more_items;
            }
            current_user_items[user] = users[user_table][user];
            i += 1;
        }
    }
    $.contextMenu({
        selector: '#file-list',
        items: {
            stage: { 
                name: $("label[for=mass_edit_stage]").text(),
                items: get_items("stage", get_callback('stage')),
                icon: "clock",
            },
            user: { 
                name: $("label[for=mass_edit_user]").text(),
                items: user_items,
                icon: "user",
            },
            project: {
                name: $("label[for=mass_edit_project]").text(),
                items: get_items("project", get_callback('project')),
            },
        },
    });


    });
})(jQuery);
