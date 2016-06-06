$(document).ready(function () {
  window.Upgrade = {
    requested_items: [],
    state: null,
    
    product_upgrade_template:  Handlebars.compile($('#product-upgrade-template').html()),
    $upgrade_list: $('#upgrade-list'),
    $auto_upgrade_warning: $('#auto-upgrade-warning'),


    initial_request: function(){
      if (this.requested_items.length) {
        var req = [];
        for (var i = 0; i < this.requested_items.length; i++) {
          req.push(
            {
              product: this.requested_items[i],
              parameters: {}
            }
          );
        }
        ZooApi.post(ZooApi.Urls.upgrade+'?initial=1', req, Upgrade.upgrade_response);
      }
    },

    upgrade_response: function (response) {
      console.log(response.data);
      if (response.data.task){
        // Upgrade task success started
        Upgrade.go_to_task(response.data.task);
      } else {
        // show Upgrade dialog
        Upgrade.state = response.data.items;
        Upgrade.fill_product_list();
      }
    },

    go_to_task: function(task){
      console.log('Upgrade task created with id', task.id);
      window.location.href = task.url;
    },

    fill_product_list: function () {
      var has_error = false;
      this.$upgrade_list.empty();
      for (var i=0; i<this.state.length; i++){
        var item = this.state[i];
        var html = this.product_upgrade_template(item);
        this.$upgrade_list.append($(html));
        if (item.error){
          has_error = true;
        }
      }

      if (has_error){
        $('#btn-start-upgrade').addClass('disabled').addClass('btn-default').removeClass('btn-success').text('Upgrade unavailable');
      }
    },

    request_upgrade: function(){
      if (this.state.length) {
        var req = [];
        var auto_upgrade = false;
        for (var i = 0; i < this.state.length; i++) {
          var product = this.state[i].product;
          req.push(
            {
              product: product.name,
              parameters: {}
            }
          );

          if (product.name == 'Helicon.Zoo'){
            auto_upgrade = true;
          }
        }

        if (auto_upgrade){
          this.show_auto_upgrade_warning(function(){
            Upgrade.request_upgrade_post(req);
          });
          return;
        }

        this.request_upgrade_post(req);
      }
    },

    request_upgrade_post: function(request){
        console.log('Upgrade request:');
        console.log(request);
        ZooApi.post(ZooApi.Urls.upgrade, request, Upgrade.upgrade_response);
    },

    show_auto_upgrade_warning: function(callback){
      this.$auto_upgrade_warning.modal('show');
      var $ok = this.$auto_upgrade_warning.find('button.ok');
      $ok.off('click');
      $ok.on('click', function(){
        callback();
      });
    },

    init: function () {

      // check request products
      var p = Common.get_query_variable('products');
      if (p){
        this.requested_items = p.split(';');
      }
      if (this.requested_items.length == 0) {
        alert('No products to Upgrade');
        return;
      }

      // initial request with requested products
      this.initial_request();

      // bind clicks
      $('#btn-start-upgrade').click(function(ev){
        Upgrade.request_upgrade();
      });

      this.$auto_upgrade_warning.modal(
        {
          show: false
        }
      )
    }
  };

  window.Upgrade.init();
});

