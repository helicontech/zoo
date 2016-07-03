$(document).ready(function () {
  window.Grid = {
    remove_button: '<button class="btn btn-default"><i class="fa fa-times text-danger remove"></i></button>',
    template: Handlebars.compile($('#grid-template').html()),
    template_locations: Handlebars.compile($('#grid-template-locations').html()),

    render_edit_values: function(params){
      return this.template({params: params, edit_keys: false, can_add: false});
    },

    render_edit_keys_options_values: function(params, key, selected_key, opts_vals){
      var result = {};
      for(i in params){
            result[params[i][key]] = {'select_vals': opts_vals, 'selected_value': params[i][selected_key] };
      }
      return  this.template_options({params: result, edit_keys: true, can_add: true, 'select_vals': opts_vals });
    },
    // TODO we will that it will works
    process_select_after_render: function(params, key, selected_key_value, func){
          for(i in params){
              var selected_value = params[i][selected_key_value];
              var query_key = 'grid-param-'+params[i][key];
              console.log("set ",query_key," to ",selected_value );
              // We must use straight
              var obj = document.getElementById(query_key);
              obj.setAttribute("data-value", selected_value);
              var formated_val;
              if(func){
                formated_val = func(selected_value);
                obj.innerHTML = formated_val;
              }else{
               obj.innerHTML =selected_value;
              }
          }
    },

    render_edit_keys_values: function(params){
      return this.template({params: params, edit_keys: true, can_add: true});
    },
    render_locations: function(params){
      return this.template_locations({params: params, edit_keys: true, can_add: true});
    },
    // it seems to work
    get_params_opt: function($placeholder, key_field, value_field){
      var params;
      if(key_field && value_field){
        params = [];
      }else{
        params = {};
      }
      $placeholder.find("table tr").each(function(e, e1){
            if($(e1).hasClass("form_add"))
                return;
            var key = $(e1).find("td.editable").text();
            var val = $(e1).find("td.optioneditable").attr("data-value");
            var dict = {};
            dict[key_field] = key;
            dict[value_field] = val;
            params.push(dict);

      });
      return params;
    },
    get_params: function($placeholder){

      var params = {};
      var i=0;
      var last_key;
      $placeholder.find("table tr>td.editable").each(function(e,e1){
                console.log(e1);
                if(i==0){
                  last_key = $(e1).text();
                  i=1;
                  return
                }
                if(i==1){
                  params[last_key]=$(e1).text();
                  i=0;
                  return
                }

      });
      return params;
    },
    connect_events_option: function(selector){
         var editor = $(selector+" tr.form_add td.col2>select").clone();
         var format_function = function(element, value){
              engine =  Gallery.get_engine(value);
              if(engine){
                  element.html(engine.title)
              }else{
                  element.html("Disabled")
              }
              element.attr("data-value", value)

         };
         $(selector + " table").editableTableWidget({"editor": editor,
                                                     "editing_class": "optioneditable",
                                                     "format_function": format_function });


         $(selector).on('click', '.remove', function(e){
             $(this).closest('tr').remove();
         });

         $(selector).on('click', '.add_option', function(e){
            var val1 = $(selector+" tr.form_add td.col1>input").val();
            var val2 = $(selector+" tr.form_add td.col2>select").val();
            if(val1 && val2){
                    var copy = $(selector+" tr.form_add").clone();
                    copy.find("td.col1").addClass("editable").removeClass("col1").html(val1);
                    format_function(copy.find("td.col2").addClass("optioneditable").removeClass("col2"), val2);
                    copy.find("td.add_option").removeClass("add_option").html(Grid.remove_button);
                    copy.on('click', '.remove', function(e){
                        $(this).closest('tr').remove();
                    });
                    copy.removeClass("form_add");
                    copy.insertAfter( selector  + " table tr.form_add" );
                    $(selector + " tr.form_add td.col1>input").val("");
                    $(selector + " tr.form_add td.col2>select").val("");
            }

        });



    },
    connect_events: function(selector, add){
      $(selector + " table").editableTableWidget();
      $(selector).on('click', '.remove', function(e){
        $(this).closest('tr').remove();
      });

      $(selector).on('click', '.add', function(e){
        var val1 = $(selector+" tr.form_add td.col1>input").val();
        var val2 = $(selector+" tr.form_add td.col2>input").val();
        if(val1 && val2){
                var copy = $(selector+" tr.form_add").clone();
                copy.find("td.col1").addClass("editable").html(val1);
                copy.find("td.col2").addClass("editable").html(val2);
                copy.find("td.add").removeClass("add").html(Grid.remove_button);
                copy.on('click', '.remove', function(e){
                    $(this).closest('tr').remove();
                });
                copy.removeClass("form_add");
                copy.insertBefore( selector  + " table tr.form_add" );
                $(selector + " tr.form_add td.col1>input").val("");
                $(selector + " tr.form_add td.col2>input").val("");
        }

      });


    },

    connect_events_locations: function(selector, add){
      $(selector + " table").editableTableWidget();
      $(selector).on('click', '.remove', function(e){
        $(this).closest('tr').remove();
      });

      $(selector).on('click', '.add', function(e){
        var val1 = $(selector+" tr.form_add td.col1>input").val();
        var val2 = $(selector+" tr.form_add td.col2>input").val();
        if(val1 && val2){
                var copy = $(selector+" tr.form_add").clone();
                copy.find("td.col1").addClass("editable").html(val1);
                copy.find("td.col2").addClass("editable").html(val2);
                copy.find("td.add").removeClass("add").html(Grid.remove_button);
                copy.on('click', '.remove', function(e){
                    $(this).closest('tr').remove();
                });
                copy.removeClass("form_add");
                copy.insertAfter( selector  + " table tr.form_add" );
                $(selector + " tr.form_add td.col1>input").val("");
                $(selector + " tr.form_add td.col2>input").val("");
        }

      });


    }

  };

  //window.Grid.init();
});

