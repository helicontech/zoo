$(document).ready(function () {
  window.Status = {

    $status: $('#status'),
    $message: $('#status-message'),
    $info: $('#info'),

    $info_template: $('<div class="alert alert-success"><i class="fa fa-check"></i> <span class="message"></span></div>'),

    show: function(message){
      this.$message.text(message);
      this.$status.show();
    },

    hide: function(timeout){
      if(timeout){
        setTimeout(function(){
            Status.$status.fadeOut();
            Status.$message.text('');
          },timeout)

      }else{
          this.$status.hide();
          this.$message.text('');
      }
    },

    success: function(message){
      var $m = this.$info_template.clone();
      $m.find('.message').text(message);
      this.$info.empty().append($m).fadeIn();
      setTimeout(function(){
        Status.$info.fadeOut();
      }, 5000);
    },

    init: function () {
    }

  };

  window.Status.init();
});

