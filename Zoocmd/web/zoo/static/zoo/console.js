
//DEPRECATED
$(document).ready(function () {
  window.Console = {

    path: null,

    created: false,

    history: [],
    history_index: null,

    default_pause: 200,
    idle_pause: 400,
    current_pause: 200,

    create: function(){
      ZooApi.post(ZooApi.Urls.console_create,  {path: this.path}, function(response){
        Console.created = true;
        Console.show_disconnected();
      });
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
      ZooApi.post(
        ZooApi.Urls.console_write,
        {data: command, path: this.path},
        function(response){
          Console.$command.val('');
          Console.hide_progress();
        }
      );
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

    print: function(stdout, stderr){
      if (stdout) {

        var new_elem = $('<span>').text(stdout).mouseup(function(e){
          Console.$command.focus();
       });

        //Console.add_focus_event(new_elem)

        this.$output.append( new_elem );

        window.scrollTo(0, document.body.scrollHeight);
      }
      if (stderr) {
        var new_elem = $('<span>').text(stderr).addClass('stderr');
        Console.add_focus_event(new_elem)

        this.$output.append();


        window.scrollTo(0, document.body.scrollHeight);
      }
    },

    cancel: function(){
      if (this.created) {
        ZooApi.post_sync(
            ZooApi.Urls.console_cancel,
            {path: this.path},
            function (response) {
              Console.created = false;
              Console.show_disconnected();
            }
        );
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
      this.$command.val(command).focus();
    },


    init: function () {

      this.$body = $('body');
      this.$command = $('#command');
      this.$output = $('#output');
      this.$cancel = $('#cancel');
      this.$close = $('button#close');
      this.$disconnected = $('#disconnected');
      this.$connect = $('button#connect');



      this.path = Common.get_query_variable('path');
      if (!this.path){
        alert('Server path is not specified.');
        return;
      }
      this.create();

      this.$command.focus();

      this.$output.mouseup(function(e){
          console.log("focusing ")
          Console.$command.focus();
      });

      $(".welcome").mouseup(function(e){
          console.log("focusing ")
          Console.$command.focus();
      });


      this.$command.keyup(function(e){
        if(e.which == 13) {
          var command = $(this).val();
          Console.write(command);
          return;
        }

        if (e.which == 38){
          Console.show_history(1);
        }
        if (e.which == 40){
          Console.show_history(-1);
        }
      });

      this.read();

      this.$close.click(function(){
        Console.cancel();
        // window.close -disallowed by modern browsers
        //window.close();
      });

      $(window).unload(function() {
        Console.cancel();
      });

      this.$connect.click(function(){
        Console.create();
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

