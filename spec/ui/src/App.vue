<template>
  <q-layout view="lHh lpr lff">
    <q-header elevated :class="env_color">
      <q-toolbar>
        <div class="col-md-auto">
        <q-toolbar-title class="text-center">
          <q-btn no-caps @click="router.push('/')">
            <header class="page-header" data-cy="app-title">
              {{ route.name }}
            </header>
          </q-btn>
          
        </q-toolbar-title>

          <div class="q-pa-md inline" v-show="!authenticated">
            <q-btn color="positive" 
                    :disable="authenticated"
                    label="Login"
                    size="1vw"
                    @click="login = true"
                    data-cy="app-login-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline" v-show="authenticated">
            <q-btn color="negative" 
                    :disable="!authenticated"
                    label="Logout"
                    size="1vw"
                    @click="logout()"
                    data-cy="app-logout-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline" v-show="isAdmin">
            <q-btn color="secondary"
                    :disable="!authenticated"
                    label="API Tokens"
                    size="1vw"
                    @click="router.push('/ui-token/')"
                    data-cy="app-admin-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="secondary"
                    label="Document Types"
                    size="1vw"
                    @click="router.push('/ui-doctype/')"
                    data-cy="app-doctype-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="secondary"
                    label="Roles"
                    size="1vw"
                    @click="router.push('/ui-role/')"
                    data-cy="app-role-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="secondary"
                    label="Departments"
                    size="1vw"
                    @click="router.push('/ui-dept/')"
                    data-cy="app-dept-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="secondary"
                    label="Approval Matrix"
                    size="1vw"
                    @click="router.push('/ui-apvl-mt/')"
                    data-cy="app-apvl-mt-btn">
            </q-btn>
          <div class="q-pa-md inline">
            <q-btn color="primary"
                    label="Specs"
                    size="1vw"
                    @click="router.push('/ui-spec/')"
                    data-cy="app-spec-btn">
            </q-btn>
          </div>
          </div>
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view
        :key="route.fullPath"
      >
      </router-view>
    </q-page-container>

    <q-dialog v-model="login">
      <login-popup-page @close="login=false"/>
    </q-dialog >
  </q-layout>
</template>

<script>
import LoginPopupPage from '@/components/LoginPopup.vue'
import {
  retrieveData
} from './utils';

import {ref, onMounted, watch, computed} from 'vue';
import {useStore} from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'LayoutDefault',
  components: {
    LoginPopupPage
  }
}
</script>


<script setup>
  const router = useRouter()
  const route = useRoute()

  const store = useStore()

  const login = ref(false)

  const data_page = ref()

  const env_color = ref()

  const authenticated = ref(computed(() => store.getters.authenticated))
  const isAdmin = ref(computed(() => store.getters.isAdmin))


  if (!env_color.value){
    set_app_color()
  }

  onMounted(() => {
    if (authenticated.value) {
      store.dispatch('getPermission');
    }
    if (route.params.doc_type){
      data_page.value = route.params.doc_type
    }
  })

  watch(() => route.path, (new_param, old_param) => {
      data_page.value = null
  })

  watch(authenticated, (newVal, oldVal) => {
      if (newVal) {
        store.dispatch("getPermission");
      } 
    })

  async function set_app_color(){
    let resp = await retrieveData('env/')
    env_color.value = resp === 'Test' ? 'glossy bg-purple' : 'glossy bg-primary'
  }

  async function logout(){
    logout.value = false;
    store.dispatch('logout');
  }
</script>

<style lang="scss">

.page-select {
  padding: 5px 10px;
  background-color: "white";
}

.page-header {
  font-size: 2vw;
  padding: .5em;
}

.select-text {
  font-size: 20px;
}

.tool-btn {
  font-size: 2vw;
  padding: 1em;
}

.inline {
  display:inline;
}

</style>
