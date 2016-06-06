$(document).ready(function () {
  window.Settings = {
    load: false,
    $form: $('#settings'),
    $url_input: $('#url'),
    $add_url_btn: $('#add-url'),
    $url_input_row: $('#url-row'),
    $save: $('#save'),
    $service_info: $('#service-info'),

    load: function(){
      Status.show('Loading settings');
      ZooApi.get(
        ZooApi.Urls.settings,
        {},
        function(response){

          Settings.print_settings(response.data);
          Settings.load = true;
          Status.hide();
        }
      );
    },

    print_settings: function(data){
      this.print_service_info(data.info);
      var settings = data.settings;
      console.log('settings: ', settings);
      var names = Object.keys(settings);
      for(var i=0; i<names.length; i++){
        var name = names[i];
        var value = settings[name];
        if (value){
          if ($.isArray(value)){
            // ?
            name = name + '[]';
            if (name == 'urls[]'){
              this.clear_url_inputs();
              for(var k=0; k<value.length; k++){
                this.add_url_input(true);
              }
            }
          } else {
            value = String(value);
          }
        } else {
          value = '';
        }
        var $control = this.$form.find('[name="'+name+'"]');
        if ($control.length == 1){
          $control.val(value);
        } else if ($control.length > 1){
          if ($control.is(':radio')){
            var $target = $control.filter('[value="'+value+'"]');
            $target.prop('checked', true);
          } else {
            // assume this is list of strings
            for(var j=0; j<value.length; j++){
              $($control[j]).val(value[j]);
            }
          }
        }
      }
    },

    print_service_info: function(info){
      var s = [];
      s.push('Version: '+info['version']);
      s.push('OS: '+info['os']);
      s.push('OS Version: '+info['os_version']);
      s.push('Bitness: '+info['bitness']);
//      s.push('User Agent: ' + navigator.userAgent);
      this.$service_info.text(s.join('\n'));
    },
    add_url_input: function(force){
      if (!force && !this.$url_input.val()){
        return;
      }
      var $row = this.$url_input_row.clone();
      $row.addClass('created').attr('id', '');
      $row.find('input').attr('id', '');
      $row.find('input').attr('name', $row.find('input').attr('name-temp'));
      $row.find('.remove').removeClass('hide-soft');
      $row.find('.add').addClass('hide-soft');
      $row.insertBefore(this.$url_input_row);
      this.$url_input.val('').focus().keyup();
    },

    clear_url_inputs: function(){
      $('.row.created').remove();
    },

    save: function(){
      if(!Settings.load)
          return ;

      var settings = this.$form.serializeObject();
      if (!settings['urls']){
        settings['urls'] = [];
      }
      if (settings['zoo_home'] == ''){
//        alert('Zoo Home setting can not be empty!');
        delete settings['zoo_home']
      }
      console.log('settings: ', settings);
      Status.show('Updating settings');
      ZooApi.post(
        ZooApi.Urls.settings,
        settings,
        function(response){
          Settings.print_settings(response.data);
          Status.hide();
          Status.success('Settings successfully updated. Core is reloading now...');
          setTimeout(
            function(){
              window.location.href = '/';
            },
            2000
          )
        }
      )
    },

    clear_cache: function(){
      Status.show('Clearing cache');
      ZooApi.get(
        ZooApi.Urls.cache_clear,
        {},
        function(response){
          Status.hide();
          Status.success('Cache successfully cleared');
          Settings.show_size($('#cache-size'), response.data.size);
        }
      );
    },

    clear_logs: function(){
      Status.show('Clearing logs');
      ZooApi.get(
        ZooApi.Urls.logs_clear,
        {},
        function(response){
          Status.hide();
          Status.success('Logs successfully cleared');
          Settings.show_size($('#logs-size'), response.data.size);
        }
      );
    },

    get_logs_and_cache_size: function(){
      ZooApi.get(
        ZooApi.Urls.logs,
        {},
        function(response){
          Settings.show_size($('#logs-size'), response.data.size);
        }
      );

      ZooApi.get(
        ZooApi.Urls.cache,
        {},
        function(response){
          Settings.show_size($('#cache-size'), response.data.size);
        }
      );

    },

    show_size: function($el, size){
      var s, unit;
      if (size > 1024*1024){
        s = size / 1024 / 1024;
        unit = ' Mb';
      } else {
        s = size / 1024;
        unit = ' Kb';
      }
      $el.text(s.toFixed(1)+unit);
    },

    init: function () {
      $('#service-menu a[href="/settings/"]').parent().addClass('active');

      this.$add_url_btn.click(function(){
          Settings.add_url_input();
      });

      this.$save.click(function(){
          Settings.save();
      });

      this.$url_input.keyup(function(e){
        if(e.which == 13) {
          Settings.add_url_input();
          e.preventDefault();
        }
      });

      this.$url_input.on('change keyup', function(){
        if (Settings.$url_input.val()){
          Settings.$add_url_btn.removeClass('disabled');
        } else {
          Settings.$add_url_btn.addClass('disabled');
        }
      });

      $('#urls-group').on('click', '.remove', function(){
        $(this).closest('.created').remove();
      });

      $('#clear-logs').click(function(){
        Settings.clear_logs();
      });
      $('#clear-cache').click(function(){
        Settings.clear_cache();
      });

      this.load();

      this.get_logs_and_cache_size();
    }

  };

  window.Settings.init();
});

