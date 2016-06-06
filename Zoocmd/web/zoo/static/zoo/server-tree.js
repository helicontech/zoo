$(document).ready(function () {
  window.ServerTree = {

    $tree: $('#server-tree'),
    $server_controls: $('#server-controls'),
    $no_server: $('#no-server'),
    is_installed:false,
    branch_template: Handlebars.compile($('#tree-branch-template').html()),

    // nodes cache
    cache: {},

    // node selected callback
    callback: null,

    // selected node
    node: null,

    // path to be tree navigated on startup
    navigate_path: null,
    navigate_path_names: null,
    current_path: null,
    current_path_index: 0,
    need_to_process_navigate_path: false,

    cache_nodes: function(nodes){
      for (var i in nodes){
        var node = nodes[i];
        this.cache_node(node);
      }
    },

    cache_node: function(node){
      this.cache[node.path] = node;
    },

    cache_clean_children: function(node){
      // clean all node children in cache
      var parent_path = node.path;
      var paths = Object.keys(this.cache);
      for(var i=0; i<paths.length; i++){
        var path = paths[i];
        if (this.cache.hasOwnProperty(path)){
          if (path == parent_path){
            continue;
          }
          if (path.startsWith(parent_path)) {
            var $node = this._get_$node(path);
            $node.remove();
            console.log('deleting node:' + path);
            delete this.cache[path];
          }
        }
      }
    },

    load_server_root: function(callback){
      Status.show('Loading server');
      if(ServerTree.is_installed){
           ZooApi.get(ZooApi.Urls.server_root, {}, function(response){
                var data = response.data;
                ServerTree.set_root(data);
                Status.hide();
                if(callback){
                  callback();
                }
              });


      }else{
          ZooApi.get(ZooApi.Urls.check_webserver_installed, {}, function(response){
              var data = response.data;
              if(data.status){
                  ServerTree.is_installed = true;
                  return   ServerTree.load_server_root(callback);

              }else{
                  var server = data.server;
                  if(server == "iisexpress"){
                       $("#no_server_name").html("Microsoft IIS Express");
                       $("#no_server_name_install_link").attr("href", "/install/?products=Microsoft.IISExpress");
                       ServerTree.$no_server.removeClass("hide-soft");
                       Server.show_server_root();
                       Server.show_active_control();

                  }
                  if(server == "iis"){
                    $("#no_server_name").html("Microsoft IIS");
                    $("#no_server_name_install_link").attr("href", "/install/?products=Microsoft.IIS");
                    ServerTree.$no_server.removeClass("hide-soft");
                    Server.show_server_root();
                    Server.show_active_control();

                  }
                  Status.hide();
                  if(callback){
                    callback();
                  }
                  //TODO adding support of other servers
              }
          });



      }

    },

    set_root: function(data){
      // server node
      var server_node = data['node'];
      if (!server_node['name']){
        // NO SERVER!
        server_node['name'] = 'Microsoft IIS is not installed';
        this.print_nodes(this.$tree, [server_node]);
        var $root_node = this.get_root_node();
        $root_node.addClass('no-server').find('.expander').remove();
        $root_node.find('.node-title .fa').removeClass('fa-home').addClass('fa-warning');

        this.$no_server.show();
        this.set_active(this.get_root_node(), server_node);

        return;
      }

      this.cache_nodes([server_node]);
      this.print_nodes(this.$tree, [server_node]);

      // web site nodes
      var website_nodes = data['children'];
      this.cache_nodes(website_nodes);
      this.print_nodes(this.get_root_node(), website_nodes);

      // set server root active - show engines
      this.set_active(this.get_root_node(), server_node);

      if (this.navigate_path){
        setTimeout(
          function() {
            ServerTree.open_navigate_path();
          },
          50
        );
      }
    },

    open_navigate_path: function(){
      if (!this.need_to_process_navigate_path){
        return;
      }

      if (this.current_path == this.navigate_path){
        this.need_to_process_navigate_path = false;
        return;
      }

      for (var i=this.current_path_index; i<this.navigate_path_names.length; i++){
        var node_name = this.navigate_path_names[i];
        if (!node_name || node_name == ''){
          continue;
        }
        this.current_path += node_name + '/';
        this.current_path_index = i+1;
        var $node = this._get_$node(this.current_path);
        if ($node.length == 1){
          this.click_node($node);
          break;
        }
      }
    },

    get_root_node: function(){
      return this.$tree.find('.node[data-type="server"]').first();
    },

    print_nodes: function($node, nodes) {
      var html = this.branch_template({nodes: nodes});
      $node.find('>.children').html(html);
      $node.addClass('loaded');
      if (!$node.hasClass('expanded')){
        this.toggle_children($node);
      }
    },

    click_node: function($node){
      if (!$node.hasClass('expanded')) {
        this.toggle_node($node);
      }else{
        this.set_active($node);
      }
    },

    toggle_node: function($node){
      if ($node.hasClass('expanded')){
        this.toggle_children($node);
      } else {
        if ($node.hasClass('loaded')){
          this.toggle_children($node);
        } else {
          this.load_node($node);
        }
      }
    },

    load_node: function($node){
      var node = this.get_node($node);
      Status.show('Loading '+$node.text());
      console.log('loading nodes for '+ node.path);
      ZooApi.get(ZooApi.Urls.server_root + node.path, {}, function(response){
        var data = response.data;
        ServerTree.set_node($node, data);
        ServerTree.set_active($node);
        Status.hide();

      });
    },

    set_active: function($node, node){
      this.$tree.find('.node.active').removeClass('active');
      ServerTree.$active = $node;
      $node.addClass('active');
      this.node = node || this.get_node($node);
      if (this.callback){
        this.callback($node, this.node);
      }
    },

    set_node: function($node, data){
      this.cache_node(data.node);
      this.cache_nodes(data.children);
      this.print_nodes($node, data.children);
      setTimeout(
        function(){
          ServerTree.open_navigate_path();
        },
        50
      );
    },

    update_node: function(data){
      var $node = this._get_$node(data.node.path);
      this.cache_clean_children(data.node);
      this.set_node($node, data);
      this.set_active($node, data.node);
    },

    toggle_children: function($node){
      $node.find('>.children').slideToggle(250);
      $node.find('>.expander>.fa').toggle();
      $node.toggleClass('expanded');
    },


    get_node: function($node){
      var path = $node.attr('data-path') || '';
      var node = this.cache[path];
      // search parent zoo app
      var parent_zoo_app_node = ServerTree._get_parent_zoo_app(node);
      if (parent_zoo_app_node){
        node['parent'] = parent_zoo_app_node;
      }
      return node;
    },

    _get_parent_zoo_app: function(node){
      var parent_path = ServerTree._get_parent_path(node.path);
      if (parent_path){
        var parent_node = ServerTree.cache[parent_path];
        if (parent_node['config']){
          return parent_node;
        }

        return ServerTree._get_parent_zoo_app(parent_node);
      }

      return null;
    },

    _get_parent_path: function(path){
      if (!path){
        return null;
      }

      // fix trailing slash
      path = path.replace(/\/+$/, '');

      var slash_index = path.lastIndexOf('/');
      if (slash_index > 0){
        return  path.substr(0, slash_index+1);
      }

      return null;
    },

    set_node_selected_callback: function(callback){
      this.callback = callback;
    },

    go_to_node_path: function(path){
      var $node = ServerTree._get_$node(path);
      ServerTree.click_node($node);
    },

    _get_$node: function(path){
      return $('.node[data-path="'+path+'"]');
    },

    update_tree_size: function(){
      var wh = $(window).height();
      var th = wh - $('#header').outerHeight() - 30;
      //console.log('set tree height: ', th);
      this.$tree.height(th);
      this.$tree.width(ServerTree.$tree.parent().width());

      this.$server_controls.height(th);



    },


    init: function () {
      this.$tree.on('click', '.node-title', function(e){
        ServerTree.click_node($(this).closest('.node'));
        e.preventDefault();
        return false;
      });
      this.$tree.on('click', '.expander', function(e){
        ServerTree.toggle_node($(this).closest('.node'));
        e.preventDefault();
        return false;
      });

      this.update_tree_size();

      $(window).resize(function(){
        ServerTree.update_tree_size();
      });

      var hash = window.location.hash;
      if (hash){
        hash = hash.substr(1);
        if (hash){
          this.navigate_path = hash;
          this.navigate_path_names = this.navigate_path.split('/');
          this.current_path = '';
          this.current_path_index = 0;
          this.need_to_process_navigate_path = true;
        }
      }
    }

  };

  window.ServerTree.init();
});

