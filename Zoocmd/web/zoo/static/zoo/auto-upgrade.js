$(document).ready(function () {
  window.AutoUpgrade = {

    $block: $('#auto-upgrade'),
    cookie_name: 'hide-auto-upgrade',

    check_upgrade: function(){
      ZooApi.get(
        ZooApi.Urls.core_upgrade,
        {},
        function(response){
          if (response.data['version']){
            if ($.cookie(AutoUpgrade.cookie_name) != '1'){
              AutoUpgrade.$block.fadeIn();
            }
          }
        }
      );
    },

    close: function(){
      this.$block.hide();
      $.cookie(this.cookie_name, "1");
    },

    init: function () {
      this.$block.find('button.close').click(function(){
        AutoUpgrade.close();
      });
      setTimeout(
        this.check_upgrade,
        1000
      );
    }

  };

  window.AutoUpgrade.init();
});

