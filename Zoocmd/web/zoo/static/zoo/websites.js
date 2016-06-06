$(document).ready(function () {
  window.Websites = {

    $websites_placeholder: $('#websites-placeholder'),
    $websites_template: $('#websites-template'),
    websites_template: null,
    $website_input: $('#website'),
    $app_path_input: $('#app_path'),
    $btn_next: $('#btn-accept-website'),
    $btn_new_website: null,
    $btn_new_website_create: null,
    $group_existing_website: null,
    $new_website_placeholder: null,
    $new_website_error: null,
    $group_existing_app_pool: null,
    $checkbox_new_app_pool: null,
    $app_pool_name: null,

    new_website_name: null,

    is_new_website_state: function(){
      return Websites.$new_website_placeholder.is("[enabled]");
    },

    load: function(){
      ZooApi.get(ZooApi.Urls.website_list, {}, function(resoponse){
        var websites = resoponse.data;
        ZooApi.get(ZooApi.Urls.app_pool_list, {}, function(resoponse){
          var app_pools = resoponse.data;
          Websites.print_websites(websites, app_pools);
        });
      });
    },

    print_websites: function(websites, app_pools){
      var html = this.websites_template({websites: websites, app_pools: app_pools});
      this.$websites_placeholder.html(html);

      this.$website_input = $('#website');
      this.$app_path_input = $('#app_path');
      this.$btn_new_website = $('#btn-new-website');
      this.$btn_new_website_create = $('#btn-new-website-create');
      this.$new_website_placeholder = $('#new-website');
      this.$new_website_error = $('#new-website-error');
      this.$group_existing_website = $('#group-existing-website');
      this.$group_existing_app_pool = $('#group-existing-app-pool');
      this.$checkbox_new_app_pool = $('#checkbox-new-app-pool');
      this.$app_pool_name = $('#app-pool');

      this.select_saved_site();

      if (this.new_website_name){
        this.$website_input.val(this.new_website_name);
        this.new_website_name = null;
        this.validate();
      }
    },

    select_saved_site: function(){
      var site_name = $.cookie('install_site_name');
      var site_path = $.cookie('install_site_path');
      if (site_name){
        this.$website_input.val(site_name).change();
      }
      if (site_path){
        this.$app_path_input.val(site_path).change();
      }
    },
    save_selected_site: function(){

        var website = '';
        var path = '';
        if (Websites.is_new_website_state()){
            var website = Websites.get_new_website();
            website = website.site_name;
            path = Websites.$app_path_input.val();
        }else{
            website = Websites.$website_input.val();
            path = Websites.$app_path_input.val();
        }


          $.cookie('install_site_name', website, {path: '/'});
          $.cookie('install_site_path', path, {path: '/'});
    },
    go2selected_website: function(){
         var site_name = $.cookie('install_site_name');
         var site_path = $.cookie('install_site_path');
         if(!site_name){
            return false;
         }
         var path = site_name + "/"; // + site_path;
         window.location.href = "/server/?path=" + path;
         return true;


    },
    on_show: function(e){
      Websites.$website_input.focus();
    },

    validate: function(e){
      var is_valid = true;

      if (Websites.is_new_website_state()){
        if ($('#new-website-name').val().length==0){
          is_valid = false;
        }
      } else {
        if (Websites.$website_input.val().length==0){
          is_valid = false;
        }
      }

      Websites.$btn_next.toggleClass('disabled', !is_valid);
    },

    get_website_parameters: function(){
      var params = {};
      // web site: existsing or create new
      if (this.is_new_website_state()){
        params['create-site'] = true;

        var website = this.get_new_website();

        params['site-name'] = website.site_name;
        // binding examples:
        // http/*:85:marketing.contoso.com
        // https/192.168.0.1:443

        var bindings =
          website.protocol + '/' +
          website.ip_address + ':' +
          website.port +':' +
          website.hostname;

        params['site-binding'] = bindings;
      } else {
        params['create-site'] = false;
        params['site-name'] = this.$website_input.val();
      }

      // app: empty or create new
      if (this.$app_path_input.val()){
        params['app-name'] = this.$app_path_input.val();
        params['create-app'] = true;
      }

      // app pool default or create new
      if (this.is_new_app_pool_selected()){
        params['create-app-pool'] = true;
      } else {
        params['app-pool-name'] = this.$app_pool_name.val();
      }

      return params;
    },
    new_website_show: function(){

          Websites.$btn_new_website.parent().hide();
          Websites.$new_website_placeholder.show();
          Websites.$group_existing_website.hide();
          Websites.$new_website_placeholder.attr('enabled', 'enabled');

    },
    toggle_new_website: function(e){
      Websites.$btn_new_website.parent().slideToggle();
      Websites.$group_existing_website.slideToggle();

      Websites.$new_website_placeholder.slideToggle(function(){
        if ($('#new-website-name').is(':visible')){
          Websites.$new_website_placeholder.attr('enabled', 'enabled');
          $('#new-website-name').focus();
        } else {
          Websites.$new_website_placeholder.removeAttr('enabled');
        }
      });
      Websites.validate_new_website();

    },

    is_valid_new_website: function(){
      var new_website = Websites.get_new_website();
      return new_website.name && new_website.ip_address && new_website.port;
    },

    validate_new_website: function(e){
      var is_valid = Websites.is_valid_new_website();
      Websites.$btn_new_website_create.toggleClass('disabled', !is_valid);
      if (is_valid){
        Websites.show_new_website_error(null);
      }
    },
    parse_iis_bindings: function(bindings){
        var arr  = bindings.split("/")
        var protocol = arr[0];
        var rest_params = arr[1].split(":");
        var ip = rest_params[0];
        var port = rest_params[1];
        var host = rest_params[2];
        return {"protocol":protocol, "ip": ip, "port":port, "host": host}

    },
    set_new_website: function(name, bindings){
         var params = Websites.parse_iis_bindings(bindings);
         $('#new-website-name').val(name);
         $('#new-website-protocol').val(params["protocol"]);
         $('#new-website-ip-address').val(params["ip"]);
         $('#new-website-port').val(params["port"]);
         $('#new-website-hostname').val(params["host"]);
    },
    get_new_website: function(){
      var website = {};
      website['site_name'] = $('#new-website-name').val();
      website['protocol'] = $('#new-website-protocol').val();
      website['ip_address'] = $('#new-website-ip-address').val();
      website['port'] = $('#new-website-port').val();
      website['hostname'] = $('#new-website-hostname').val();
      return website;
    },

    show_new_website_error: function(msg){
      if (msg){
        this.$new_website_error.text(msg).slideDown();
      } else {
        this.$new_website_error.slideUp();
      }
    },

    /*
    create_new_website: function(e){
      var website = Websites.get_new_website();
      ZooApi.post(ZooApi.Urls.website_create, website, function(response){
        if (response.data.error){
          Websites.show_new_website_error(response.data.error);
        } else {
          Websites.new_website_created(response.data.website);
        }
      });
    },

    new_website_created: function(data){
      this.show_new_website_error(null);
      console.log('new site created: ', data);
      this.new_website_name = data.name;
      this.load();
    },
    */

    is_new_app_pool_selected: function(){
      return this.$checkbox_new_app_pool.is(':checked');
    },

    toggle_new_app_pool: function(ev){
      var is_new_app_pool = Websites.is_new_app_pool_selected();
      Websites.$group_existing_app_pool.slideToggle(is_new_app_pool);
    },

    init: function () {
      this.websites_template = Handlebars.compile(this.$websites_template.html());
      this.load();
      this.$websites_placeholder.on('change keyup', '.form-control', this.validate);
      this.$websites_placeholder.on('click', '#btn-new-website', this.toggle_new_website);
      this.$websites_placeholder.on('change keyup', '#new-website .form-control', this.validate_new_website);
      this.$websites_placeholder.on('click', '#btn-new-website-cancel', this.toggle_new_website);
      //this.$websites_placeholder.on('click', '#btn-new-website-create', this.create_new_website);
      this.$websites_placeholder.on('change', '#checkbox-new-app-pool', this.toggle_new_app_pool);

    }

  };

  window.Websites.init();
});

