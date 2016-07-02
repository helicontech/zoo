$(document).ready(function () {
  window.Engine = {

    $modal: $('#modal-engine'),
    engine_properties_template: Handlebars.compile($('#engine-properties-template').html()),

    engine: null,


    show: function (engine) {
      this.engine = engine;
      this.$modal.find('.modal-title').text(engine.title + ' Properties');
      this.$modal.find('.modal-body').html(
        this.engine_properties_template(engine)
      );
      var params = Common.clone_end_remove_keys(engine.config, ['enabled', 'environment_variables']);
      this.$modal.find('#engine-parameters-grid').html(Grid.render_edit_keys_values(params));
      Grid.connect_events("#engine-parameters-grid");

      this.$modal.find('#engine-environment').html(Grid.render_edit_keys_values(engine.config.environment_variables));
      Grid.connect_events("#engine-environment");
      this.$modal.modal('show');
    },

    save: function(){

      var config = Grid.get_params(this.$modal.find('#engine-parameters-grid'));
      config['environment_variables'] = Grid.get_params(this.$modal.find('#engine-environment'));
      config['enabled'] = this.$modal.find('#engine-enabled').is(':checked');

      console.log('saving engine config', config);
      this.$modal.modal('hide');

      Status.show('Saving engine');
      ZooApi.post(
        ZooApi.Urls.engine + this.engine.name + '/config/',
        config,
        function(response){
          var engine = response.data;
          console.log(engine);
          Status.hide();

          // hack: save updated engine in gallery cache
          Gallery.cache[engine.name] = engine;
        }
      );
    },

    init: function(){
      this.$modal.modal({
        keyboard: true,
        show: false
      });
      this.$modal.find('.btn.save').click(function(){
        Engine.save();
      });
    }
  };

  Engine.init();

});

