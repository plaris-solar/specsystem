<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h5">{{props.username}}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
            <q-input label="Delegates" v-model.trim="delegates" data-cy="user-detail-delegates" dense />
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
            <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveUser()" data-cy="spec-detail-update"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { defineProps, putData, retrieveData, } from '@/utils.js'
import {ref, onMounted} from 'vue'

export default {
    name: 'UserDetailPage',
}
</script>

<script setup>    
    const props = defineProps({
        username: String,
    })

    const delegates = ref('')

    async function saveUser(){
        const body = {
            delegates:delegates.value,
        }

        let res = await putData(`user/${props.username}`, body, 
            'Successfully updated user ' + props.username)
    }

    async function loadData() {
        let res = await retrieveData(`user/${props.username}`);
        delegates.value = res['delegates']
    }

    onMounted(() => {
        loadData()
    })
</script>

<style scoped>
.filter-btn {
    width: 5em;
    margin-bottom: 2vh;
}

.dialog_window{
    max-width: 50vw;
    width: 50vw;
}

.spacer{
    width: 2vw;
}
</style>
