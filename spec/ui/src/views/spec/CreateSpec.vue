<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h4">Create Spec</div>
            <q-btn icon="close" flat round dense data-cy="spec-create-close" v-close-popup /> 
        </q-card-section>
        <q-card-section class="q-pt-none">
            <q-select
                label="Document Type"
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
          <q-btn label="Save" color="primary" icon="save" @click="saveSpec()" data-cy="spec-create-create"/>
          <div class="spacer"/>
          <q-btn label="Cancel" color="red" icon="cancel" v-close-popup data-cy="spec-create-cancel"/>
        </q-card-actions>

        <q-dialog v-model="waiting" no-esc-dismiss no-backdrop-dismiss>
            <q-card>
                <q-card-section align="center">
                    <h4>Creating new spec. Please wait</h4>
                    <p>This may take a minute while the Spec and Jira stories are created.</p>
                    <br/>
                    <p>Do not refresh the page.</p>
                </q-card-section>
            </q-card>
        </q-dialog>
    </q-card>
</template>

<script>
import { postData, retrieveData, showNotif, } from '@/utils.js'
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
    const waiting = ref(false)
    const title = ref('')

    async function saveSpec(){
        waiting.value = true
        const body = {
            state: 'Draft',
            title: title.value,
            doc_type: doc_type.value,
            department: department.value,
            sigs:[],
            files:[],
            refs:[],
        }


        let res = await postData('spec/', body, null)
        if (res.__resp_status < 300) {
            showNotif(`Spec created: ${res.num}/${res.ver}`, 'green')
            router.push({name:"Spec Detail", params:{num:res.num, ver:res.ver}})
        }
        
        waiting.value = false
    }

    onMounted(() => {
        waiting.value = false
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

.dialog_window{
    max-width: 50vw;
    width: 50vw;
}

.spacer{
    width: 2vw;
}
</style>
