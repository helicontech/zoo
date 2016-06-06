$(document).ready(function () {
  window.DependencyTree = {
    product_install_template: null,
    selected_dependencies: {},

    render_items_and_add: function(items, $target){
      for(var i=0; i<items.length; i++) {
        var item = items[i];
        item['client_id'] = item['client_id'] || Math.uuid(10);

        if (item.hasOwnProperty('or')) {
          var or_options = item['or'];

          var $or_target = $('<div>').addClass('or').attr('data-select-id', item['client_id']);
          $target.append($or_target);

          for (var j=0; j<or_options.length; j++){
            var or_item = or_options[j];
            or_item['or_option'] = true;
            var $html = this.render_item(or_item);
            $html.hide();
            this.append_item(or_item, $html, $or_target);
            $or_target.find('#select-menu-'+selected_option_client_id).dropdown();
          }

          this.render_select_menu($or_target, or_options);

          var selected_option_client_id = this.get_selected_option_client_id(item['client_id'], or_options);
          $or_target.find('.install-item[data-client-id="'+selected_option_client_id+'"]').show();

        } else {
          // render product node
          var $html = this.render_item(item);
          this.append_item(item, $html, $target);
        }
      }
    },

    render_select_menu: function($target, or_options){
      var $menu = $('<div>'), or_item, client_id;
      for (var j=0; j<or_options.length; j++) {
        or_item = or_options[j];
        client_id = or_item['client_id'];
        $menu.append($('<li>').append($target.find('.install-item[data-client-id="'+client_id+'"]>.install-item-content>.install-item-header').clone()));
      }
      for (var k=0; k<or_options.length; k++) {
        or_item = or_options[k];
        client_id = or_item['client_id'];
        var $dropdown_menu = $target.find('#select-menu-'+client_id).parent().find('>.install-select-menu');
        $dropdown_menu.append($menu.find('>li').clone());
      }
    },

    render_item: function(item){
      item['client_id'] = item['client_id'] || Math.uuid(10);
      var html = this.product_install_template(item);
      return $(html);
    },

    append_item: function(item, $html, $target){
      $target.append($html);
      if (item.hasOwnProperty('and')) {
        // and product dependencies
        this.render_items_and_add(item['and'], $target.find('.install-item[data-client-id="'+item['client_id']+'"]>.install-dependencies'));
      }
    },

    get_selected_option_client_id: function(select_id, or_options){
      if (!this.selected_dependencies[select_id]){
        this.selected_dependencies[select_id] = or_options[0]['client_id'];
      }
      return this.selected_dependencies[select_id];
    },

    dependency_option_selected: function($li){
      var select_id = $li.closest('.or').attr('data-select-id');
      this.selected_dependencies[select_id] = $li.find('[data-client-id]').attr('data-client-id');
    }
  };
});

