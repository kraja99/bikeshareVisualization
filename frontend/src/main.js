// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import * as VueGoogleMaps from 'vue2-google-maps';
import App from './App';
import router from './router';

Vue.use(BootstrapVue);

Vue.use(VueGoogleMaps, {
  load: {
    key: process.env.GMAP_KEY,
  },
});

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: {
    App,
  },
});
