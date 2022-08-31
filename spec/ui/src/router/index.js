import { createWebHistory, createRouter } from "vue-router";
import HomePage from "@/views/home.vue";
import ApprovalMatrixPage from "@/views/approvalMatrix/ApprovalMatrixMain.vue"
import DepartmentPage from "@/views/department/DepartmentMain.vue"
import DocTypePage from "@/views/doctype/DocTypeMain.vue"
import RolePage from "@/views/role/RoleMain.vue"
import SpecDetailPage from "@/views/spec/SpecDetail.vue"
import SpecPage from "@/views/spec/SpecMain.vue"
import TokenPage from "@/views/token/TokenMain.vue"
import UserDetailPage from "@/views/user/UserDetail.vue"

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomePage,
  },
  {
    path: '/ui-apvl-mt',
    name: 'ApprovalMatrix',
    component: ApprovalMatrixPage
  },
  {
    path: '/ui-token',
    name: 'Token',
    component: TokenPage
  },
  {
    path: '/ui-doctype',
    name: 'Document Type',
    component: DocTypePage
  },
  {
    path: '/ui-role',
    name: 'Role',
    component: RolePage
  },
  {
    path: '/ui-dept',
    name: 'Department',
    component: DepartmentPage
  },
  {
    path: '/ui-spec',
    name: 'Spec',
    component: SpecPage
  },
  {
    path: '/ui-spec/:num/:ver?',
    name: 'Spec Detail',
    component: SpecDetailPage,
    props: true,
  },
  {
    path: '/ui-user/:username',
    name: 'User Detail',
    component: UserDetailPage,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;