<template>
    <q-page class="flex center">
        <div v-show="!authenticated">
            <login-page/>
        </div>

        <div v-show="authenticated">
            <span class="row home-header">
                <h3 class="center">
                    Welcome to the Spec System!
                </h3>
            </span>
            <h4 class="flex center">
                Home
            </h4>
        </div>
    </q-page>
</template>

<script>

import { computed} from 'vue'
import { useStore } from 'vuex'
import LoginPage from '@/components/Login.vue'

export default {
  name: 'HomePage',
  props: {
      docs: Array,
  },
  components: {
        LoginPage,
    },

}
</script>

<script setup>
    const store = useStore()

    const authenticated = computed(() => store.getters.authenticated)
</script>


<style scoped>

.page-select-col {
    width: 33%;
}

.page-select {
    padding-top: 1em;
}

.scroll-box {
    height: 60vh; 
    width: 90vw;
}

li {
    list-style-type: none;
}

.page-btns {
    margin: 1em;
}

h4 {
    margin-top: 5vh;
    margin-bottom: 1vh;
}

.home-header{
    display: inline
}

.data-btns-background{
    width: 75vw; 
    background: rgba(0, 0, 0, 0.05); 
    text-align: center;
}

.center{
    justify-content: center;
    text-align: center;
}
</style>