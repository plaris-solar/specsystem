<template>
  <q-layout view="lHh lpr lff">
    <q-header elevated :class="env_color">
      <q-toolbar>
        <div class="col">
          <q-chip size="lg" >
            <q-select borderless 
                    :options="display_docs"
                    v-model= "data_page"
                    use-input
                    input-debounce="0"
                    color="blue"
                    label="Select Page"
                    class="q-pa-sm text-h6"
                    clearable 
                    @filter="filterFn"
                    v-bind:input-style="{width: data_page ? 0: null}"
                    data-cy="app-doc-select"
                    @update:model-value="toData(data_page)">
            </q-select>
          </q-chip>
        </div>
        <div class="col-md-auto">
        <q-toolbar-title class="text-center">
          <q-btn no-caps @click="router.push('/')">
            <header class="page-header" data-cy="app-title">
              {{ route.name }}
            </header>
          </q-btn>
          
        </q-toolbar-title>
        </div>
        <div class="col text-right">
          <div class="q-pa-md inline" >
            <q-btn :disable="!authenticated" color="secondary" label="Upload Data" size="1vw" @click="upload_csv = true" data-cy="app-upload-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="secondary" 
                    label="Manage Data"
                    :disable="!authenticated"
                    @click="toDataManagement()"
                    size="1vw"
                    data-cy="app-management-btn">
            </q-btn>
          </div>

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
          <div class="q-pa-md inline" v-if="isSupervisor">
            <q-btn color="brown"
                    :disable="!authenticated"
                    label="Admin"
                    size="1vw"
                    @click="router.push('/ui-token/')"
                    data-cy="app-admin-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="brown"
                    label="Roles"
                    size="1vw"
                    @click="router.push('/ui-role/')"
                    data-cy="app-role-btn">
            </q-btn>
          </div>
          <div class="q-pa-md inline">
            <q-btn color="brown"
                    label="Categories"
                    size="1vw"
                    @click="router.push('/ui-cat/')"
                    data-cy="app-cat-btn">
            </q-btn>
          </div>
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view
        :docs="docs"
        :key="route.fullPath"
        :rerender="upload_csv"
        @update_doc="getDocList()">
      </router-view>
    </q-page-container>
    <q-dialog v-model="upload_csv">
      <upload-csv-window
          :docs="docs"
          :doc_type="route.params.doc_type"
          @csvUpload="closeCsvPopup"
          data-cy="app-upload-window"/>
    </q-dialog >
    <q-dialog v-model="login">
      <login-popup-page @close="login=false"/>
    </q-dialog >
  </q-layout>
</template>

<script>
import uploadCsvWindow from '@/components/uploadCsv.vue'
import LoginPopupPage from '@/components/LoginPopup.vue'
import {
  doc_list,
  retrieveData
} from './utils';

import {ref, onMounted, watch, computed} from 'vue';
import {useStore} from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'LayoutDefault',
  components: {
    uploadCsvWindow,
    LoginPopupPage
  }
}
</script>


<script setup>
  const router = useRouter()
  const route = useRoute()

  const store = useStore()

  const upload_csv = ref(false)
  const login = ref(false)

  const display_docs = ref([])
  const docs = ref([])
  const data_page = ref()

  const env_color = ref()

  const authenticated = ref(computed(() => store.getters.authenticated))
  const isSupervisor = ref(computed(() => store.getters.isSupervisor))


  if (!env_color.value){
    set_app_color()
  }

  onMounted(() => {
    getDocList();
    if (authenticated.value) {
      store.dispatch('getPermission');
    }
    if (route.params.doc_type){
      data_page.value = route.params.doc_type
    }
  })

  watch(() => route.path, (new_param, old_param) => {
    if (route.path.includes('ui-data')){
      data_page.value = route.params.doc_type
    }
    else{
      data_page.value = null
    }
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

  async function getDocList() {
    docs.value = await doc_list();
    display_docs.value = docs.value;

  }

  function closeCsvPopup(){
    upload_csv.value = false;
  }

  function filterFn (val, update) {
    if (val === ''){
      update(() => {
        display_docs.value = docs.value;
      })
      return;
    }
    update(() => {
      const needle = val.toUpperCase()
      display_docs.value = docs.value.filter(v => v.toUpperCase().indexOf(needle) > -1)
    })
  }

  function toData(val){
    if (val){
      router.push('/ui-data/' + val)
    }
  }

  function toDataManagement() {
    router.push('/ui-docs')
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
