<template>
  <q-card class="dialog-window">
        <q-card-section class="row">
            <q-input v-model="ver" 
                :prefix="props.num+' /'"
                data-cy="spec-detail-num" dense :readonly="true" borderless 
                class="text-h5 text-white"
                label-color="white"/>
        </q-card-section>

        <q-card-section class="q-pt-none row">
            <q-select
                label="State"
                v-model="state"
                :options="[{label:'Draft',value:'Draft'},{label:'Signoff',value:'Signoff'},{label:'Active',value:'Active'},{label:'Obsolete',value:'Obsolete'},]"
                emit-value
                dense :readonly="!edit || !isAdmin"
                data-cy="spec-detail-state"
            />
            <q-select label="Anonymous Access" v-model="anon_access" 
                :options="[{label:'True',value:true}, {label:'False',value:false}]"
                data-cy="spec-detail-anon_access" dense :readonly="!edit || !isAdmin"/>
            <q-select
                label="Document Type"
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
        </q-card-section>

        <q-card-section class="q-pt-none">
            <q-input label="Title" v-model.trim="title" data-cy="spec-detail-title" dense :readonly="!edit"/>
            <q-input label="Keywords" v-model.trim="keywords" data-cy="spec-detail-keywords" dense :readonly="!edit"/>

            <span v-show="String(jira).length > 0">
                Jira: <a :href="jira" target="_blank" rel="noopener noreferrer">{{String(jira).substring(String(jira).lastIndexOf('/')+1)}}</a>
            </span>
            <q-input v-show="edit && isAdmin" label="Jira" v-model.trim="jira" data-cy="spec-detail-jira" dense :readonly="!edit"/>

        </q-card-section>

        <q-card-section class="q-pt-none">
            Signatures:
            <q-table
                :rows="sigRows"
                hide-bottom
                data-cy="spec-detail-sigs">
                <template v-slot:header>
                    <q-th v-show="edit"/>
                    <q-th>Role</q-th>
                    <q-th>Signer</q-th>
                    <q-th>Signed</q-th>
                    <q-th>By</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td v-show="edit">
                            <q-btn round color="negative" 
                                    @click="deleteSig(tprops.row)"
                                    icon="delete" size="xs" dense
                                    data-cy="data-delete-btn"
                                    v-show="!tprops.row['from_am']">
                            </q-btn>
                        </q-td>
                        <q-td v-if="!tprops.row['_new']" style="white-space: nowrap;">
                            {{tprops.row["role"]}}
                            <span  v-show="tprops.row['spec_one']">*</span></q-td>
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
                        <q-td>
                            {{dispDate(tprops.row["signed_dt"])}}
                            <q-btn 
                                v-if="state_loaded === 'Signoff' && tprops.row['signed_dt'] === null" 
                                label="Sign" @click="signRole(tprops.row)"  data-cy="spec-detail-sign"/>
                            <q-btn 
                                v-if="state_loaded === 'Signoff' && tprops.row['signed_dt'] === null" 
                                label="Reject" @click="rejectRole(tprops.row)"  data-cy="spec-detail-reject"/>
                        </q-td>
                        <q-td>{{tprops.row["delegate"]}}</q-td>
                    </q-tr>
                </template>
                <template v-slot:bottom-row v-if="edit">
                    <q-btn color="primary" dense
                        @click="sigRows.push({_new:true})"
                        icon-right="add" size="xs"
                        no-caps
                        data-cy="add_sig-btn"
                        v-show="edit">
                    </q-btn>
                </template>
           </q-table>
        </q-card-section>
        
        <q-card-section class="q-pt-none">
            References:
            <q-table
                :rows="refRows"
                hide-bottom
                data-cy="spec-detail-refs">
                <template v-slot:header>
                    <q-th v-show="edit"/>
                    <q-th>Num</q-th>
                    <q-th>Ver (optional)</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td v-show="edit">
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
                <template v-slot:bottom-row v-if="edit">
                    <q-btn color="primary" dense
                        @click="refRows.push({_new:true})"
                        icon-right="add" size="xs"
                        no-caps
                        data-cy="add_ref-btn"
                        v-show="edit">
                    </q-btn>
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
                    <q-th v-show="edit"/>
                    <q-th>File Name</q-th>
                    <q-th>Add to PDF</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td v-show="edit">
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
                            <a :href="apiServerHost+'/spec/file/'+props.num+'/'+ver.value+'/'+tprops.row['filename']" data-cy="spec-detail-file-filename"
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
                        :url="files=>`${apiServerHost}/spec/file/${props.num}/${ver.value}`"
                        label="Select File to Upload"
                        @uploaded="refreshFileList"
                        data-cy="add_file-uploader"
                        multiple
                    />
                </template>
           </q-table>
        </q-card-section>
        
        <q-card-section class="q-pt-none">
            History:
            <q-table
                :rows="histRows"
                hide-bottom
                data-cy="spec-detail-files">
                <template v-slot:header>
                    <q-th>Who</q-th>
                    <q-th>When</q-th>
                    <q-th>Operation</q-th>
                    <q-th>Comment</q-th>
                </template>
                <template v-slot:body="tprops">
                    <q-tr>
                        <q-td>{{tprops.row['upd_by']}}</q-td>  
                        <q-td>{{dispDate(tprops.row['mod_ts'])}}</q-td>  
                        <q-td>{{tprops.row['change_type']}}</q-td>  
                        <q-td>{{tprops.row['comment']}}</q-td>    
                    </q-tr>
                </template>
           </q-table>
        </q-card-section>

        <q-card-section class="q-pt-none">
            <q-input label="Comment" v-model.trim="comment" data-cy="spec-detail-comment" type="textarea" v-show="edit"/>
        </q-card-section>

        <span v-show="state_loaded === 'Draft'">
            <q-card-actions v-show="!edit" class="bg-white text-teal" align="center">
                <q-btn label="Edit" color="primary" size="lg" class="filter-btn" @click="edit=true" data-cy="spec-detail-update"/>
                <div class="spacer"/>
                <q-btn label="Submit" color="primary" size="lg" class="filter-btn" @click="submitSpec()"  data-cy="spec-detail-cancel"/>
            </q-card-actions>
            <q-card-actions v-show="edit" class="bg-white text-teal" align="center">
                <q-btn label="Save" color="primary" size="lg" class="filter-btn" @click="saveSpec()" data-cy="spec-detail-update"/>
                <div class="spacer"/>
                <q-btn label="Delete" color="red" size="lg" class="filter-btn" @click="deleteSpec()"  data-cy="spec-detail-cancel"/>
                <div class="spacer"/>
                <q-btn label="Cancel" color="red" size="lg" class="filter-btn" @click="cancel()"  data-cy="spec-detail-cancel"/>
            </q-card-actions>
        </span>
        <span v-show="state_loaded === 'Active' || state_loaded === 'Obsolete'">
            <q-card-actions class="bg-white text-teal" align="center">
                <q-btn label="Revise" color="primary" size="lg" class="filter-btn" @click="reviseSpec()"  data-cy="spec-detail-update"/>
            </q-card-actions>
        </span>
        <span v-show="state_loaded !== 'Draft' && isAdmin">
            <q-card-actions v-show="!edit" class="bg-white text-teal" align="center">
                <q-btn label="Admin Edit" color="red" size="lg" class="filter-btn" @click="edit=true" data-cy="spec-detail-update"/>
            </q-card-actions>
            <q-card-actions v-show="edit" class="bg-white text-teal" align="center">
                <q-btn label="Admin Save" color="primary" size="lg" class="filter-btn" @click="saveSpec()" data-cy="spec-detail-update"/>
                <div class="spacer"/>
                <q-btn label="Cancel" color="red" size="lg" class="filter-btn" @click="cancel()"  data-cy="spec-detail-cancel"/>
            </q-card-actions>
        </span>

        <div class="q-pa-md window-width">
            <q-table
                :rows="version_list"
                :columns="spec_columns"
                :rows-per-page-options="[0]"
                data-cy="spec-table">
                <template v-slot:header="props">
                    <q-th v-for="col in columns" 
                          :key="col.name" 
                          :props="props" >
                            {{col.label}}
                    </q-th>
                </template>
                <template v-slot:body="props">
                    <q-tr :props="props" @click="props.row._new_row && !props.selected ? props.selected=true : false">
                        <q-td v-for="col in props.cols" :key="col.name" :props="props" class='text-center'>
                            <span v-if="col.name === 'num'">
                                <router-link :to="'/ui-spec/'+props.row['num']+'/'+props.row['ver']">
                                    {{props.row['num']}}/{{props.row['ver']}}
                                    </router-link>
                            </span>
                            <span v-else-if="col.name === 'mod_ts'">{{dispDate(props.row[col.name])}}</span>
                            <span v-else>{{props.row[col.name]}}</span>
                        </q-td>
                    </q-tr>
                </template>
            </q-table>
        </div>

    </q-card>
    <q-dialog v-model="reject_spec">
        <reject-spec-dialog
            :num = "props.num"
            :ver = "ver.value"
            :sigRow = "sigRow"
            @updateSpec="loadSpec()"/>
    </q-dialog >
