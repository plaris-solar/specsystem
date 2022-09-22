<template>
  <q-page class="flex flex-center" >
    <div class="col">
        <q-input
          class="username"
          label="username"
          v-model="username"
          data-cy="login-username-input"/>
        <div class="spacer-large"/>
        <q-input v-model="password" :type="is_pwd ? 'password' : 'text'" label="password" data-cy="login-password-input">
          <template v-slot:append>
            <q-icon
              :name="is_pwd ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click="is_pwd = !is_pwd"
            />
          </template>
        </q-input>
        <div class="text-center spacer"/>
        <div class="text-center">
        <q-btn label="Login" @click="login" color="primary" icon="login" data-cy="login-login-btn"/>
        <div class="spacer-xl"/>
        </div>
    </div>

  </q-page>
</template>

<script>
import {ref, onMounted, watch, computed, defineEmits, defineProps} from 'vue'
import { useStore } from 'vuex'
import {apiServerHost, getCookie} from '@/utils.js'

export default {
    name: 'LoginPage'
}
</script>

<script setup>
    const store = useStore()

    const username = ref()
    const password = ref()
    const csrf = ref()
    
    const is_loggin_in = ref(false)
    const is_pwd = ref(true)

    const authenticated = ref(computed(() => store.getters.authenticated))

    const emit = defineEmits(['close'])

    const props = defineProps({
        isPopUp: Boolean,
    })

    onMounted(() => {
      window.addEventListener('keypress', handleKeyPress);
    })

    watch(authenticated, (newVal, oldVal) => {
      if (newVal) {
        window.removeEventListener('keypress', handleKeyPress);
        store.dispatch("getPermission");
        username.value = null;
        password.value = null;
      } 
      else {
        window.addEventListener('keypress', handleKeyPress);
      }
    })

    function handleKeyPress(e) {
      if (is_loggin_in.value) return;
      if (e.key === 'Enter') {
        login();
      }
    }

    async function login(){
      if (!authenticated.value){
        is_loggin_in.value = true
        var loginForm = new FormData()
        await setCSRFToken().then((tok) => {
          loginForm.append('csrfmiddlewaretoken', csrf.value)
          loginForm.append('username', username.value)
          loginForm.append('password', password.value)
        })
        await store.dispatch("login", {
            form: loginForm,
          });
        is_loggin_in.value = false;
        if (authenticated.value & props.isPopUp){
          emit('close')
        }
      }
    }

    async function setCSRFToken() {
      await window.fetch(apiServerHost + "/accounts/login/");
      csrf.value = getCookie("csrftoken")
    }
</script>

<style scoped>
.username{
  width: 30vw
}

.spacer{
   height: 3vh
}

.spacer-large{
  height: 6vh
}

.spacer-xl{
  height: 40vh
}
</style>