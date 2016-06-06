$(document).ready(function () {
  window.Sync = {

    init: function () {
      ZooApi.get(
        ZooApi.Urls.sync,
        {},
        function(response){
          var task = response.data.task;
          console.log('sync task created with id ', task.id);
          window.location.href = task.url;
        }
      )
    }

  };

  window.Sync.init();
});

