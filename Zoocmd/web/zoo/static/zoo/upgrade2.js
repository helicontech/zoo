$(document).ready(function () {
  window.Upgrade = {

    requested_items: [],
    requested_products_names: [],
    requested_products: [],
    installed_products_names: [],
    installed_products: [],
    task_id: null,//session of logs
    state: null,
    is_install_response_processed: false,
    product_upgrade_template:  Handlebars.compile($('#product-upgrade-template').html()),
    $install_list_products: $('#upgrade-list'),
    $auto_upgrade_warning: $('#auto-upgrade-warning'),

    initial_request: function(){
      if (this.requested_items.length) {
        var req = {
          requested_products: this.requested_items,
          initial: true
        };
        ZooApi.post(ZooApi.Urls.upgrade, req, Upgrade.install_response);
      }
    },

    install_response: function (response) {
      console.log('upgrade response: ');
      console.log(response.data);
      //Upgrade.$response_log.text(JSON.stringify(response.data, null, ' '));
      if (response.data.task){
        // install task success started
        if (response.data.task.id){
           console.log(response.data.task.id);
           Task.task_id = response.data.task.id;
           Upgrade.task_id = response.data.task.id;
           Upgrade.setup_cancel_event(Upgrade.cancel_task, "Cancel");
           Task.init(Upgrade);
           $("#tab-product-list").hide();
           // TODO rework this
           Upgrade.hide_next_button();
           Upgrade.setup_next_event(Upgrade.default_cancel, "Finish");

           $("#tab-pill-list").removeClass("active");
           $("#tab-pill-upgrading").addClass("active");
           $("#tab-product-list").removeClass("active");
           $("#tab-product-upgrading").addClass("active");
           $("#tab-pill-upgrading").show();

           $("#tab-pill-upgrading").attr("id", "tab-installing");

           Status.hide();
       }

      } else {
        // show install dialog
        $("tab-product-list").addClass("active");
        $("#first_tab").removeClass("active");
        $("#tab-pill-upgrading").hide();
        Upgrade.items = response.data.items;
        Upgrade.update();
      }
    },

    update: function(){
      this.is_install_response_processed = false;
      this.process_install_response();
      this.render_product_tree();
    },



    dependency_option_selected: function($li){
      DependencyTree.dependency_option_selected($li);
      this.update();
    },

    render_product_tree: function(){
      this.$install_list_products.empty();
      DependencyTree.render_items_and_add(this.items, this.$install_list_products);
      var arr_title = [];
      for( i in this.items){
        arr_title.push(this.items[i].product.title)

      }
      $("#master_title").html("Upgrading product(s): " + arr_title.join(","))

    },

    process_install_response: function(){
      if (!this.is_install_response_processed){

        // search requested_products and products_has_parameters
        this.get_install_product_list();

        this.is_install_response_processed = true;
      }
    },

    get_install_product_list: function(){
      this.requested_products_names = [];
      this.requested_products = [];
      this.installed_products_names = [];
      this.installed_products = [];

      this._loop_items(this.items);
      console.log('requested product names:', this.requested_products_names);
      console.log('installed product names:', this.installed_products_names);
    },

    _loop_items: function(items, filter_id){
      for(var i=0; i<items.length; i++){
        var item = items[i];
        item['client_id'] = item['client_id'] || Math.uuid(10);

        if (filter_id && item['client_id']!=filter_id){
          continue;
        }

        if (item['product']){
          var product = item['product'];

          // check upgrade is available
          if (!item['can_upgrade'] && !item['last_version']){
            alert('Upgrade is not available for product ' + product['name']);
            $('#btn-start-upgrade').addClass('disabled').addClass('btn-default').removeClass('btn-success').text('Upgrade unavailable');
            return;
          }

          if (product['application']){
            // skip application, accept product and engines only
          } else {
            var product_name = product['name'];
            if ($.inArray(product_name, this.requested_products_names) == -1) {
              if (!item['last_version']  ) {
                // product is not installed
                this.requested_products_names.push(product_name);
                this.requested_products.push(item);
                var parameters = item['parameters'];
                //if (product.hasOwnProperty('parameters') && Object.keys(product.parameters).length > 0) {
                if (parameters && parameters.length > 0) {
                  this.products_has_parameters = true;
                }
              } else {
                // product is installed, save it for install request
                if ($.inArray(product_name, this.installed_products_names) == -1) {
                  this.installed_products_names.push(product_name);
                  this.installed_products.push(item);
                }
              }
            }
          }
        }

        if (item['and']){
          this._loop_items(item['and']);
        }

        if (item['or']){
          var or_options = item['or'];
          for (var j=0; j<or_options.length; j++){
            var or_item = or_options[j];
            or_item['client_id'] = or_item['client_id'] || Math.uuid(10);
          }
          var selected_id = DependencyTree.get_selected_option_client_id(item['client_id'], or_options);
          this._loop_items(or_options, selected_id);
        }
      }
    },

    prepare_install_request: function(){
      var products = [];
      var auto_upgrade = false;
      for(var i=0; i<this.requested_products.length; i++){
        var product_name = this.requested_products[i].product.name;
        products.push(
          {
            product: product_name,
            parameters: null
          }
        );

        if (product_name == 'Helicon.Zoo'){
          auto_upgrade = true;
        }

      }

      var req = {
        install_products: products,
        requested_products: this.requested_items
      };

      if (auto_upgrade){
        this.show_auto_upgrade_warning(function(){
          Upgrade.request_install(req);
        });
        return;
      }


      console.log(req);
      return req;
    },

    request_install: function(req){
      req = req || this.prepare_install_request();
      if (!req){
        return;
      }
      Status.show('Requesting upgrade...');
      if (req.install_products.length){
        ZooApi.post(ZooApi.Urls.upgrade, req, Upgrade.install_response);
      } else {
        Status.hide();
      }
    },
    show_auto_upgrade_warning: function(callback){
      this.$auto_upgrade_warning.modal('show');
      var $ok = this.$auto_upgrade_warning.find('button.ok');
      $ok.off('click');
      $ok.on('click', function(){
        Upgrade.$auto_upgrade_warning.modal('hide');
        callback();
      });
    },


    default_cancel: function(ev){
            var http_referer = Common.get_query_variable('back');
            if(http_referer && http_referer!="false" ){
                     // also you should delete it on server
                  window.location.href=http_referer;
                 return false;
            }else{
                 window.location.href="/gallery/";
                 return false;
            }

    },
    setup_next_event: function(callable, title){
        $("#master-next").unbind("click");
        $("#master-next").bind("click", callable).html(title);
    },
    show_cancel_button: function(){

         $("#master-cancel").show();
    },
    show_next_button: function(){
         $("#master-next").show();
    },
    hide_cancel_button: function(){
         $("#master-cancel").hide();
    },
    hide_next_button: function(){
         $("#master-next").hide();
    },
    setup_cancel_event: function(callable, title){
        $("#master-cancel").unbind("click");
        $("#master-cancel").bind("click", callable).html(title);
    },
    cancel_task: function(ev){
         var http_referer = Common.get_query_variable('back');
         location.href='/cancel_task/' + Upgrade.task_id + "/?back="+http_referer;
    },
    finish: function(TaskObj, Result){
           console.log("Show finish ");
           Upgrade.hide_cancel_button();
           Upgrade.show_next_button();
    },

    init: function () {
      Upgrade.setup_cancel_event(Upgrade.default_cancel, "Cancel");
      // init dependency tree
      DependencyTree.product_install_template = this.product_upgrade_template;
      // check request products
      var p = Common.get_query_variable('products');
      if (p){
        this.requested_items = p.split(';');
      }
      if (this.requested_items.length == 0) {
        alert('No products to upgrade');
        return;
      }

      this.$install_list_products.on('click', '.install-select-menu>li', function(){
        Upgrade.dependency_option_selected($(this));
      });

      // initial request with requested products
      this.initial_request();
      Upgrade.setup_next_event(function(ev){
                               Upgrade.request_install();
                               } ,"Upgrade")


      this.$auto_upgrade_warning.modal(
        {
          show: false
        }
      );
    }
  };

  window.Upgrade.init();
});
