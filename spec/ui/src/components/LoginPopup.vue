<template>
    <q-card class="scroll">
        <q-card-section class="bg-primary text-white row ">
            <div class="col-4"/>
            <div class="text-h4 col-4 text-center">Login</div>
            <div class="col-4 text-right">             
                <q-btn icon="close" flat round dense v-close-popup="authenticated" /> 
            </div>
        </q-card-section>
        <q-card-section  >
            <login-page :isPopUp="true" @close="emit('close')" class=" column"/>
        </q-card-section>
    </q-card>
</template>

<script>
import LoginPage from '@/components/Login.vue'
import { defineEmits } from 'vue'

export default {
    name: "LoginPopupPage",
    components: {
        LoginPage
    }
}
</script>

<script setup>
    const emit = defineEmits(['close'])
</script>

<style  scoped>
.scroll {
    overflow: hidden;
    max-width: 60vw;
    height:25em;
}
</style>