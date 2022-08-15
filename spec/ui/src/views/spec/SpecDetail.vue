<template>
  <q-card class="dialog-window">
        <q-card-section class="bg-primary text-white row ">
            <div class="text-h5">{{props.num}}/{{props.ver}} - {{state}}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
            <q-select
                label="Doc Type"
                v-model="doc_type"
                :options="doc_typeList"
                emit-value
                dense :readonly="!edit"
                data-cy="spec-detail-doc_type"
            />
            <q-select
                label="Department"
                v-model="department"
                :options="deptList"
                emit-value
                dense :readonly="!edit"
                data-cy="spec-detail-department"
            />
            <q-input label="Title" v-model.trim="title" data-cy="spec-detail-title" dense :readonly="!edit"/>
            <q-input label="Keywords" v-model.trim="keywords" data-cy="spec-detail-keywords" dense :readonly="!edit"/>

            Jira: <a :href="jira" target="_blank" rel="noopener noreferrer">{{String(jira).substring(String(jira).lastIndexOf('/')+1)}}</a>
            <q-input label="Jira" v-model.trim="jira" data-cy="spec-detail-jira" dense :readonly="!edit"/>
        </q-card-section>

        <q-card-section class="q-pt-none">
            Signatures:
            <q-table
                :rows="sigRows"
                hide-bottom
                data-cy="spec-detail-sigs">
                <template v-slot:top-left v-if="edit">
                    <q-btn color="primary" dense
                        @click="sigRows.push({_new:true})"
                        icon-right="add" size="xs"
                        no-caps
                        data-cy="add_sig-btn"
                        v-if="edit">
                    </q-btn>
                </template>
                <template v-slot:header>
                    <q-th v-if="edit"/>
                    <q-th>Role</q-th>
                    <q-th>Signer</q-th>
                    <q-th>Signed</q-th>
                    <q-th>By</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td v-if="edit">
                            <q-btn round color="negative" 
                                    @click="deleteSig(tprops.row)"
                                    icon="delete" size="xs" dense
                                    data-cy="data-delete-btn"
                                    v-if="!tprops.row['from_am']">
                            </q-btn>
                        </q-td>
                        <q-td v-if="!tprops.row['_new']" style="white-space: nowrap;">
                            {{tprops.row["role"]}}
                            <span  v-if="tprops.row['spec_one']">*</span></q-td>
                        <q-td v-else>   
                            <q-select
                                v-model="tprops.row['role']"
                                :options="roleList"
                                emit-value
                                dense :readonly="!edit"
                            />                     
                        </q-td>
                        <q-td>   
                            <q-input
                                v-model="tprops.row['signer']" 
                                :data-cy="genCy(`signer`, tprops.row['signer'])"
                                dense borderless :readonly="!edit"/>                        
                        </q-td>
                        <q-td>{{tprops.row["signed_dt"]}}</q-td>
                        <q-td>{{tprops.row["delgate"]}}</q-td>
                    </q-tr>
                </template>
           </q-table>
        </q-card-section>
        
        <q-card-section class="q-pt-none">
            References:
            <q-table
                :rows="refRows"
                hide-bottom
                data-cy="spec-detail-refs">
                <template v-slot:top-left v-if="edit">
                    <q-btn color="primary" dense
                        @click="refRows.push({_new:true})"
                        icon-right="add" size="xs"
                        no-caps
                        data-cy="add_ref-btn"
                        v-if="edit">
                    </q-btn>
                </template>

                <template v-slot:header>
                    <q-th v-if="edit"/>
                    <q-th>Num</q-th>
                    <q-th>Ver (optional)</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td v-if="edit">
                            <q-btn round color="negative" 
                                    @click="deleteRef(tprops.row)"
                                    icon="delete" size="xs" dense
                                    data-cy="ref-delete-btn">
                            </q-btn>
                        </q-td>
                        <q-td>
                            <q-input v-model.trim="tprops.row['num']" type="number" data-cy="spec-detail-ref-num" dense borderless :readonly="!edit"/>
                        </q-td>                        
                        <q-td>
                            <q-input v-model.trim="tprops.row['ver']" data-cy="spec-detail-ref-ver" dense borderless :readonly="!edit"/>
                        </q-td>
                    </q-tr>
                </template>
           </q-table>
        </q-card-section>
        
        <q-card-section class="q-pt-none">
            Files:
            <q-table
                :rows="fileRows"
                hide-bottom
                data-cy="spec-detail-files">
                <template v-slot:header>
                    <q-th v-if="edit"/>
                    <q-th>File Name</q-th>
                    <q-th>Add to PDF</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td v-if="edit">
                            <q-btn round color="negative" 
                                    @click="deleteFile(tprops.row)"
                                    icon="delete" size="xs" dense
                                    data-cy="file-delete-btn">
                            </q-btn>
                            <q-btn round  
                                    @click="moveFileRowUp(tprops.row)"
                                    icon="arrow_upward" size="xs" dense
                                    data-cy="file-move-up-btn">
                            </q-btn>
                            <q-btn round 
                                    @click="moveFileRowDown(tprops.row)"
                                    icon="arrow_downward" size="xs" dense
                                    data-cy="file-move-down-btn">
                            </q-btn>
                        </q-td>
                        <q-td>
                            <a :href="apiServerHost+'/spec/file/'+props.num+'/'+props.ver+'/'+tprops.row['filename']" data-cy="spec-detail-file-filename"
                                target="_blank">
                                {{tprops.row['filename']}}
                            </a>
                        </q-td>                        
                        <q-td>
                            <q-checkbox v-model="tprops.row['incl_pdf']" data-cy="spec-detail-ref-ver" dense :disable="!edit"/>
                        </q-td>                      
                        <q-td>

                        </q-td>
                    </q-tr>
                </template>
                <template v-slot:bottom-row v-if="edit">
                    <q-uploader
                        class="my-card"
                        :fieldName="(file) =>`file`"
                        :headers="[{name:'X-CSRFToken',value:getCookie('csrftoken') }]"
                        with-credentials
                        :url="files=>`${apiServerHost}/spec/file/${props.num}/${props.ver}`"
                        label="Select File to Upload"
                        @uploaded="refreshFileList"
                        data-cy="add_file-uploader"
                        multiple
                    />
                </template>
           </q-table>
        </q-card-section>

        <span v-if="state === 'Draft'">
            <q-card-actions v-if="!edit" class="bg-white text-teal" align="center">
            <q-btn label="Edit" color="primary" size="lg" class="filter-btn" @click="edit=true" data-cy="spec-detail-update"/>
            </q-card-actions>
            <q-card-actions v-else class="bg-white text-teal" align="center">
            <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveSpec()" data-cy="spec-detail-update"/>
            <div class="spacer"/>
            <q-btn label="Delete" color="red" size="lg" class="filter-btn" @click="deleteSpec()"  data-cy="spec-detail-cancel"/>
            <div class="spacer"/>
            <q-btn label="Cancel" color="red" size="lg" class="filter-btn" @click="cancel()"  data-cy="spec-detail-cancel"/>
            </q-card-actions>
        </span>
    </q-card>
