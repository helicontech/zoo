$(document).ready(function () {
  window.Database = {

    $engine: $('#db-engine'),
    $placeholder: $('#database-placeholder'),
    $btn_check_connection: $('#db-check-connection'),
    $btn_accept_database: $('#btn-accept-database'),

    $connection_status_success: $('#connection-status-success'),
    $connection_status_failed: $('#connection-status-failed'),

    engines: [],

    set_engines: function(engines){
      this.engines = engines;
    },

    print_engine_options: function(){
      var $e = this.$engine;
      $e.find('option').remove();
      if (this.engines && this.engines.length) {
        for (var i=0; i<this.engines.length; i++){
          var engine = this.engines[i];
          $('<option value="'+engine+'">'+engine+'</option>').appendTo($e);
        }
      }
    },

    get_db_params: function(){
      var params = {};
      this.$placeholder.find('.form-control').each(function(i, el){
        var $el = $(el);
        var id_attr = $el.attr('id');
        if (id_attr && id_attr.substr(0, 3) == 'db-'){
          params[id_attr] = $el.val();
        }
      });

      return params;
    },

    check_connection: function(){
      Status.show('Checking database connection');
      var params = this.get_db_params();
      ZooApi.post(ZooApi.Urls.db_check_connection, params, this.check_connection_response);
    },

    check_connection_response: function(response){
      Status.hide();
      console.log(response.data);
      if (response.data.success){
        Database.$connection_status_success.show();
        Database.$connection_status_failed.hide();
      } else {
        Database.$connection_status_success.hide();
        Database.$connection_status_failed.show();
      }
    },

    validate: function () {

      Database.$connection_status_success.hide();
      Database.$connection_status_failed.hide();

      var params = this.get_db_params();

      var is_valid = true;
      for(var prop in params){
        if(!params[prop]){
          is_valid = false;
          break;
        }
      }

      this.$btn_accept_database.toggleClass('disabled', !is_valid);
    },

    init: function () {
      this.$btn_check_connection.click(function(){Database.check_connection();});
      this.$placeholder.on('change keyup', '.form-control', function(){Database.validate();});
      this.validate();
    }

  };

  window.Database.init();
});

