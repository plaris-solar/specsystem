<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="col-4"/>
            <div class="text-h4 col-4 text-center">Create Token</div>
            <div class="col-4 text-right">             
                <q-btn icon="close" flat round dense data-cy="token-create-close" v-close-popup /> 
            </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Username" v-model="user" @keydown.enter.prevent="createToken()" data-cy="token-create-user"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Create" color="primary" icon="save" @click="createToken()" data-cy="token-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" icon="cancel" v-close-popup data-cy="token-create-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { postData } from '@/utils.js'
import {ref, defineEmits} from 'vue'

export default {
    name: 'CreateTokenDialog',
}
</script>

<script setup>

    const emit = defineEmits(['newToken'])

    const user = ref('')

    async function createToken(){
        await postData(`auth/token/${user.value}`, {}, 'Successfully created token for ' + user.value).then(() => emit('newToken'))
    }


</script>

<style scoped>
.dialog_window{
    max-width: 50vw;
    width: 50vw;
}

.spacer{
    width: 2vw;
}
</style>
