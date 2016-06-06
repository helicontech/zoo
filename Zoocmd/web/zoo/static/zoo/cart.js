$(document).ready(function () {
  window.Cart = {

    $panel: $('#cart-panel'),
    $install_button: $('#cart-install'),
    $uninstall_button: $('#cart-uninstall'),

    $clear_button: $('#cart-clear'),

    add_product: function (product_name, type_action) {
      var cart = this.get_cart(type_action);
      if ($.inArray(product_name, cart) == -1){
        cart.push(product_name);
        this.set_cart(cart, type_action);
        this.update_panel();
      }
    },

    remove_product: function (product_name, type_action) {
      var cart = this.get_cart(type_action);
      var index = cart.indexOf(product_name);
      if (index >= 0){
        cart.splice(index, 1);
        this.set_cart(cart, type_action);
        this.update_panel();
      }
    },

    update_panel: function () {
      var items2install = this.get_cart("install")
      var items2uninstall = this.get_cart("uninstall");
      var uninstall_check =  (items2uninstall && items2uninstall.length > 0);
      var install_check =  (items2install && items2install.length > 0)

      this.$install_button.hide();
      this.$uninstall_button.hide();
      if(install_check) {
        this.$install_button.show();
        this.$install_button.find('>span').text('Install '+items2install.length+' products');
      }
      if (uninstall_check) {
        this.$uninstall_button.show();
        this.$uninstall_button.find('>span').text('Uninstall '+items2uninstall.length+' products');

      }

      if( install_check ||  uninstall_check){
         this.$panel.show();
      }else{
         this.$panel.hide();
      }

    },

    clear: function(){
      $.removeCookie('zoo_cart_install');
      $.removeCookie('zoo_cart_uninstall');
      Cart.update_panel();
      Gallery.select_products([],[]);
    },

    get_cart: function(type_action){
      var s = $.cookie('zoo_cart_'+type_action);
      if (s){
        return s.split(';');
      } else {
        return [];
      }
    },

    set_cart: function(list, type_action){
      if (list && list.length>0) {
        $.cookie('zoo_cart_'+type_action, list.join(';'));
      } else {
        $.removeCookie('zoo_cart_'+type_action);
      }
    },
    install_application: function(Application){
        window.location.href = '/install/application/?back='+Gallery.back+'&products=' + Application;
    },
    click_install: function(ev){
      var cart = Cart.get_cart("install");
      if (cart && cart.length>0){
        Cart.clear();
        Gallery.save_state();
        window.location.href = '/install/?back='+Gallery.back+'&products='+cart.join(';');
      }
    },
    uninstall: function(ev){
      var cart = Cart.get_cart("uninstall");
      if (cart && cart.length>0){
        Gallery.save_state();
        Cart.clear();
        window.location.href = '/uninstall/?back='+Gallery.back+'&products='+cart.join(';');
      }
    },

    init: function () {
      this.$clear_button.click(this.clear);
      this.$install_button.click(this.click_install);
      this.$uninstall_button.click(this.uninstall);
    }
  };

  window.Cart.init();
});

