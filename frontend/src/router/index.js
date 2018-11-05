import Vue from 'vue';
import Router from 'vue-router';
import Bikeshare from '@/components/Bikeshare';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Bikeshare',
      component: Bikeshare,
    },
  ],
});
