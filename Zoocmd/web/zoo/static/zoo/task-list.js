$(document).ready(function () {
  window.TaskList = {
    task_template: null,
    $table:$('#task_list_table'),
    $search_input: $('#product-search-input'),
    js_search: function() {
       var search_text = $("#product-search-input").val().toLocaleLowerCase();
       $("div.search input").val(search_text).keyup();


    },
    init: function () {
      $('#service-menu').find('a[href="/task/"]').parent().addClass('active');
       this.$search_input.keyup(this.js_search );
       this.$table.bootstrapTable({
                onClickRow: function (row) {
                   window.location.href='./'+row.id+"/";
                },
                onLoadSuccess: function (data) {
                    $('[data-toggle="tooltip"]').tooltip({
                      placement : 'bottom'
                    });
                    console.log('Event: onLoadSuccess, data: ' + data);
                },
       });

    }

  };
  window.TaskList.init();
});

