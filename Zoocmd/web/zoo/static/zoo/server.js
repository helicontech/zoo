$(document).ready(function () {
  window.Server = {

    app_template: Handlebars.compile($('#server-zoo-app-template').html()),
    parent_app_template: Handlebars.compile($('#server-parent-app-template').html()),
    engine_app_template: Handlebars.compile($('#server-engine-template').html()),
    engines_list_dropdown_template: Handlebars.compile($('#server-engine-list-template').html()),
    $server_controls: $('#server-controls .server-control'),
    $engines_placeholder: $('#engines-placeholder'),
    $selected_engine_placeholder: $('#selected_engine_placeholder'),
    $zoo_app_placeholder: $('#zoo-app-placeholder'),
    $zoo_parent_app_placeholder: $('#zoo-parent-app-placeholder'),
    $zoo_app: $('#zoo-app'),
    $no_app_placeholder: $('#no-app-placeholder'),
    selected_engine: null,
    current_node: null,
    hide_controls: function(){
      this.$server_controls.slideUp();
    },

    show_active_control: function(){
      this.$server_controls.not('.active').hide();
      this.$server_controls.filter('.active').fadeIn();
    },

    print_browse_links: function(){
      var $browse_links = this.$server_controls.filter('.active').find('.browse-links');
      var $link_list = $browse_links.find('ul');
      var node = this.current_node;
      if (node.type == 'server'){
        return;
      }

      var site_name = this._get_site_name(node.path);
      var site_node = ServerTree.cache[site_name];
      var urls = site_node.urls;
      var site_path = node.path.replace(site_name, '');

      $link_list.empty();
      for(var i=0; i<urls.length; i++){
        var url = urls[i] + site_path;
//        $link_list.append($('<li><a target="_blank" onClick="doSomething()" href="javascript:Server.open_site(\''+site_name+'\', \''+url+'\')">'+url+'</a></li>'));

        $link_list.append($('<li><a onClick="return Server.open_site(\''+site_name+'\', \''+url+'\')" target="_blank" onClick="doSomething()" href="'+url+'">'+url+'</a></li>'));
      }
    },
    open_site:function(site_name, location){

         if(site_name.substr(-1) === '/') {
               site_name = site_name.substr(0, site_name.length - 1);
         }
         ZooApi.post(
                ZooApi.Urls.site_launch,
                {"sitename": site_name, "url": location},
                function(response){
                    console.log(response.data.status);
                });
         return true
    },
    _get_site_name: function(path){
      var slash_index = path.indexOf('/');
      if (slash_index > 0){
        return path.substr(0, slash_index+1);
      }
      return path;
    },

        //$
    save_environment_variables: function(engine_name){
            var engine_settings = Common.search_element_by_key(this.application.engines,'engine', engine_name );
            engine_settings.environment_variables = Grid.get_params(Server.$zoo_app.find('#app-environment'));

    },
    set_selected_engine: function(EngineName){
           var engine =  Gallery.get_engine(EngineName);
           var title = '';
           if(engine){
                title = engine.title;
           }else{
                title = EngineName;

           }
           var prev_selected_engine = Server.selected_engine;
           // changing engines for locations locations
           $("#app-location table tr td.col2").each(function(e, e1){
                var prev_engine = $(e1).text();
                if(prev_engine == prev_selected_engine){
                      $(e1).text(EngineName);
                }
           });

           Server.selected_engine = EngineName;
           $("#engine").text( title );



           Server.app_engine_change();
    },
    app_engine_change: function(){

        var engine_settings = Common.search_element_by_key(this.application.engines,'engine',
                                                           this.selected_engine );

        var environment_variables = engine_settings.environment_variables;
        Server.$zoo_app.find('#app-environment').html(Grid.render_edit_keys_values(environment_variables || []));

        var engine = Gallery.get_engine(this.selected_engine);



        var compiled_html = Server.engine_app_template(engine);
        // we are not able to use Server.$select cause this placeholder is nested into template
        $("#selected_engine_placeholder").html(compiled_html);

        $("#selected_engine_placeholder").on('click', '.btn-engine-properties', function(e){
                e.preventDefault();
                var engine = Gallery.get_parent_product_for_control($(this));
                Engine.show(engine);

        });


      var list = []
      for(i in this.application.engines){
          var engine = Gallery.get_engine(this.application.engines[i].engine)
          if(engine)
            list.push(engine)
      }

       compiled_html = Server.engines_list_dropdown_template({"engines":list});
       $("#engine-dropdown-placeholder").html(compiled_html);
       Grid.connect_events("#app-environment");

    },
    show_zoo_app: function($node, node){
          var html = this.app_template({node: node});

          var $z = this.$zoo_app;
          $z.html(html);

          $z.find('#path').val(node.config.path);
          var application = node.config.application;
          var pre_sel_vals = application['engines'];
          this.application = application;

          var select_vals = []
          select_vals.push({'value':'none', 'title': 'Disabled' })
          for(i in pre_sel_vals){
            var engine = Gallery.get_engine(pre_sel_vals[i].engine);
            var title;
            if(!engine){
                //ErrorMessage.show_html("I can't find engine "+pre_sel_vals[i].engine)
                //title = pre_sel_vals[i].engine;
                continue
            }else{
                title = engine.title;
            }
            select_vals.push({'value': pre_sel_vals[i].engine,
                              'title': title })
          }
          var locations = application['locations'] || [];
          var params = {};
          for(i in locations){
             params[locations[i]['path']] = locations[i]['engine'];
          }
          $z.find('#app-location').html(Grid.render_locations(params));
          Grid.connect_events_locations("#app-location");
          //Grid.connect_events_option("#app-location");
          if(!application.parameters)
                application.parameters = {'selected-engine': pre_sel_vals[0].engine};

          if(!application.parameters['selected-engine']){
                 application.parameters['selected-engine'] = pre_sel_vals[0].engine;
          }

          this.set_selected_engine(application.parameters['selected-engine']);
          this.$zoo_app_placeholder.addClass('active');

    },

    save_zoo_app: function(){
      var $z = this.$zoo_app;
      Server.save_environment_variables(Server.selected_engine);

      var location = [];
      $.each(Grid.get_params($z.find('#app-location')),function (key, value) {
           location.push({'path':key, 'engine':value});
      });
      var config = {
            'selected-engine': Server.selected_engine,
            engines: Server.application.engines,
            path: $z.find('#path').val(),
            environment_variables: Grid.get_params($z.find('#app-environment')),
            locations: location,
      };

      console.log('app config: ', config);

      Status.show('Updating zoo app');

      ZooApi.post(
        ZooApi.Urls.server_root + this.current_node.path,
        config,
        function(response){
          console.log('updating zoo app response: ', response.data);
          Status.hide();
          Status.success('Successfully updated');

          // force to update node view
          Server.current_node = null;
          ServerTree.update_node(response.data);
        }
      )
    },

    show_node: function($node, node){
      if (this.current_node && this.current_node.path == node.path){
        return;
      }

      this.$server_controls.removeClass('active');

      this._show_node($node, node);

      this.show_active_control();
      this.current_node = node;
      this.print_browse_links();
      this.clear_saved_site();
    },

    _show_node: function($node, node) {
      if (node.type == 'server'){
        this.show_server_root();
        return;
      }
      try{
        // .zoo exists ?
              if (node.config != null){
                // .zoo exists

                // state ?
                if (node.config){
                  // state enabled

                  // eninge ?
                  if (node.config.hasOwnProperty('application') && node.config.application){
                    // yes

                    // show app
                        this.show_zoo_app($node, node);


                  } else {
                    // no engine

                    // parent app ?
                    if (node.hasOwnProperty('parent') && node.parent){
                      // yes

                      if (node.parent.config){
                        // parent app enabled

                        // show parent app
                        this.show_parent_zoo_app($node, node);
                      } else {
                        // parent app disabled

                        this.show_empty_app();
                      }
                    } else {
                      // unknown disabled
                      this.show_empty_app();
                    }
                  }
                } else {
                  // state disabled

                  // eninge ?
                  if (node.config.hasOwnProperty('application') && node.config.application){
                    // yes
                    // show disabled app
                        this.show_zoo_app($node, node);

                  } else {
                    // no engine

                    // parent app ?
                    if (node.hasOwnProperty('parent') && node.parent){
                      // yes

                      // show disabled parent app
                      this.show_parent_zoo_app($node, node);
                    } else {
                      // unknown disabled
                      this.show_empty_app();
                    }
                  }
                }
              } else {
                // no .zoo

                // parent app ?
                if (node.hasOwnProperty('parent') && node.parent){
                  // yes

                  if (node.parent.config){
                    // parent app enabled

                    // show parent app
                    this.show_parent_zoo_app($node, node);
                  } else {
                    // parent app disabled

                    this.show_empty_app();
                  }
                } else {
                  // no parent app

                  this.show_empty_app();
                }
              }
      }catch(err){
            console.log("can't create app window");
            this.show_empty_app();
      }
    },

    show_parent_zoo_app: function($node, node){
      console.log('show parent app', node);
      var html = this.parent_app_template({node: node});
      this.$zoo_parent_app_placeholder.html(html).addClass('active');
    },

    show_server_root: function(){
      // init gallery with engines
      Gallery.init(this.engine_list_settings);

      this.$engines_placeholder.addClass('active');
    },

    show_empty_app: function(){
     /* var html = this.parent_app_template({node: node});
      this.$zoo_parent_app_placeholder.html(html).addClass('active');*/
      this.$no_app_placeholder.addClass('active');
    },

    save_site_and_path: function(){
        // save domain & path for install wizard in cookies
        var node = Server.current_node;
        if (node){
          var path = node.path;
          // path: Default Web Site/qwe/wer
          var site_name = null, site_path = '';
          var slash_index = path.indexOf('/');
          if (slash_index > 0){
            site_name = path.substr(0, slash_index);
            site_path = path.substr(slash_index);
          } else {
            site_name = path;
          }

          $.cookie('install_site_name', site_name, {path: '/'});
          $.cookie('install_site_path', site_path, {path: '/'});
        }
    },

    clear_saved_site: function(){
      $.removeCookie('install_site_name', {path: '/'});
      $.removeCookie('install_site_path', {path: '/'});
    },

    disable_zoo_app: function(){
      this.toggle_zoo_app('disabled');
    },

    toggle_zoo_app: function(state){
      var config = {
        state: state
      };

      Status.show('Updating zoo app');
      ZooApi.post(
        ZooApi.Urls.server_root + this.current_node.path,
        config,
        function(response){
          console.log('disabling zoo app response: ', response.data);
          Status.hide();
          Status.success('Successfully updated');

          // force to update node view
          Server.current_node = null;
          ServerTree.update_node(response.data);
        }
      );
    },

    init: function () {

      $('#main-menu a[href="/server/"]').parent().addClass('active');

      ServerTree.set_node_selected_callback(function($node, node){
        Server.show_node($node, node);
      });

      var site_path = Common.get_query_variable("path");
      if(site_path){
          ServerTree.load_server_root(function(){
                    //emulate clicking on nodes
                    var node = $("li.node[data-path='"+ site_path +"']");
                    console.log("find path ", site_path, " node ", node);
                    ServerTree.click_node(node);
                });
      }else{
          ServerTree.load_server_root();
      }


      this.$engines_placeholder.on('click', '.btn-engine-properties', function(e){
        e.preventDefault();
        var engine = Gallery.get_parent_product_for_control($(this));
        Engine.show(engine);
      });

      this.$server_controls.on('click', '.install-app', function(e){
        Server.save_site_and_path();
        return true;
      });

      this.$zoo_app.on('click', '.btn.save', function(e){
        Server.save_zoo_app();
      });

      this.$server_controls.on('click', '.node-link', function(){
        var path = $(this).attr('data-path');
        ServerTree.go_to_node_path(path);
      });

      this.$server_controls.on('mouseenter', '.node-link', function(){
        $(this).addClass('highlight');
        var path = $(this).attr('data-path');
        var $node = $('.node[data-path="'+path+'"]');
        $node.addClass('highlight');
      });
      this.$server_controls.on('mouseleave', '.node-link', function(){
        $(this).removeClass('highlight');
        var path = $(this).attr('data-path');
        var $node = $('.node[data-path="'+path+'"]');
        $node.removeClass('highlight');
      });

      this.$server_controls.on('click', '.btn.enable', function(){
        Server.toggle_zoo_app('enabled');
      });
      this.$server_controls.on('click', '.btn.disable', function(){
        Server.toggle_zoo_app('disabled');
      });

      this.$server_controls.on('mouseenter', '.btn.disable', function(){
        $(this).tooltip('show');
      });

      this.$server_controls.on('click', '.start-web-console', function(){
        console_path = Server.current_node.path

        window.open('/console/?path='+encodeURIComponent(Server.current_node.path)+"&engine="+Server.selected_engine,
                   'zoo_web_console_'+console_path, "width=800, height=600, menubar=no, scrollbars=yes, resizable=yes, toolbar=no");
      });

    },

    engine_list_settings: {
      $installed_list: $('#engines-installed'),
      $not_installed_list: $('#engines-not-installed'),
      filter: 'engine'
    }

  };

  window.Server.init();
});

