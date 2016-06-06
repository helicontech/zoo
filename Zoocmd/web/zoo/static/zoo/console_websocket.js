$(document).ready(function () {
  window.Console = {

    path: null,

    created: false,

    history: [],
    history_index: null,

    default_pause: 200,
    idle_pause: 400,
    current_pause: 200,

    create: function(this_obj){
                        ws = new WebSocket("ws://localhost:7799/console2");
                        this_obj.console_socket = ws;
                        this_obj.console_socket.onopen = function () {
                            console.log("open connection...");
                            this_obj.created=true;
                            this_obj.show_disconnected();
                            var engine = Common.get_query_variable("engine");
                            this_obj.console_socket.send("{\"create\":true,\"engine\":\""+engine+"\",\"path\":\""+ this_obj.path +"\"}");
                        };
                        this_obj.console_socket.onmessage = function (Txt) {

                            var Obj = JSON.parse(Txt.data);
                            if(Obj.status) {
                                 this_obj.print(Obj["messages"]);
                                 this_obj.console_socket.send("{\"ping\":true,\"path\":\""
                                                                     + this_obj.path + "\"}");
                            }
                            this_obj.console_socket.send("{\"ping\":true,\"path\":\""
                                                                     + this_obj.path + "\"}");

                        };
                        this_obj.console_socket.onclose = function () {
                            console.log("Connection is closed...");
                            this_obj.created=false;
                            this_obj.show_disconnected();
                        };
    },
    show_progress: function(){

    },

    hide_progress: function(){

    },

    write: function(command){
      if (!this.created){
        return;
      }
      this.current_pause = this.default_pause;
      this.save_history(command);
      this.show_progress();
      this.send_command(command);
      this.$command.val('');
      this.hide_progress();

    },
    send_command: function(command){
            var msg = JSON.stringify({'command': command, path: this.path});
            this.console_socket.send(msg);
    },
    read: function(){
      if (!this.created){
        this.wait_and_read();
        return;
      }
      ZooApi.get(
        ZooApi.Urls.console_read,
        {path: this.path},
        function(response){
          if (response.data.stdout || response.data.stderr){
            console.log('read response: ', response.data);
            Console.current_pause = Console.default_pause;
          } else {
            // empty response
            Console.current_pause = Console.idle_pause;
          }
          Console.print(response.data.stdout, response.data.stderr);
          Console.wait_and_read();
        },
        function(jqxhr, status, error){
          ZooApi.on_error(jqxhr, status, error);
          Console.created = false;
          Console.show_disconnected();
        }
      );
    },

    wait_and_read: function () {
      setTimeout(
        function(){
          Console.read();
        },
        Console.current_pause
      );
    },

    print: function(stdout){

        if (stdout) {
           for(i in stdout){
                var item = stdout[i].message;
                 var new_elem;
                if(stdout[i].type=="stdout"){
                    new_elem = $('<span>').text(item);
                }else{
                    new_elem = $('<span style="color:red">').text(item);
                }
                console.log(item)
               this.$output.append( new_elem );
            }
            window.scrollTo(0, document.body.scrollHeight);
        }


    },
    ctrl_c: function(){
      if (this.created) {
            this.console_socket.send("{\"ctrl_c\":true,\"path\":\""+ this.path +"\"}");
            Console.$command.focus();
      }
    },
    cancel: function(){
      if (this.created) {
            this.console_socket.send("{\"cancel\":true,\"path\":\""+ this.path +"\"}");
      }
    },


    show_disconnected: function(){
      if (this.created){
        this.$cancel.show();
        this.$disconnected.hide();
      } else {
        this.$cancel.hide();
        this.$disconnected.show();
      }
      this.$command.focus();
    },

    save_history: function(command){
      var s = command.trim();
      if (s) {
        this.history.splice(0, 0, command);
        this.history_index = null;
      }
    },

    show_history: function(dir){

      if (this.history.length == 0){
        return;
      }

      if (this.history_index == null){
        if (dir > 0){
          this.history_index = 0;
        }
      } else {
        this.history_index += dir;
      }

      if (this.history_index < 0){
        this.history_index = 0;
      }

      if (this.history_index == null){
        return;
      }

      if (this.history_index >= this.history.length){
        this.history_index = this.history.length - 1;
      }

      var command = this.history[this.history_index];
      this.$command.val(command);
    },


    init: function () {

      this.$body = $('body');
      this.$command = $('#command');
      this.$output = $('#output');
      this.$cancel = $('#cancel');
      this.$close = $('button#close');
      this.$disconnected = $('#disconnected');
      this.$connect = $('button#connect');
      var this_obj = this;


      this.path = Common.get_query_variable('path');
      if (!this.path){
        alert('Server path is not specified.');
        return;
      }
      this.create(this_obj);
      this.$command.focus();

       $("body").keydown(function(e){
            Console.$command.focus();
            if(e.which == 13) {
              var command = Console.$command.val();
              Console.write(command);
              return false;
            }
            if (e.which == 38){
              Console.show_history(1);
              return false;
            }
            if (e.which == 40){
              Console.show_history(-1);

              return false;
            }

       });

      this.$close.click(function(){

        Console.ctrl_c();

      });


      $(window).unload(function(){
            Console.cancel();
      });

      this.$connect.click(function(){
             Console.create(this_obj);
      })
    }
  };

  window.Console.init();
});

//Ensures there will be no 'console is undefined' errors
window.console = window.console || (function(){
    var c = {}; c.log = c.warn = c.debug = c.info = c.error = c.time = c.dir = c.profile = c.clear = c.exception = c.trace = c.assert = function(s){};
    return c;
})();

