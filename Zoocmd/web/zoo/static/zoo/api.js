$(document).ready(function () {
  window.ZooApi = {

  /*  Urls: {
      product_list: '/api/1/product/list/',
      tag_list:     '/api/1/tag/list/',

      install:   '/api/1/install/',
      upgrade:   '/api/1/upgrade/',
      uninstall: '/api/1/uninstall/',

      task_list: '/api/1/task/list/',
      task:      '/api/1/task/id/',

      website_list:   '/api/1/server/list/',
      website_create: '/api/1/server/create/',
      server_root:    '/api/1/server/root/',

      engine_list: '/api/1/engine/list/',
      engine:      '/api/1/engine/id/',

      app_pool_list: '/api/1/webapppool/list/',

      db_check_connection: '/api/1/db/check/',

      console_create: '/api/1/console/create/',
      console_write:  '/api/1/console/write/',
      console_read:   '/api/1/console/read/',
      console_cancel: '/api/1/console/cancel/',

      settings:   '/api/1/settings/',
      core_state: '/api/1/core/state/',
      sync:       '/api/1/core/sync/',
      core_upgrade: '/api/1/core/upgrade/',
      cache:  '/api/1/core/cache/',
      cache_clear:  '/api/1/core/cache/clear/',
      logs:   '/api/1/core/logs/',
      logs_clear:   '/api/1/core/logs/clear/'
    },
    */
    Urls: {
      product_list: '/api/2/product/list/',
      tag_list:     '/api/2/tag/list/',
      site_launch: "/api/2/site_launch/",
      install:   '/api/2/install/',
      check_webserver_installed: "/api/2/check_webserver_installed/",
      install_app:   '/api/2/install/application/',
      upgrade:   '/api/2/upgrade/',
      uninstall: '/api/2/uninstall/',

      task_list: '/api/2/task/list/',
      task:      '/api/2/task/id/',

      website_list:   '/api/2/server/list/',
      website_create: '/api/2/server/create/',
      server_root:    '/api/2/server/root/',

      engine_list: '/api/2/engine/list/',
      engine:      '/api/2/engine/id/',

      app_pool_list: '/api/2/webapppool/list/',

      db_check_connection: '/api/2/db/check/',

      console_create: '/api/2/console/create/',
      console_write:  '/api/2/console/write/',
      console_read:   '/api/2/console/read/',
      console_cancel: '/api/2/console/cancel/',

      settings:   '/api/2/settings/',
      core_state: '/api/2/core/state/',
      sync:       '/api/2/core/sync/',
      core_upgrade: '/api/2/core/upgrade/',
      cache:  '/api/2/core/cache/',
      cache_clear:  '/api/2/core/cache/clear/',
      logs:   '/api/2/core/logs/',
      logs_clear:   '/api/2/core/logs/clear/'
    },
    get: function (url, data, on_success, on_error) {
      $.ajax({
               type: 'GET',
               url: url + '?' + $.param(data),
               dataType : 'json',
               async: true,
               success: on_success,
               error: on_error || this.on_error
             });
    },

    post: function (url, data, on_success) {
      $.ajax({
               type: 'POST',
               url: url,
               dataType : 'json',
               async: true,
               data: JSON.stringify(data),
               contentType: 'application/json',
               success: on_success,
               error: this.on_error
             });
    },

    post_sync: function (url, data, on_success) {
      $.ajax({
               type: 'POST',
               url: url,
               dataType : 'json',
               async: false,
               data: JSON.stringify(data),
               contentType: 'application/json',
               success: on_success,
               error: this.on_error
             });
    },

    on_error: function (jqxhr, status, error) {
      if (window.Status && window.ErrorMessage) {
        Status.hide();
        ErrorMessage.show(jqxhr, status, error);
      } else {
        if (jqxhr && 'responseJSON' in jqxhr && 'error' in jqxhr['responseJSON']){
          var err = jqxhr['responseJSON']['error'];
          alert('An error occurred: ' + err.args);
        } else {
          console.log('An error occured: ', jqxhr, status, error);
          alert('An error occurred: ' + error);
        }
      }
    },

    get_cookie: function (name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != "") {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },

    csrf_safe_method: function (method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    },

    init: function () {
      var csrftoken = this.get_cookie('csrftoken');
      var api = this;
      $.ajaxSetup({
                    beforeSend: function (xhr, settings) {
                      xhr.url = settings.url;
                      xhr.method = settings.type;
                      if (!api.csrf_safe_method(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                      }
                    }
                  });
    }
  };

  window.ZooApi.init();
});

