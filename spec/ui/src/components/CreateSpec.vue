<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">Create Spec</div>
            <q-btn icon="close" flat round dense data-cy="token-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Category" v-model.trim="cat" v-if="props.createMode" data-cy="cat-create-spec"/>
            <q-input label="Sub Category" v-model.trim="sub_cat" v-if="props.createMode" data-cy="sub_cat-create-spec"/>
            <q-input label="Title" v-model.trim="title" data-cy="title-create-spec"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveSpec()" data-cy="spec-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" v-close-popup data-cy="spec-create-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { defineProps, notifyResponse, postData, } from '@/utils.js'
import {ref, defineEmits, onMounted} from 'vue'

export default {
    name: 'CreateSpecDialog',
}
</script>

<script setup>    
    const props = defineProps({
        specRow: Object,
        createMode: Boolean,
    })

    const emit = defineEmits(['updateTable'])

    const cat = ref('')
    const sub_cat = ref('')
    const title = ref('')

    async function saveSpec(){
        const body = {
            cat: cat.value + '/' + sub_cat.value,
            title: title.value,
            sigs:[],
            files:[],
            refs:[],
        }


        let res = await postData('spec/', body, null)
        console.log(`res`)
        if (res.status < 300){
            let body = await res?.json()
            notifyResponse(res, `Spec created: ${body.num}/${body.ver}`)
            emit('updateTable')
        } else {
            notifyResponse(res, ' ')
        }
    }

    onMounted(() => {
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
