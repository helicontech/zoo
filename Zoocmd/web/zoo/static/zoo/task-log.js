$(document).ready(function () {
  window.TaskLog = {

    $task_placeholder: $('#task-placeholder'),
    $task_log: $('#task-log'),

    $task_template: $('#task-template'),
    task_template: null,

    $task_log_template: $('#task-log-template'),
    task_log_template: null,

    task_id: window['task_id'],
    task_finished: false,
    last_updated: null,
    last_log: 0,
    urls_printed: false,

    update_log_size: function(){
      var wh = $(window).height();
      var tph = this.$task_placeholder.height();
      var th = wh - $('#header').outerHeight() - tph - 100;
      console.log('task log height: ', th);
      this.$task_log.height(th);
    },

    init: function () {
      $('#service-menu').find('a[href="/task/"]').parent().addClass('active');

      this.update_log_size();
      $(window).resize(function(){
        TaskLog.update_log_size();
      });

      var status = $('.status').attr('data-status');
      var status_class = Common.get_label_class_for_status(status);
      $('.status').addClass('label-'+status_class);

      var ua = window.navigator.userAgent;
      if (ua.indexOf('MSIE ') > 0 || ua.indexOf('Trident') > 0) {
        $('#copy-log').click(function () {
          var log = TaskLog.$task_log[0];
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

  window.TaskLog.init();
});

