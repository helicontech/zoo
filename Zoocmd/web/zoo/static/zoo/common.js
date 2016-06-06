/**
 * Protect window.console method calls, e.g. console is not defined on IE
 * unless dev tools are open, and IE doesn't define console.debug
 */
(function() {
  if (!window.console) {
    window.console = {};
  }
  // union of Chrome, FF, IE, and Safari console methods
  var m = [
    "log", "info", "warn", "error", "debug", "trace", "dir", "group",
    "groupCollapsed", "groupEnd", "time", "timeEnd", "profile", "profileEnd",
    "dirxml", "assert", "count", "markTimeline", "timeStamp", "clear"
  ];
  // define undefined methods as noops to prevent errors
  for (var i = 0; i < m.length; i++) {
    if (!window.console[m[i]]) {
      window.console[m[i]] = function() {};
    }
  }
})();


/**
 * Object .keys fix for IE8
 */
Object.keys=Object.keys||function(o,k,r){r=[];for(k in o)r.hasOwnProperty.call(o,k)&&r.push(k);return r}


$(document).ready(function () {
  window.Common = {

    get_query_variable: function (variable) {
      var query_string = window.location.search;
      if (query_string && query_string.length>1) {
        var query = query_string.substring(1);
        query = query.split("+").join(" ");
        var vars = query.split('&');
        for (var i = 0; i < vars.length; i++) {
          var pair = vars[i].split('=');
          if (decodeURIComponent(pair[0]) == variable) {
            return decodeURIComponent(pair[1]);
          }
        }
      }
      return null;
    },
    search_element_by_key: function(elems, key, value){
            for(i in elems){
                if(elems[i][key] == value )
                    return elems[i];
            }
            return  null;
    },
    //updating classes
    get_label_class_for_status: function(status){
      if (status == 'failed'){
        return 'danger';
      }
      if (status == 'pending'){
        return 'default';
      }
      if (status == 'done'){
        return 'success';
      }
      if (status == 'running'){
        return 'info';
      }
      return 'default';
    },

    get_label_class_for_level: function(level){
      level = level.toLowerCase();
      if (level == 'debug'){
        return 'muted';
      }
      if (level == 'info'){
        return 'success';
      }
      if (level == 'warning'){
        return 'warning';
      }
      if (level == 'error' || level == 'critical'){
        return 'danger';
      }
      if (level == 'running'){
        return 'info';
      }
      return 'default';
    },

    clone_end_remove_keys: function(obj, keys_to_remove){
      var x = $.extend({}, obj);
      if (keys_to_remove){
        for (var i=0; i<keys_to_remove.length; i++){
          var key = keys_to_remove[i];
          if (x.hasOwnProperty(key)){
            delete x[key];
          }
        }
      }
      return x;
    },

    init: function () {
      if (window.Handlebars) {
        Handlebars.registerHelper('humanize_parameter_name', function (parameter_name) {
          return parameter_name.replace(/_/g, ' ');
        });
        Handlebars.registerHelper('strip_link', function (link) {
          if (link) {
            return link.replace(/^https?:\/\//, '');
          } else {
            return 'no link :-('
          }
        });
        var f = this;
        Handlebars.registerHelper('get_label_class', function (status) {
          return f.get_label_class_for_status(status);
        });
        Handlebars.registerHelper('datetime_fromnow', function (dt) {
          return moment(dt).fromNow();
        });
        Handlebars.registerHelper('datetime_format', function (dt) {
          return moment(dt).format('YYYY-MM-DD HH:mm:ss');
        });
        Handlebars.registerHelper('unixtime_format', function (dt) {
          dt = new Date(parseFloat(dt) * 1000.0);
          return moment(dt).format('YYYY-MM-DD HH:mm:ss.SSS');
        });
        Handlebars.registerHelper('get_level_class', function (level) {
          return Common.get_label_class_for_level(level);
        });
        Handlebars.registerHelper('format_level', function (level) {
          if (level == 'WARNING') {
            level = 'WARN';
          }
          var l = level.length;
          if (l < 5) {
            for (var i = 0; i < 5 - l; i++) {
              level += ' ';
            }
          }
          return level
        });
        Handlebars.registerHelper('get_node_icon', function (node_type) {
          if (node_type == 'server') {
            return 'home';
          }
          if (node_type == 'site') {
            return 'globe';
          }
          if (node_type == 'directory') {
            return 'folder';
          }
          if (node_type == 'virtual directory') {
            return 'folder';
          }

          return 'question-circle';
        });
        Handlebars.registerHelper('ifeq', function (a, b, opts) {
          if (a == b) // Or === depending on your needs
            return opts.fn(this);
          else
            return opts.inverse(this);
        });
        Handlebars.registerHelper('get_engine_title', function (engine_name) {
          try {
            var engine = Gallery.get_engine(engine_name);
            if (engine) {
              return engine.title;
            }
          } catch (err) {
          }
          return engine_name;
        });
      }
    }
  };

  window.Common.init();
});

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

if (typeof String.prototype.startsWith !== 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}


(function($){
    $.fn.serializeObject = function(){

        var self = this,
            json = {},
            push_counters = {},
            patterns = {
                "validate": /^[a-zA-Z][a-zA-Z0-9_]*(?:\[(?:\d*|[a-zA-Z0-9_]+)\])*$/,
                "key":      /[a-zA-Z0-9_]+|(?=\[\])/g,
                "push":     /^$/,
                "fixed":    /^\d+$/,
                "named":    /^[a-zA-Z0-9_]+$/
            };


        this.build = function(base, key, value){
            base[key] = value;
            return base;
        };

        this.push_counter = function(key){
            if(push_counters[key] === undefined){
                push_counters[key] = 0;
            }
            return push_counters[key]++;
        };

        $.each($(this).serializeArray(), function(){

            // skip invalid keys
            if(!patterns.validate.test(this.name)){
                return;
            }

            var k,
                keys = this.name.match(patterns.key),
                merge = this.value,
                reverse_key = this.name;

            while((k = keys.pop()) !== undefined){

                // adjust reverse_key
                reverse_key = reverse_key.replace(new RegExp("\\[" + k + "\\]$"), '');

                // push
                if(k.match(patterns.push)){
                    merge = self.build([], self.push_counter(reverse_key), merge);
                }

                // fixed
                else if(k.match(patterns.fixed)){
                    merge = self.build([], k, merge);
                }

                // named
                else if(k.match(patterns.named)){
                    merge = self.build({}, k, merge);
                }
            }

            json = $.extend(true, json, merge);
        });

        return json;
    };
})(jQuery);