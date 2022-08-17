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
                Pages
            </h4>
            <div class="col-md-auto scroll-box" style="background: rgba(0, 0, 0, 0.05);text-align: center;">
                <q-scroll-area class="scroll-box">
                    <div class="column inline page-select-col">
                        <li v-for="(item, key) in docs.slice(0, docs.length/3)" :key="key" class="page-select">
                            <q-btn size="xl" @click="router.push('/ui-data/' + item)" :data-cy="item">{{item}}</q-btn>
                        </li>
                    </div>
                    <div class="column inline page-select-col" >
                        <li v-for="(item, key) in docs.slice(docs.length/3, 2*(docs.length/3))" :key="key" class="page-select">
                            <q-btn size="xl" @click="router.push('/ui-data/' + item)" :data-cy="item">{{item}}</q-btn>
                        </li>
                    </div>
                    <div class="column inline page-select-col" >
                        <li v-for="(item, key) in docs.slice(2*(docs.length/3), docs.length)" :key="key" class="page-select">
                            <q-btn size="xl" @click="router.push('/ui-data/' + item)" :data-cy="item">{{item}}</q-btn>
                        </li>
                    </div>
                </q-scroll-area>
            </div>
            
        </div>
    </q-page>
</template>

<script>

import { useRouter } from 'vue-router';
import {ref, computed} from 'vue'
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
    const router = ref(useRouter())
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