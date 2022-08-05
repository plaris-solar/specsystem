import { createWebHistory, createRouter } from "vue-router";
import HomePage from "@/views/home.vue";
import CategoryPage from "@/views/category/CategoryMain.vue"
import DocPage from "@/views/docs/DocMain.vue"
import DocDetailPage from "@/views/docs/DocDetail.vue"
import DataPage from "@/views/data/DataMain.vue"
import RolePage from "@/views/role/RoleMain.vue"
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
    path: '/ui-docs',
    name: 'Data Management',
    component: DocPage,
  },
  {
    path: '/ui-doc-detail/:doc_type?',
    name: 'Management',
    component: DocDetailPage,
  },
  {
    path: '/ui-data/:doc_type?',
    name: 'Data',
    component: DataPage
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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;