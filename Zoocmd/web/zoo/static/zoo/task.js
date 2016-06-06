/*
    {
 "data": {
  "log_messages": [
   {
    "source": "web.read_stderr",
    "created": 1419607149.190669,
    "message": "Core loader: Creating core...\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.242672,
    "message": "settings:\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.244673,
    "message": "bitness: '64'\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.246673,
    "message": "cache_path: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\\cache\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.252673,
    "message": "lang: null\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.254673,
    "message": "logs_path: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\\logs\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.257673,
    "message": "os: windows\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.259673,
    "message": "os_version: 6.1.7601\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.262674,
    "message": "root: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.264674,
    "message": "storage_path: C:\\Users\\ruslan\\NewLifeProjects\\Zoo\\data\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.267674,
    "message": "urls: ['http://ci-helicontech/zoo4/feed.yaml']\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.269674,
    "message": "version: 1.0.0.0\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.272674,
    "message": "webserver: iis\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.274674,
    "message": "zoo_home: c:\\zuu\r\n",
    "level": "WARNING"
   },
   {
    "source": "web.read_stderr",
    "created": 1419607149.277674,
    "message": "\r\n",
    "level": "WARNING"
   }
  ],
  "task": {
   "created": "2014-12-26T17:19:07.371565",
   "status": "pending",
   "params_str": "{\n \"parameters\": {\n  \"erlang59\": {\n   \"install_dir\": \"%SystemDrive%\\\\erl5.9\"\n  }\n },\n \"products\": [\n  {\n   \"author\": \"Ericsson Computer Science Laboratory\",\n   \"description\": \"Erlang is a programming language used to build massively scalable soft real-time systems\\nwith requirements on high availability. Some of its uses are in telecoms, banking, e-commerce,\\ncomputer telephony and instant messaging. Erlang's runtime system has built-in support for concurrency,\\ndistribution and fault tolerance.\\n\",\n   \"eula\": \"http://www.erlang.org/EPLICENSE\",\n   \"files\": [\n    {\n     \"file\": \"http://www.erlang.org/download/otp_win32_R15B.exe\",\n     \"filename\": \"otp_win32_R15B.exe\"\n    }\n   ],\n   \"find_installed_command\": \"if 'install_dir' in parameters and os.path_exists(parameters['install_dir']):\\n  result = InstalledProductInfo()\\n  result.version = windows.get_file_version(parameters['install_dir'] + '\\\\\\\\bin\\\\\\\\erlang.exe', parts=3)\\n  result.install_dir = parameters['install_dir']\",\n   \"icon\": \"http://ci-helicontech/zoo4/Erlang/erlang-100x100.png\",\n   \"install_command\": \"os.cmd('{0} /S /D=\\\"{1}\\\"'.format(files[0].path, parameters['install_dir']))\",\n   \"installed_version\": null,\n   \"link\": \"http://www.erlang.org/\",\n   \"os\": \"windows\",\n   \"parameters\": {\n    \"install_dir\": \"%SystemDrive%\\\\erl5.9\"\n   },\n   \"product\": \"Erlang59\",\n   \"tags\": [\n    \"server\"\n   ],\n   \"title\": \"Erlang\",\n   \"uninstall_command\": \"os.delete_path(parameters['install_dir'])\",\n   \"upgrade_command\": \"os.cmd('{0} /S /D=\\\"{1}\\\"'.format(files[0].path, parameters['install_dir']))\",\n   \"version\": \"5.9 R15B\"\n  }\n ],\n \"requested_products\": [\n  \"Erlang59\"\n ]\n}",
   "updated": "2014-12-26T17:19:07.371565",
   "title": "Installing products: Erlang59",
   "command": "install",
   "params": {
    "requested_products": [
     "Erlang59"
    ],
    "parameters": {
     "erlang59": {
      "install_dir": "%SystemDrive%\\erl5.9"
     }
    },
    "products": [
     {
      "product": "Erlang59",
      "install_command": "os.cmd('{0} /S /D=\"{1}\"'.format(files[0].path, parameters['install_dir']))",
      "author": "Ericsson Computer Science Laboratory",
      "parameters": {
       "install_dir": "%SystemDrive%\\erl5.9"
      },
      "files": [
       {
        "filename": "otp_win32_R15B.exe",
        "file": "http://www.erlang.org/download/otp_win32_R15B.exe"
       }
      ],
      "eula": "http://www.erlang.org/EPLICENSE",
      "title": "Erlang",
      "upgrade_command": "os.cmd('{0} /S /D=\"{1}\"'.format(files[0].path, parameters['install_dir']))",
      "os": "windows",
      "installed_version": null,
      "find_installed_command": "if 'install_dir' in parameters and os.path_exists(parameters['install_dir']):\n  result = InstalledProductInfo()\n  result.version = windows.get_file_version(parameters['install_dir'] + '\\\\bin\\\\erlang.exe', parts=3)\n  result.install_dir = parameters['install_dir']",
      "description": "Erlang is a programming language used to build massively scalable soft real-time systems\nwith requirements on high availability. Some of its uses are in telecoms, banking, e-commerce,\ncomputer telephony and instant messaging. Erlang's runtime system has built-in support for concurrency,\ndistribution and fault tolerance.\n",
      "uninstall_command": "os.delete_path(parameters['install_dir'])",
      "tags": [
       "server"
      ],
      "link": "http://www.erlang.org/",
      "icon": "http://ci-helicontech/zoo4/Erlang/erlang-100x100.png",
      "version": "5.9 R15B"
     }
    ]
   },
   "is_finished": false,
   "error_message": "",
   "id": 110
  }
 }
}
  */
