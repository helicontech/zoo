$(document).ready(function () {
  window.WaitCore = {
   core_state: function(callback){


       ZooApi.post(
        ZooApi.Urls.core_state,
        {},
        function(response){

          if( response.data["state"]=="ready"){
             console.log(response);
             if(response.data["warnings"]){
                 var data = response.data;
                 var html = "";
                 for(var i=0; i<data['warnings'].length; i++){
                      var error = data['warnings'][i];
                      html += '\n' + error['message'] + ':\n' + error['traceback'];
                 }
                 $('div.modal-footer button[data-dismiss="modal"]').on("click", function(){
                       location.reload();

                 });
                 ErrorMessage.show_html(html);
                 Status.hide();
                 return ;
             }else{
                 location.reload();
             }

          }
          if(response.data["state"]=="failed"){
                 var data = response.data;
                 var html = "";
                 if (data['errors']){
                    for(var i=0; i<data['errors'].length; i++){
                      var error = data['errors'][i];
                      html += '\n' + error['message'] + ':\n' + error['traceback'];
                    }
                 }
                 $('div.modal-footer button[data-dismiss="modal"]').on("click", function(){
                       window.location.href = "/settings/";

                 });
                 ErrorMessage.show_html(html);
                 Status.hide();
                 return ;
          }




          Status.show( response.data["message"]);
          callback();

        }
      );




    },
    reload_state:function(){
        WaitCore.core_state(function(){
               setTimeout(WaitCore.reload_state, 500);
          });
    },
    init:function(){
          Status.show("Core is not ready");
          window.WaitCore.reload_state();
    }


  };
  window.WaitCore.init();

});
