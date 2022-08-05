<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">{{props.createMode?'Create':'Update '+props.categoryRow['category']}} Category</div>
            <q-btn icon="close" flat round dense data-cy="token-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-input label="Category" v-model.trim="cat" v-if="props.createMode" data-cy="cat-create-category"/>
            <q-input label="Sub Category" v-model.trim="sub_cat" v-if="props.createMode" data-cy="sub_cat-create-category"/>
            <q-input label="Description" v-model.trim="descr" data-cy="descr-create-category"/>
            <q-select label="Active" v-model="active" 
                :options="[{label:'True',value:true}, {label:'False',value:false}]"
                data-cy="active-create-category"/>
            <q-select label="Confidential" v-model="confidential" 
                :options="[{label:'True',value:true}, {label:'False',value:false}]"
                data-cy="confidential-create-category"/>
            <q-input label="File Template" v-model.trim="file_temp"  data-cy="file_temp-create-category"/>
            <q-input label="Jira Template" v-model.trim="jira_temp"  data-cy="jira_temp-create-category"/>
            <q-input label="Required Roles" v-model.trim="roles"  data-cy="roles-create-category"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveCategory()" data-cy="category-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" v-close-popup data-cy="category-create-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { defineProps, postData, putData } from '@/utils.js'
import {ref, defineEmits, onMounted} from 'vue'

export default {
    name: 'CreateCategoryDialog',
}
</script>

<script setup>    
    const props = defineProps({
        categoryRow: Object,
        createMode: Boolean,
    })

    const emit = defineEmits(['updateTable'])

    const cat = ref('')
    const sub_cat = ref('')
    const descr = ref('')
    const active = ref(false)
    const confidential = ref(false)
    const file_temp = ref('')
    const jira_temp = ref('')
    const roles = ref('')

    async function saveCategory(){
        const body = {
            cat: cat.value,
            sub_cat: sub_cat.value,
            descr: descr.value,
            active: active.value.value,
            confidential: confidential.value.value,
            file_temp: file_temp.value,
            jira_temp: jira_temp.value,
            roles: roles.value
        }

        if (props.createMode) {
            let res = await postData('category/', body, 'Successfully created category ' + cat.value + '/' + sub_cat.value)
            console.log(`res`)
            if (res.status < 300){
                emit('updateTable')
            }
        }
        else {
            let res = await putData(`category/${cat.value}/${sub_cat.value}`, body, 'Successfully updated category ' + cat.value + '/' + sub_cat.value)
            if (res.status < 300){
                emit('updateTable')
            }
        }
    }

    onMounted(() => {
        cat.value = props.categoryRow['cat']
        sub_cat.value = props.categoryRow['sub_cat']
        descr.value = props.categoryRow['descr']
        if (props.categoryRow['active']) {active.value = true} else {active.value=false}
        if (props.categoryRow['confidential']) {confidential.value = true} else {confidential.value=false}
        file_temp.value = props.categoryRow['file_temp']
        jira_temp.value = props.categoryRow['jira_temp']
        roles.value = props.categoryRow['roles']
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