</template>

<script>
import { apiServerHost, defineProps, deleteData, genCy, getCookie, putData, retrieveData } from '@/utils.js'
import {ref, onMounted} from 'vue'
import {useRouter, } from 'vue-router'

export default {
    name: 'SpecDetailPage',
}
</script>

<script setup>    
    const props = defineProps({
        num: String,
        ver: String,
    })

    const created_by = ref('')
    const create_dt = ref('')
    const department = ref('')
    const deptList = ref([])
    const doc_type = ref('')
    const doc_typeList = ref([])
    const edit = ref(false)
    const keywords = ref('')
    const fileRows = ref([])
    const histRows = ref([])
    const jira = ref('')
    const mod_ts = ref('')
    const refRows = ref([])
    const roleList = ref([])
    const router=useRouter();
    const sigRows = ref([])
    const state = ref('')
    const title = ref('')
    const ver = ref('')

    async function saveSpec(){
        const body = {
            doc_type: doc_type.value,
            department: department.value,
            title: title.value,
            keywords: keywords.value,
            jira: jira.value,
            sigs:sigRows.value,
            files:fileRows.value,
            refs:refRows.value,
        }

        let res = await putData(`spec/${props.num}/${props.ver}`, body, 
            'Successfully updated spec ' + props.num + '/' + props.ver)
        if (res.status < 300){
            edit.value = false
        }
    }

    onMounted(() => {
        loadSpec()
        loadLists()
    })

    function cancel() {
        window.location.reload()
    }

    async function deleteFile(fileRow) {
        if (!window.confirm(`Delete file: ${fileRow.filename}?`)) {
            return
        }
        let res = await deleteData(`spec/file/${props.num}/${props.ver}/${fileRow.filename}`, {}, `Deleting file: ${fileRow.filename}`);
        fileRows.value.splice(fileRows.value.indexOf(fileRow), 1)
    }

    function deleteRef(refRow) {
        refRows.value.splice(refRows.value.indexOf(refRow), 1)
    }

    function deleteSig(sigRow) {
        sigRows.value.splice(sigRows.value.indexOf(sigRow), 1)
    }

    async function deleteSpec(){
        if (!window.confirm(`Delete spec: ${props.num}/${props.ver}?`)) {
            return
        }
        
        deleteData(`spec/${props.num}/${props.ver}`, '{}', `Deleted spec: ${props.num}/${props.ver} successfully.`).then((res) => {
            if (res.status < 300){
                router.push({name:"Spec"})
            }
        })
    }

    async function loadSpec() {
        let res = await retrieveData(`spec/${props.num}/${props.ver?props.ver:'*'}`);
        
        ver.value = res['ver']
        doc_type.value = res['doc_type']
        department.value = res['department']
        title.value = res['title']
        keywords.value = res['keywords']
        state.value = res['state']
        created_by.value = res['created_by']
        create_dt.value = res['create_dt']
        mod_ts.value = res['mod_ts']
        jira.value = res['jira']
        sigRows.value = res['sigs']
        fileRows.value = res['files']
        refRows.value = res['refs']
        histRows.value = res['hist']
    }

    async function moveFileRowUp(fileRow) {
        var rownum = fileRows.value.indexOf(fileRow)
        if (rownum <= 0) {return}

        var row = fileRows.value.splice(rownum, 1)[0]
        fileRows.value.splice(rownum-1, 0, row)
    }

    async function moveFileRowDown(fileRow) {
        var rownum = fileRows.value.indexOf(fileRow)
        if (rownum >= fileRows.value.length) {return}

        var row = fileRows.value.splice(rownum, 1)[0]
        fileRows.value.splice(rownum+1, 0, row)
    }

    async function refreshFileList() {
        let res = await retrieveData(`spec/${props.num}/${props.ver}`);
        fileRows.value = res['files']
    }

    async function loadLists() {
        let data_rows = await retrieveData('role/?limit=1000');
        roleList.value = data_rows['results'].map((e) => {return ({label:e['role'],value:e['role']})})
        
        data_rows = await retrieveData('doctype/?limit=1000');
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
