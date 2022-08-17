<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">{{props.createMode?'Create':'Update '+props.doctypeRow['name']}} Doc Type</div>
            <q-btn icon="close" flat round dense data-cy="token-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Name" v-model.trim="doctype" v-show="props.createMode" data-cy="doctype-create-doctype"/>
            <q-input label="Description" v-model.trim="descr" data-cy="descr-create-doctype"/>
            <q-select label="Confidential" v-model="confidential" 
                :options="[{label:'True',value:true}, {label:'False',value:false}]"
                data-cy="confidential-create-doctype"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveDoctype()" data-cy="token-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" v-close-popup data-cy="token-create-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { defineProps, postData, putData } from '@/utils.js'
import {ref, defineEmits, onMounted} from 'vue'

export default {
    name: 'CreateDoctypeDialog',
}
</script>

<script setup>    
    const props = defineProps({
        doctypeRow: Object,
        createMode: Boolean,
    })

    const emit = defineEmits(['updateTable'])

    const doctype = ref('')
    const descr = ref('')
    const confidential = ref({label:'False',value:false})

    async function saveDoctype(){
        const body = {
            name: doctype.value,
            descr: descr.value,
            confidential: confidential.value.value,
        }

        if (props.createMode) {
            let res = await postData('doctype/', body, 'Successfully created doctype ' + doctype.value)
            if (res.status < 300){
                emit('updateTable')
            }
        }
        else {
            let res = await putData(`doctype/${doctype.value}`, body, 'Successfully updated doctype ' + doctype.value)
            if (res.status < 300){
                emit('updateTable')
            }
        }
    }

    onMounted(() => {
        if (props.doctypeRow['name'] !== undefined) {
            doctype.value = props.doctypeRow['name']
            descr.value = props.doctypeRow['descr']
            if (props.doctypeRow['confidential']) {confidential.value = {label:'True',value:true}} else {confidential.value={label:'False',value:false}}
        }
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