</template>

<script>
import { apiServerHost, defineProps, deleteData, dispDate, genCy, getCookie, postData, putData, retrieveData, 
        showNotif, } from '@/utils.js'
import { computed, onMounted, ref, } from 'vue'
import { useRouter, } from 'vue-router'
import { useStore } from 'vuex'
import RejectSpecDialog from '@/views/spec/RejectSpec.vue'

export default {
    name: 'SpecDetailPage',
    components: {
        RejectSpecDialog,
    },
}
</script>

<script setup>    
    const props = defineProps({
        num: String,
        ver: String,
    })
    const store = useStore()

    const anon_access = ref({label:'False',value:false})
    const comment = ref('')
    const created_by = ref('')
    const create_dt = ref('')
    const department = ref('')
    const deptList = ref([])
    const doc_type = ref('')
    const doc_typeList = ref([])
    const edit = ref(false)
    const isAdmin = ref(computed(() => store.getters.isAdmin))
    const keywords = ref('')
    const fileRows = ref([])
    const histRows = ref([])
    const jira = ref('')
    const mod_ts = ref('')
    const refRows = ref([])
    const reject_spec = ref(false)
    const roleList = ref([])
    const router=useRouter();
    const sigRow = ref({})
    const sigRows = ref([])
    const state = ref('')
    const state_loaded = ref('')
    const title = ref('')
    const ver = ref('')
    const version_list = ref([])

    async function saveSpec(){
        const body = {
            state: state.value,
            doc_type: doc_type.value,
            department: department.value,
            title: title.value,
            keywords: keywords.value,
            jira: jira.value,
            sigs:sigRows.value,
            files:fileRows.value,
            refs:refRows.value,
            comment:comment.value,
        }

        let res = await putData(`spec/${props.num}/${ver.value}`, body, 
            'Successfully updated spec ' + props.num + '/' + ver.value)
        if (res.__resp_status < 300){
            edit.value = false
            loadForm(res)
        }
    }

    onMounted(() => {
        ver.value = props.ver
        loadSpec()
        loadOtherVersions()
        loadLists()
    })

    function cancel() {
        window.location.reload()
    }

    async function deleteFile(fileRow) {
        if (!window.confirm(`Delete file: ${fileRow.filename}?`)) {
            return
        }
        let res = await deleteData(`spec/file/${props.num}/${ver.value}/${fileRow.filename}`, {}, `Deleting file: ${fileRow.filename}`);
        fileRows.value.splice(fileRows.value.indexOf(fileRow), 1)
    }

    function deleteRef(refRow) {
        refRows.value.splice(refRows.value.indexOf(refRow), 1)
    }

    function deleteSig(sigRow) {
        sigRows.value.splice(sigRows.value.indexOf(sigRow), 1)
    }

    async function deleteSpec(){
        if (!window.confirm(`Delete spec: ${props.num}/${ver.value}?`)) {
            return
        }
        
        deleteData(`spec/${props.num}/${ver.value}`, '{}', `Deleted spec: ${props.num}/${ver.value} successfully.`).then((res) => {
            if (res.__resp_status < 300){
                router.push({name:"Spec"})
            }
        })
    }

    function loadForm(res) {        
        edit.value = false
        reject_spec.value = false

        ver.value = res['ver']
        doc_type.value = res['doc_type']
        department.value = res['department']
        title.value = res['title']
        keywords.value = res['keywords']
        state.value = res['state']
        state_loaded.value = res['state']
        created_by.value = res['created_by']
        create_dt.value = res['create_dt']
        mod_ts.value = res['mod_ts']
        jira.value = res['jira']
        sigRows.value = res['sigs']
        fileRows.value = res['files']
        refRows.value = res['refs']
        histRows.value = res['hist']
    }

    async function loadOtherVersions() {
        let res = await retrieveData(`spec/${props.num}`);
        version_list.value = res['results']
    }

    async function loadSpec() {
        let res = await retrieveData(`spec/${props.num}/${ver.value?ver.value:'*'}`);
        loadForm(res)
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
        let res = await retrieveData(`spec/${props.num}/${ver.value}`);
        fileRows.value = res['files']
    }

    async function rejectRole(row){
        sigRow.value=row
        reject_spec.value = true
    }

    async function reviseSpec(){
        if (!window.confirm(`Create new revision of spec: ${props.num}/${ver.value}?`)) {
            return
        }
        
        let res = await postData(`spec/${props.num}/${ver.value}`, {}, null)
        if (res.__resp_status < 300) {
            showNotif(`Spec created: ${res.num}/${res.ver}`, 'green')
            router.push({name:"Spec Detail", params:{num:res.num, ver:res.ver}})
        }
    }

    async function signRole(sigRow){
        let res = await postData(`spec/sign/${props.num}/${ver.value}`, {'role':sigRow['role'], 'signer':sigRow['signer']}, `Signed spec: ${props.num}/${ver.value} successfully.`).then((res) => {
            if (res.__resp_status < 300){
                router.go()
            }
        })
    }

    async function submitSpec(){
        
        postData(`spec/submit/${props.num}/${ver.value}`, {}, `Submitted spec: ${props.num}/${ver.value} for signatures successfully.`).then((res) => {
            if (res.__resp_status < 300){
                router.go()
            }
        })
    }

    async function loadLists() {
        let data_rows = await retrieveData('role/?limit=1000');
        roleList.value = data_rows['results'].map((e) => {return ({label:e['role'],value:e['role']})})
        
        data_rows = await retrieveData('doctype/?limit=1000');
        doc_typeList.value = data_rows['results'].map((e) => {return ({label:e['name'],value:e['name']})})
        
        data_rows = await retrieveData('dept/?limit=1000');
        deptList.value = data_rows['results'].map((e) => {return ({label:e['name'],value:e['name']})})
    }

    const spec_columns = [
            { name: 'num', align: 'left', label: 'Spec', field: 'num', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'title', align: 'left', label: 'Title', field: 'title', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'doc_type', align: 'left', label: 'Doc Type', field: 'doc_type', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'department', align: 'left', label: 'Department', field: 'department', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'keywords', align: 'left', label: 'Keywords', field: 'keywords', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'state', align: 'left', label: 'State', field: 'state', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'created_by', align: 'left', label: 'Created By', field: 'created_by', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'mod_ts', align: 'left', label: 'Last Modified', field: 'mod_ts', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'anon_access', align: 'left', label: 'Anonymous Access', field: 'anon_access', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
        ]
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
