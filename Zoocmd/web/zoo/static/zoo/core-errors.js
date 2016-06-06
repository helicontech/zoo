$(document).ready(function () {
  window.Home = {

    at_home_page: window.location.pathname == '/',

    wait_and_check_state: function(){
      if (!Home.at_home_page){
        return;
      }
      setTimeout(
        function(){
          Home.check_state();
        },
        2000
      );
    },

    check_state: function(){
      ZooApi.get(
        ZooApi.Urls.core_state,
        {},
        function(response){
          Home.show_state(response.data);
        }
      );
    },

    show_state: function(data){
      var state = data['state'];
      if (state == 'starting'){
        var message = data['message'];
        message = message || '';
        $('#message').text(message);
        return this.wait_and_check_state();
      }

      if (state == 'ready'){
           if(data["warnings"]&&data["warnings"].length){
                 var html = "";
                 for(var i=0; i<data['warnings'].length; i++){
                      var error = data['warnings'][i];
                      html += '\n' + error['message'] + ':\n' + error['traceback'];
                 }
                 $('div.modal-footer button[data-dismiss="modal"]').on("click", function(){
                     if(window.Home.at_home_page) {
                       window.location.href = '/gallery/?filter=application';
                    }else{
                      return true;
                    }
                 });
                 ErrorMessage.show_html(html);
                 Status.hide();
                 return ;
             }else{
               if (this.at_home_page) {
                    window.location.href = '/gallery/?filter=application';
                    return
              }

             }
      }



/*
      if (state == 'failed'){
        if (this.at_home_page) {
          var html = this.errors_template(data);
          $('h1').slideUp();
          $('#errors').html(html).slideDown();
        } else {
          var html = 'An errors occured during Core loading:\n';
          if (data['errors']){
            for(var i=0; i<data['errors'].length; i++){
              var error = data['errors'][i];
              html += '\n' + error['message'] + ':\n' + error['traceback'];
            }
          }
          ErrorMessage.show_html(html);
        }
        return;
      }
*/
      this.wait_and_check_state();
    },

    init: function () {
      this.check_state();
    }

  };

  window.Home.init();
});

