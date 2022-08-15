<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">Create Spec</div>
            <q-btn icon="close" flat round dense data-cy="spec-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-select
                label="Doc Type"
                v-model="doc_type"
                :options="doc_typeList"
                emit-value
                data-cy="spec-create-doc_type"
            />
            <q-select
                label="Department"
                v-model="department"
                :options="deptList"
                emit-value
                data-cy="spec-create-department"
            />
            <q-input label="Title" v-model.trim="title" data-cy="spec-create-title"/>
        </q-card-section>

        <q-card-actions class="bg-white text-teal" align="center">
          <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveSpec()" data-cy="spec-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" size="lg" class="filter-btn" v-close-popup data-cy="spec-create-cancel"/>
        </q-card-actions>
    </q-card>
</template>

<script>
import { notifyResponse, postData, retrieveData, } from '@/utils.js'
import {ref, onMounted} from 'vue'
import {useRouter, } from 'vue-router'

export default {
    name: 'CreateSpecDialog',
}
</script>

<script setup>    
    const department = ref('')
    const deptList = ref([])
    const doc_type = ref('')
    const doc_typeList = ref([])
    const router=useRouter();
    const title = ref('')

    async function saveSpec(){
        const body = {
            title: title.value,
            doc_type: doc_type.value,
            department: department.value,
            sigs:[],
            files:[],
            refs:[],
        }


        let res = await postData('spec/', body, null)
        console.log(`res`)
        if (res.status < 300){
            let body = await res?.json()
            notifyResponse(res, `Spec created: ${body.num}/${body.ver}`)
            router.push({name:"Spec Detail", params:{num:body.num, ver:body.ver}})
        } else {
            notifyResponse(res, ' ')
        }
    }

    onMounted(() => {
        loadLists()
    })

    async function loadLists() {
        let data_rows = await retrieveData('doctype/?limit=1000');
        doc_typeList.value = data_rows['results'].map((e) => {return ({label:e['name'],value:e['name']})})
        
        data_rows = await retrieveData('dept/?limit=1000');
        deptList.value = data_rows['results'].map((e) => {return ({label:e['name'],value:e['name']})})
    }
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
