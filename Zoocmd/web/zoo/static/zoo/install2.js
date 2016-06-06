  Install = {
    raw_state:{},
    type:"product",
    title:"",
    requested_items: [],
    requested_products_names: [],
    requested_products: [],
    requested_products_title: [],
    requested_product_parameters:{},
    installed_products_names: [],
    installed_products: [],
    starting: true,
    task_id: null,
    //state -> handler to do
    $modal_dlg: $('#modal-install-confirm'),
    current_state: "",

    selected_engine: null,
    requested_application_prototype: null,
    requested_application_db_types: false,
    requested_application_has_unknown_parameters: false,

    state: null,
    is_install_response_processed: false,
    products_has_parameters: false,
    product_tabs:[
      "tab-pill-list",
      "tab-pill-product-parameters",
      "tab-pill-product-licenses",
      "tab-pill-product-installing"
    ],
    tabs_count:180,
    tabs_classes:{
       'tab-pill-list': "active",
       'tab-pill-product-parameters': "active",
       'tab-pill-product-licenses': "active",
       'tab-pill-product-installing': "pending",
       "tab-pill-appl-website": 'active',
       "tab-pill-appl-settings":'active',
       "tab-pill-appl-database": 'active',
       "tab-pill-appl-installing": 'pending'
    },
    tabs_length:{
       'tab-pill-list': 170,
       'tab-pill-product-parameters': 214,
       'tab-pill-product-licenses': 150,
       'tab-pill-product-installing': 167,
       "tab-pill-appl-website": 150,
       "tab-pill-appl-settings":219,
       "tab-pill-appl-database": 204,
       "tab-pill-appl-installing": 167
    },
    product_pages:[
      "tab-list",
      "tab-product-parameters",
      "tab-product-licenses",
      "tab-product-installing"
    ],
    product_page4state:{
      "start":[],
      "requirements":[],
      "wait_params":[0],
      "wait_licences":[0,1],
      "installing":[0,1,2]
    },
    product_tabs4state:{
      "start":[],
      "requirements":[0],
      "wait_params":[0,1],
      "wait_licences":[0,1,2],
      "installing":[0,1,2,3]
    },
    // for application
    appl_tabs:[
      "tab-pill-appl-website",
      "tab-pill-appl-settings",
      "tab-pill-appl-database",
      "tab-pill-appl-installing"
    ],
    appl_tabs4state:{
      "start":[],
      "website":[0],
      "wait_params":[0,1],
      "wait_database":[0,1,2],
      "installing_application":[0,1,2,3]
    },
    appl_pages:[
      "tab-application",
      "tab-website",
      "tab-application-parameters",
      "tab-database",
      "tab-appl-install"
    ],
    appl_page4state:{
      "start":[],
      "website":[0],
      "wait_params":[0,1],
      "wait_database":[0,1,2],
      "installing_application":[0,1,2,3]
    },


    product_install_template:  Handlebars.compile($('#product-install-template2').html()),
    product_licenses_template:  Handlebars.compile($('#product-licenses-template').html()),
    parameters_template:  Handlebars.compile($('#parameters-template').html()),
    product_install_errors_template: Handlebars.compile($('#product-install-errors').html()),
    $response_log: $('#response-log'),

    //$install_list_application: $('#install-list-application'),
    $install_list_products: $('#install-list-products'),
    $install_list_application: $('#install-list-application'),
    //$install_list: $('#install-list'),
    $product_params_list: $('#product-parameters-list'),
    $application_params_list: $('#application-parameters-list'),

    $install_request_code: $('#install-request-code'),
    $install_request_errors: $('#install-request-errors'),
    $install_request_errors_placeholder: $('#install-request-errors .placeholder'),



    product_master_licenses: function(ev, callback){
        //Install.hide_pages_before(Install.current_state);
        var result_html="";
        Install.setup_next_event(Install.next, "I Agree");
        Install.setup_cancel_event(Install.default_cancel, "Cancel");

        for(var i=0;i<Install.requested_products.length ; i++){
               var item = Install.requested_products[i];
               item['client_id'] = item['client_id'] || Math.uuid(10);
               result_html += Install.product_licenses_template(item);
        }
        $("#product-licenses-list").html(result_html);
        $("#tab-product-licenses").show();
        Install.current_state = "wait_licences";
        callback();
    },
    requested_application:null,
    product_master2install: function(ev){
          return ev;
    },
    cancel_task: function(ev){
         var http_referer = Common.get_query_variable('back');
         location.href='/cancel_task/' + Install.task_id + "/?back="+http_referer;
    },
    master_installing:function(response){
       //Install.hide_pages_before("installing");
       console.log("installing");
       console.log(response);
       $("#finish-task-button").addClass("hidden");
       $("#cancel_button").show();
       Task.clean_log();
       if (response.data.task.id){
           Install.setup_cancel_event(Install.cancel_task, "Cancel");
          // install task success started
           Install.task_id = response.data.task.id;
           Task.init(Install);
           $("#tab-product-installing").show();
           Status.hide();
       } else {
           // show error dialog
           Install.update();
       }
    },
    start_install_application:function(){
        console.log("start application");
        // for  product


        $("#install-pills > a").each(function(index, elem){
                                        $(elem).removeClass("active");
                                    });

        for(i in Install.product_tabs ){
                 $("#"+Install.product_pages[i]).hide();
        }
        Install.current_state = "start";
        $("#tab-pill-product-installing").removeClass("hidden");
        //$("#first_tab_application").addClass("active");
        $("#install-pills-appl").removeClass("hidden");
        $("#tab-application").show();
        Install.appl_next({});
    },
    appl_next: function(ev){
       var Routes = {
        "start": window.Install.appl_master2website_page,
        "website": window.Install.appl_master2params_page,
        "wait_params": window.Install.appl_master2database,
        "wait_database": window.Install.appl_master2install_command
      };
      // console.log(Install.current_state);
      Routes[Install.current_state](ev, function(){
                Install.hide_pages_before(Install.current_state, Install.appl_pages, Install.appl_page4state);
                Install.render_up_buttons_application();
      });

    },

    //default fsm changer
    default_handler: function(State, Page2Show, CallBack){

        Install.current_state = State;
         $("#"+Page2Show).show();
         CallBack();

    },
    //show web site web-master
    appl_master2website_page: function(ev, callback){
       Install.setup_next_event(Install.appl_next, "Next");
       Install.setup_cancel_event(Install.default_cancel, "Cancel");

       if(Install.requested_application["parameters"]){
            var params = Install.requested_application["parameters"];
            var found = Common.search_element_by_key(params, 'name', 'create-site');
            if(found && found["value"]){
                var site_name = Common.search_element_by_key(params, 'name', 'site-name');
                var bindings = Common.search_element_by_key(params, 'name', 'site-binding');
                Websites.set_new_website(site_name["value"], bindings["value"]);
                Websites.new_website_show();
            }
       }
       Install.default_handler("website", "tab-website", callback);
    },
    appl_master2params_page: function(ev, callback){
        Websites.save_selected_site();
        if(Install.requested_application_has_unknown_parameters){
            Install.setup_next_event(Install.appl_next, "Next");
            Install.setup_cancel_event(Install.default_cancel, "Cancel");
            Install.default_handler("wait_params", "tab-application-parameters", callback);
        }else{
            // emulate changing state and clicking the button
            Install.current_state = "wait_params";
            Install.appl_next(ev);

        }

    },
    appl_master2database: function(ev, callback){
            if(Install.requested_application_db_types){

                Install.setup_next_event(Install.appl_next, "Next");
                Install.setup_cancel_event(Install.default_cancel, "Cancel");

                Install.default_handler("wait_database", "tab-database", callback);
            }else{
                Install.current_state = "wait_database";
                Install.appl_next(ev);
            }
    },
    appl_master2install_command: function(ev, callback){

      Status.show('Requesting installation...');
      var req =  Install.prepare_install_application_request();
      Install.current_state = "installing_application";
      req.command = "install";
      // TODO ZooApi.Urls.install -> ZooApi.Urls.install_application

      Install.hide_next_button();
      Install.setup_cancel_event(Install.default_cancel, "Cancel");

      ZooApi.post(ZooApi.Urls.install, req, Install.master_installing);
      callback();

      $("#appl-status-tab").attr("id", "status-tab");
      $("#tab-pill-appl-installing").attr("id", "tab-installing");
      $("#appl-spin-tab").attr("id","icon-spin-tab");

    },
    prepare_install_application_request: function(){
        var products = [];
        var app_name = this.requested_application.product.name;
        products.push({
                      product: app_name,
                      parameters: this.get_application_parameters()}
                     );
        var req = {
         install_products: products,
         requested_products: this.requested_items,
        };
        return req;
    },
    // Install button
    product_master2install_command: function(ev, callback){

      Status.show('Requesting installation...');
      var req =  Install.prepare_install_request();
      Install.current_state = "installing";
      req.command = "install";
      Install.hide_next_button();

      Install.setup_cancel_event(Install.default_cancel, "Cancel");
      ZooApi.post(ZooApi.Urls.install, req, Install.master_installing);
      callback();
      $("#product-status-tab").attr("id", "status-tab");
      $("#tab-pill-product-installing").attr("id", "tab-installing");
      $("#product-spin-tab").attr("id","icon-spin-tab");


    },
    product_master2params_page: function(ev, callback){
        // if there are no request products
        if(Install.requested_products.length == 0 ){
            Install.setup_next_event(Install.next, "Next");
            Install.setup_cancel_event(Install.default_cancel, "Cancel");

            if(Install.requested_application){

                Install.start_install_application();
                return
            }else{
                Install.move_away();
                return
            }
        }else{
            Install.setup_next_event(Install.next, "Next");
            Install.setup_cancel_event(Install.default_cancel, "Cancel");

            Install.current_state = "wait_params";
            console.log(Install.products_has_parameters)
            if(Install.products_has_parameters){
                $("#tab-product-parameters").show();
                callback();
                return ;
            }else{
                //Emulate steping
                Install.current_state = "wait_licences";
                Install.product_master_licenses(ev, callback);
                return
            }
        }

    },
    hide_pages_before:function(State, product_pages, product_page4state ){


        for(var i=0; i<product_page4state[State].length; i++){
            $("#"+product_pages[i]).hide();
        }
    },
//    java script commands to master
    next: function(ev){
       var Routes = {
        "requirements": window.Install.product_master2params_page,
        "wait_params": window.Install.product_master_licenses,
        "wait_licences": window.Install.product_master2install_command
      };

      Routes[Install.current_state](ev, function(){
                Install.hide_pages_before(Install.current_state,
                                          Install.product_pages,
                                          Install.product_page4state);
                Install.render_up_buttons_products();
      });
    },
    default_cancel: function(ev){
         var http_referer = Common.get_query_variable('back');
         if(http_referer && http_referer != "false"){
             // also you should delete it on server
            window.location.href=http_referer;
            return false;
         }else{
            location.href="/gallery/";
            return false;
         }
    },
    finish: function(TaskObj, Result){
           // if we are installing application then
           console.log("Finish event");

           if(Install.requested_application && Result == "done"){
                    // wat it application
                    if(Install.current_state == "installing_application"){
                        //  if it's a finish of installing application
                        Install.setup_next_event(function(){
                                                     if(!Websites.go2selected_website()){
                                                            Install.finish_task();
                                                            return false;
                                                     }
                                     }, "Finish");

                    }else{
                       // master has just installed the deps of application
                       Install.show_cancel_button();
                       Install.setup_cancel_event(Install.default_cancel, "Cancel");
                       Install.setup_next_event(Install.start_install_application, "Install " + Install.name);
                    }

           }else{
                    // master has just installed the common installation
                    Install.setup_next_event(Install.finish_task, "Finish");
           }
           Install.show_next_button();
           Install.hide_cancel_button();


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
    finish_task: function(){
         var http_referer = Common.get_query_variable('back');
         if(http_referer && http_referer != "false" ){
             // also you should delete it on server
            window.location.href=http_referer;
            return false;
         }else{
            window.location.href="/gallery/";
            return false;
         }

    },
    move_away:function(){
            var http_referer = Common.get_query_variable('back');
            if(http_referer && http_referer!="false"){
                     // also you should delete it on server

                  window.location.href=http_referer;
                 return false;
            }else{
                     window.location.href="/gallery/";
                    return false;
            }

    },
// render applications tab in the top

    render_up_buttons_application: function(){
        var i=0;
        for(i=0; i<this.appl_tabs4state[this.current_state].length; i++){
             $("#"+this.appl_tabs[i]).removeClass("active");
        }
        $("#first_tab_application").removeClass("active");
        if(i>0){
            var css_class = this.tabs_classes[ this.appl_tabs[i-1] ];
            console.log(css_class);
            $("#"+this.appl_tabs[i-1]).addClass(css_class);
            $("#"+this.appl_tabs[i-1]).css("display","");
            var tab_length = this.tabs_length[this.product_tabs[i-1]]
            this.tabs_count += tab_length;
            if(this.tabs_count>1000){
                    this.tabs_count -=tab_length;
                    $("#install-pills").css("margin-left", tab_length*-1 + "px");
            }


        }
    },

    render_up_buttons_products: function(){
        var i=0;
        for(i=0; i<this.product_tabs4state[this.current_state].length; i++){
             $("#"+this.product_tabs[i]).removeClass("active");
        }
        $("#first_tab").removeClass("active");
        if(this.current_state == "requirements"){
                    $("#first_tab").addClass("active");
        }
        if(i>0){
            var css_class = this.tabs_classes[ this.product_tabs[i-1] ];
            console.log(css_class);
            $("#"+this.product_tabs[i-1]).addClass(css_class);
            $("#"+this.product_tabs[i-1]).css("display","");
            // there tabs
            var tab_length = this.tabs_length[this.product_tabs[i-1]]
            this.tabs_count += tab_length;
            if(this.tabs_count>1000){
                    this.tabs_count -=tab_length;
                    $("#install-pills").css("margin-left", tab_length*-1 + "px");
            }



        }
    },
    update: function(){

      this.is_install_response_processed = false;
      this.process_install_response();
      this.render_wizard_tabs();
      this.show_errors();

    },
    dependency_option_selected: function($li){
      DependencyTree.dependency_option_selected($li);
      this.update();
    },

    render_product_tree: function(){
      this.$install_list_products.empty();
      DependencyTree.render_items_and_add(this.items, this.$install_list_products);
      // if there is an application
      if(this.requested_application){
        this.$install_list_application.empty();
        DependencyTree.render_items_and_add([this.requested_application], this.$install_list_application);
      }
    },

    fill_product_list: function () {
      var printed_product_names = [];
      this.render_product_tree();
      WizardTabs.$list.find('.actions-bar').slideDown().removeClass('hide-soft');
    },

    fill_product_params: function () {
      this.$product_params_list.empty();
      if (this.products_has_parameters){
        for(var i=0; i<this.requested_products.length; i++){
          var product = this.requested_products[i].product;
          var parameters = this.requested_products[i].parameters;
          if (parameters && parameters.length > 0){
            var html = this.parameters_template(this.requested_products[i]);
            var $html = $(html);
            $html.appendTo(this.$product_params_list);
          }
        }
        this.validate_parameters(WizardTabs.$product_params);
      }
    },


    fill_application_params: function () {
      this.$application_params_list.empty();
      if (this.requested_application){
        var html = this.parameters_template(this.requested_application);
        var $html = $(html);
        $html.appendTo(this.$application_params_list);

        this.validate_parameters(WizardTabs.$application_params);
      }
    },

    fill_database_selector: function(){
      if (this.requested_application_db_types){
            Database.set_engines(this.requested_application_db_types);
            Database.print_engine_options();
      }else{
            // hide not required setting tab
            $("#tab-pill-appl-database").hide();

      }
    },

    render_wizard_tabs: function(){
      this.fill_product_list();
      this.fill_product_params();
      this.fill_database_selector();
      this.fill_application_params();
    },

    process_install_response: function(){
      if (!this.is_install_response_processed){

        WizardTabs.hide_pills();

        // search requested_products and products_has_parameters


        // application must be the first item in list
        var product = this.items[0]['product'];
        if (product && product.hasOwnProperty('application')){



            this.requested_application = this.items[0];
            this.items = this.items[0].and;
            //shortcut
            this.name  = this.requested_application.product.application;
            this.requested_application.and = []
//            break
        }
        // toggle application specific tabs
        if (this.requested_application) {

          // always show web site page
          WizardTabs.show_pill(WizardTabs.$pill_web_site);

          // get database
          var db_types = null;
          if (this.requested_application.product.hasOwnProperty('database_type')){
            db_types = this.requested_application.product.database_type;
            if (db_types && db_types.length > 0) {
              this.requested_application_db_types = db_types;
            }
          }

          if (this.requested_application_db_types){
            WizardTabs.show_pill(WizardTabs.$pill_database);
          }

          this.requested_application_has_unknown_parameters = Object.keys(this.requested_application.product.parameters).length > 0;
          if (this.requested_application_has_unknown_parameters) {
            WizardTabs.show_pill(WizardTabs.$pill_application_params);
          }else{
            // hide not required setting tab
            $("#tab-pill-appl-settings").hide();
          }
        }

        this.get_install_product_list();
        this.is_install_response_processed = true;
        if (this.requested_application){
                $("#master_title").html("Installing application: " + this.requested_application.product.title);

        }else{
              if(this.requested_products_title.length>1){
                   $("#master_title").html("Installing products: " + this.requested_products_title.join(', ')  );
               }else{
                   $("#master_title").html("Installing product: " + this.requested_products_title.join('')  );
               }
        }


      }
    },

    get_install_product_list: function(){
      Install.products_has_parameters = false;
      Install.requested_products_names = [];
      Install.requested_products_title = [];
      Install.requested_products = [];
      Install.installed_products_names = [];
      Install.installed_products = [];
      console.log('items:', Install.items);

      Install._loop_items(Install.items);
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
        console.log("adding product");
        console.log(item);

        if (item['product']){
          var product = item['product'];
          if (product['application']){
            // skip application, accept product and engines only
          } else {
            var product_name = product['name'];
            var product_title = product['title'];
            // раньше была проверка, по которой мы не проверяли продукты-дубли в списке
            // теперь будли оставляем, дальше в апи дубли уберуться
            //if ($.inArray(product_name, this.requested_products_names) == -1) {
              if (!product['installed_version']) {
                // product is not installed


                this.requested_products_names.push(product_name);
                this.requested_products_title.push(product_title);

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
            //}

            // try to save selected engine
            if (product['engine']){
              // save selected engine
              this.selected_engine = product;
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

    show_errors: function(){
      var has_errors = false;
      this.$install_request_errors_placeholder.empty();

      for (var i=0; i<this.items.length; i++) {
        var item = this.items[i];
        if (item.error){
          has_errors = true;
          var html = this.product_install_errors_template(item);
          var $html = $(html);
          $html.appendTo(this.$install_request_errors_placeholder);
        }
      }

      if (has_errors) {
        this.$install_request_errors.slideDown();
      } else {
        this.$install_request_errors.slideUp();
      }
    },

    prepare_install_request: function(){
      var products = [];

      for(var i=0; i<this.requested_products.length; i++){
        var product_name = this.requested_products[i].product.name;
        var product_parameters = this.get_product_parameters(product_name);
        products.push(
          {
            product: product_name,
            parameters: product_parameters
          }
        );
      }


      var req = {
        install_products: products,
        requested_products: this.requested_items,
      };
      console.log(req);
      return req;
    },
    get_product_parameters: function(product_name){
      var params = {};
      var $product_parameters_block = $('.parameter-item[data-product="'+product_name+'"]');
      if ($product_parameters_block.length) {
        $product_parameters_block.find('.form-group').each(function(i, el){
          var $input = $(this).find('[data-parameter]');
          var name = $input.attr('data-parameter');
          params[name] = $input.val();
        });
      }
      return params;
    },
    get_selected_engine: function(){
      if (this.selected_engine){
        return this.selected_engine['name'];
      }
      return null;
    },

    get_application_parameters: function(){
      var params = {};

      if (this.requested_application){
        var website_params = Websites.get_website_parameters();
        $.extend(params, website_params);
      }

      if (this.requested_application_db_types){
        var db_params = Database.get_db_params();
        $.extend(params, db_params);
      }

      if (this.requested_application_has_unknown_parameters){
        var unknown_params = this.get_product_parameters(this.requested_application.product.name);
        $.extend(params, unknown_params);
      }

      var selected_engine = this.get_selected_engine();
      if (selected_engine){
        params['selected-engine'] = selected_engine;
      }

      return params;
    },

    show_install_request: function(){
      var req = this.prepare_install_request();
      this.$install_request_code.text(JSON.stringify(req, null, 2));
    },

    validate_parameters: function($parameters_placeholder){
      var has_empty = false;
      $parameters_placeholder.find('input.parameter-value').each(function(i, el){
        if (!$(el).val()){
          has_empty = true;
        }
      });

      $parameters_placeholder.find('.wizard-next').toggleClass('disabled', has_empty);
    },

    init: function () {

      Install.setup_next_event(Install.default_cancel, "Finish");
      Install.hide_cancel_button();


      // init dependency tree
      DependencyTree.product_install_template = this.product_install_template;

      // start js application tabs and etc
      this.product_master_start();

      this.$install_list_products.on('click', '.install-select-menu>li', function(){
        Install.dependency_option_selected($(this));
      });
      // bind validators
      //checking params on table
      WizardTabs.$product_params.on('change keyup', 'input.parameter-value', function(ev){
        Install.validate_parameters(WizardTabs.$product_params);
      });
      WizardTabs.$application_params.on('change keyup', 'input.parameter-value', function(ev){
        Install.validate_parameters(WizardTabs.$application_params);
      });


    },
    initial_request: function(response){
          Status.hide();
          Install.current_state = response.data.state;
          Install.items = response.data.items;
          Install.data = response.data;
          Install.update();
          if(!Install.products_has_parameters){
            $("#tab-pill-product-parameters").hide();
          }
          Install.setup_next_event(Install.next, "Next");
          Install.show_cancel_button();
          Install.setup_cancel_event(Install.default_cancel, "Cancel");

          $("#first_tab").removeClass("active");
          $("#tab-pill-list").addClass("active");
    },
    is_application:function(){
            var patt = /application/i;
            return patt.test(window.location.href);
    },
    // at first time we use server  like an echo server
    // but if user refresh page we are getting products requested in previous work
    product_master_start: function(){
       // check request products
       // we need avoid of this
        var p = Common.get_query_variable('products');
        var req = '';
        var url = ZooApi.Urls.install;
        if(Install.is_application()){
          Install.requested_items = p.split(';');
          Install.requested_items = [Install.requested_items[0]];
          url = ZooApi.Urls.install_app + Install.requested_items[0];
        }else{
            if (p){
                Install.requested_items = p.split(';');
            }
        }
        req = {
                  "command":"start",
                  "requested_products": Install.requested_items,
        }
        ZooApi.post(url, req, Install.initial_request);



    },


  };




  WizardTabs = {

    $pills: $('#install-pills'),

    $pill_list: $('#tab-pill-list'),
    $pill_product_params: $('#tab-pill-product-parameters'),
    $pill_web_site: $('#tab-pill-web-site'),
    $pill_database: $('#tab-pill-database'),
    $pill_application_params: $('#tab-pill-application-parameters'),
    $pill_install: $('#tab-pill-install'),

    $list: $('#tab-list'),
    $product_params: $('#tab-product-parameters'),
    $web_site: $('#tab-web-site'),
    $database: $('#tab-database'),
    $application_params: $('#tab-application-parameters'),
    $install: $('#tab-install'),

    enable: function($pill){
      $pill.removeClass('disabled');
    },

    show_pill: function($pill){

      $pill.removeClass('hidden');
    },

    hide_pills: function(){
      this.$pills.find('>li').not(':first').not(':last').addClass('hidden');
    },

    get_tab: function($pill){
      return $($pill.find('>a').attr('href'));
    },
    next: function(ev){
      var $active_pill = WizardTabs.$pills.find('>.active');
      var $next_pill = $active_pill.nextAll().filter(':visible:first');

      if ($next_pill.length){
        WizardTabs.enable($next_pill);
        $next_pill.find('>a').tab('show');
        var $tab = WizardTabs.get_tab($next_pill);
        $tab.find('input[type=text]:first').focus();
      }
    },


  };