// TODO add supporting of running task


Task = {




    $task_placeholder: $('#task-log-placeholder'),
    $task_log: $('#task-log'),
    $task_log_window: $('#task-log pre'),
    $task_template: $('#task-template'),
    task_template: null,
    window_resize: false,
    $task_menu: $("div.task_menu"),
    $task_log_template: $('#task-log-template'),
    status_repr:
    {"pending": "Pending",
     "running": "Installing",
     "exception": "Exception",
     "failed": "Failed",
     "done": "Success",
    },
    task_log_template: null,
    log_socket: null,
    task_finished: false,
    last_updated: null,
    last_log: 0,


    ExtObject: null,

    $go_to_node_link: $('#go-to-node'),
    clean_log: function(){
        Task.$task_log_window.html("");
    },
    load: function(){

        if (!Task.task_finished && "WebSocket" in window && !Task.ExtObject.reading) {
                var ws ;
                var this_obj = window.Task;
                //TODO try reconnect
                setTimeout(function() {
                        // TODO move to attributes host
                        ws = new WebSocket("ws://localhost:7799/socket/log");
                        this_obj.log_socket = ws;
                        this_obj.log_socket.onopen = function () {
                            console.log("open connection...");
                            this_obj.log_socket.send("{\"msg\":\"hello\",\"task_id\":\""
                                                      + this_obj.ExtObject.task_id + "\"}");
                        };
                        this_obj.log_socket.onmessage = function (Txt) {

                            var Obj = JSON.parse(Txt.data);

                            if(Obj.status) {
                                 console.log(Obj);
                                 this_obj.print_log(Obj["data"]);

                                 if( Obj["state"] === "done" || Obj["state"] === "failed" ){
                                        console.log("open DLG");
                                        this_obj.task_finished = true;
                                        Task.ExtObject.finish(Task, Obj["state"]);
                                        this_obj.log_socket.close()

                                 }else {
                                        this_obj.log_socket.send("{\"msg\":\"ping\",\"task_id\":\""
                                                                 + this_obj.ExtObject.task_id + "\"}");
                                 }

                            }else{
                                //if(!task_obj||!this_obj.task_finished )
                                 this_obj.log_socket.send("{\"msg\":\"ping\",\"task_id\":\""
                                                               + this_obj.ExtObject.task_id + "\"}");
                            }


                        };
                        this_obj.log_socket.onclose = function () {
                            console.log("Connection is closed...");
                        };

                }, 2000);
            } else {
                Task.update_log();
                Task.ExtObject.finish(Task);
            }




    },

    print_task: function(task){

      Task.last_updated = task.updated;
      repr_status = Task.status_repr[task.status];
      console.log('task status obj:', $("#status-tab"), task);

      $("#status-tab").html(repr_status);
      $("#tab-installing").attr("class", task.status);
      console.log('task:',  $("#tab-installing"));

      if(task.status != "running" && task.status != "pending" && task.status != "exception"){
             $("#icon-spin-tab").remove();

             $("#tab-installing").attr("id", "tab-pill-product-installing");
             $("#status-tab").attr("id", "product-status-tab");
      }
      if(task.status == "running" || task.status == "pending"){
            $("#btn-task-cancel").removeClass("hidden");
      }
      if (task.is_finished){
          Task.task_finished = true;
        }

    },

    update_log: function(){
      console.log('update task log since', this.last_log);
      //Status.show('loading logs');
      ZooApi.get(ZooApi.Urls.task + this.ExtObject.task_id + '/log/', {since: this.last_log}, function(response){
        Task.print_log(response.data);
        if (!response.data.task.is_finished || !Task.task_finished){
             Task.wait_and_reload_log();
        }

      });
    },
    linkify: function(text) {
        var urlRegex =/(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        return text.replace(urlRegex, function(url) {
            return '<a target="_blank" href="' + url + '">' + url + '</a>';
        });
    },
    // only print logs to textarea
    print_log: function(data){
      if (data.log_messages){
          //Status.show('printing logs');
        //var html = '';
        var text = [];
        for(var i=0; i<data.log_messages.length; i++){
          var log = data.log_messages[i];
          var message = log['message'];

          message = message.replace(/\s*$/g, '') + '\n';
          message = Task.linkify(message);
          var error_exist = false;
          console.log(log);
          if(log.level==20){
                text.push( message );

          }else{
                text.push("<font class='error' color='red'>"+message+"</font>");
          }
          //+1 a little hack :)
          this.last_log = log.created+1;
        }
        var append_text = text.join("");
        //$(html).appendTo(this.$task_log);
        var ch = this.$task_log[0].clientHeight;
        var sctop = this.$task_log[0].scrollTop;
        var scroll_h = this.$task_log[0].scrollHeight;
        var div = (sctop + ch) - scroll_h;

        //console.log("scroll height "+scroll_h + "scroll top "+sctop + " client_height "+ ch+ " div  is " +div );
        if (text.length > 0 &&  Math.abs( div )<20  ) {
          this.$task_log_window.append(append_text);
          this.$task_log[0].scrollTop = this.$task_log[0].scrollHeight;
        }else{
          this.$task_log_window.append(append_text);

        }
        if(error_exist){
            console.log("error on job", error_exist);
            $("#error"+error_exist).on('click',  function(){
                  $("font.error"+error_exist).show();

               });
        }

      }

      console.log(data.task)
      this.print_task(data.task);
      if(Task.window_resize){
        this.update_log_size();
      }

    },

    wait_and_reload_log: function(){
      setTimeout(function(){
          Task.update_log();
        }, 5000
      );
    },



    cancel: function(cancel_callback){
      console.log('canceling task');
      ZooApi.post(ZooApi.Urls.task + this.ExtObject.task_id + '/cancel/', {}, function(response){
        if(cancel_callback){
            cancel_callback(response.data)
        }else{
            console.log(response.data);
        }
      });
    },
    show_error: function(id){
        $("."+id).removeClass('hidden');
    },
    rerun: function(){
      console.log('re-run task');
      Status.show('re-running task');
      ZooApi.post(ZooApi.Urls.task + this.ExtObject.task_id + '/rerun/', {}, function(response){
        console.log(response.data);
        window.location.reload(true);
      });
    },

    toggle_debug_log: function(enable){
      this.$task_log.find('.log-level-DEBUG').toggle(enable);
      this.$task_log.find('.log-dbg').toggle(enable);
    },


    get_result_urls: function(task){
      $('#result-urls').hide();
      if (!task.is_finished){
        return;
      }

      // search product
      var app_params = null;

      if (task.params) {
        var products_params = task.params.parameters;
        if (products_params) {
          var product_names = Object.keys(products_params);
          for (var i = 0; i < product_names.length; i++) {
            var product_params = products_params[product_names[i]];
            if (product_params.hasOwnProperty('site-name')) {
              app_params = product_params;
              break;
            }
          }
        }
      }

      if (!app_params){
        return;
      }

      var site_name = app_params['site-name'];
      var app_path = app_paramde_link.removeClass('hidden').attr('href', this.$go_to_node_link.attr('href') + '#' + node_path);

      // TODO: get start page!
      var start_page = app_params['start-page'] || '';
      if (app_path.startsWith('/')){
        app_path = app_path.substr(1);
      }s['app-name'] || '';

      var node_path = site_name + app_path;
      this.$go_to_no
      if (app_path && !app_path.endsWith('/')){
        app_path = app_path + '/'
      }
      if (start_page.startsWith('/')){
        start_page = start_page.substr(1);
      }

      // get site object
      ZooApi.get(ZooApi.Urls.server_root + site_name + '/', {}, function(response){
        var node = response.data.node;
        var result_urls = [];
        if (node['urls']){
          for(var i=0; i<node.urls.length; i++){
            var url = node.urls[i];
            result_urls.push(url + app_path + start_page);
          }
          Task.print_result_urls(result_urls);
        }
      });
    },

    print_result_urls: function(urls){
      var html = Handlebars.compile("\{\{#each urls}}<li><a href=\"{{this}}\" target=\"_blank\">{{this}}</a></li>\{\{/each\}\}")({urls: urls});
      $('#result-urls>ul').html(html).parent().show();
    },

    update_log_size: function(){

      var wh = $(window).height();
      var th = wh - $('#header').outerHeight() - 70;
      console.log('set tree height: ', th);
      this.$task_placeholder.height(th);

    },
    attach_window_resize:function(){
           Task.update_log_size();
          $(window).resize(function(){
            Task.update_log_size();
          });
          Task.window_resize = true;
    },
    init: function (Ext) {
      Task.task_log_template = null;
      Task.log_socket = null;
      Task.task_finished  = false;
      Task.last_updated = null;
      Task.last_log = 0;
//      Task.urls_printed = false;
      $('#service-menu').find('a[href="/task/"]').parent().addClass('active');
      Task.ExtObject = Ext;

      // DEPRECATED
      this.$task_placeholder.on('click', '#btn-toggle-task-meta', function(ev){
        Task.$task_placeholder.find('#task-meta').toggle();
      });

      this.$task_placeholder.on('click', '#btn-task-rerun', function(ev){
        Task.rerun();
      });
      // DEPRECATED

      this.$task_menu.on('click', '#btn-task-cancel', function(ev){
            console.log("canceling log", Task.ExtObject.task_id);
            var interface_hide = function(data){
                    if(data.status){
                         Status.show("Job has been canceled");
                         $("#btn-task-cancel").hide();
                         Status.hide(700);
                    }else{
                         Status.show("I can't stop job");
                    }
            }
            Task.cancel(interface_hide);
      });
      this.$task_menu.on('click', '#btn-task-back-history', function(ev){
        window.location.href="/task/";

      });

      this.task_template = Handlebars.compile(this.$task_template.html());
      this.task_log_template = Handlebars.compile(this.$task_log_template.html());

      this.load();


      var ua = window.navigator.userAgent;
      if (ua.indexOf('MSIE ') > 0 || ua.indexOf('Trident') > 0) {
        $('#copy-log').click(function () {
          var log = Task.$task_log[0];
          var cl = document.getElementById('clipboard-area');
          cl.innerText = log.innerText;
          cl.focus();
          var r = cl.createTextRange();
          r.execCommand('selectall');
          r.execCommand('Copy');
        });
      } else {
        $('#copy-log').hide();
      }

    }

  };

