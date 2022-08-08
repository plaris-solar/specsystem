import { createWebHistory, createRouter } from "vue-router";
import HomePage from "@/views/home.vue";
import CategoryPage from "@/views/category/CategoryMain.vue"
import RolePage from "@/views/role/RoleMain.vue"
import SpecPage from "@/views/spec/SpecMain.vue"
import TokenPage from "@/views/token/TokenMain.vue"

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage,
  },
  {
    path: '/ui-cat',
    name: 'Category',
    component: CategoryPage
  },
  {
    path: '/ui-token',
    name: 'Token',
    component: TokenPage
  },
  {
    path: '/ui-role',
    name: 'Role',
    component: RolePage
  },
  {
    path: '/ui-spec',
    name: 'Spec',
    component: SpecPage
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;