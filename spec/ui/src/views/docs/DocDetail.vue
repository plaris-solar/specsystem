<template>
    <q-page class="flex " >
        <div class="q-pa-md window-width" >
            <div class="q-gutter-x-md row items-center doc-tools">
                <div class='column'>
                <q-input outlined 
                         v-model="doc_type" 
                         label="Page Name..." 
                         class="text-box" 
                         :readonly="!isSupervisor" 
                         input-class="doc-select" 
                         data-cy="doc-detail-doc-name"/>
                <div class="spacer"/>
                <q-select outlined 
                        :options="schema_fields"
                        v-model="id_col"
                        use-input
                        input-debounce="0"
                        color="blue"
                        label="ID Column"
                        clearable
                        @filter="filterFn"
                        data-cy="doc-detail-id-col">
                        <template v-slot:append>
                            <q-icon name="help" />
                            <q-tooltip class="tooltip">
                                This column will be used for indexing. <br> It cannot contain null values. <br> Duplicate data will not be overwritten.
                            </q-tooltip>
                        </template>
                </q-select>
                </div>
                <q-input    outlined type="textarea" 
                            v-model="doc_descr" 
                            label="Page Description..." 
                            :readonly="!isSupervisor" 
                            class="text-box" 
                            input-class="doc-select" 
                            data-cy="doc-detail-doc-descr"/>
                <div class="row justify-center col-6 q-gutter-x-md">
                    <q-btn color="primary" 
                            @click="saveDoc()"
                            size="lg"
                            class="doc-btn"
                            :disable="!isSupervisor"
                            data-cy="doc-detail-save-btn">
                            Save<br>Page Data
                    </q-btn>
                    
                    <q-file class="doc-btn" 
                            color="blue-grey" 
                            standout 
                            syle="height: 5em"
                            bottom-slots 
                            v-model="csv" 
                            clearable
                            label="Upload CSV Template"
                            :disable="!isSupervisor"
                            @update:model-value="readCsvTemplate(csv)"
                            @clear="clearFile()"
                            data-cy="doc-detail-csv-btn">
                        <template v-slot:prepend>
                        <q-icon name="attach_file" />
                        </template>
                    </q-file>
                </div>
            </div>
            <q-table
                title="Page Details"
                :rows="rows"
                :columns="columns"
                :rows-per-page-options="[0]"
                row-key="page"
                :separator="'cell'"
                data-cy="doc_detail-table">
                <template v-slot:top-right>
                    <q-btn color="primary" 
                        @click="addNewRow()"
                        class="btn-spacer"
                        label="Add Row"
                        icon-right="add"
                        :disable="!authenticated"
                        no-caps
                        data-cy="doc-detail-row-btn">
                    </q-btn>
                </template>
                    <template v-slot:body="props">
                        <q-tr :props="props">
                            <q-td key="delete" :props="props">
                                <q-btn v-if="props.row.column != id_col"
                                    color="negative"
                                    icon-right="delete"
                                    no-caps
                                    flat
                                    dense
                                    :disable="!isSupervisor"
                                    @click="deleteRow(props.row)"
                                    :data-cy="genCy('doc-detail-delete', props.row.column)"/>
                            </q-td>
                            <q-td key="column" :props="props">
                                <q-input v-if="props.row.column != id_col" 
                                         borderless 
                                         standout="bg-yellow text-white" 
                                         :readonly="!isSupervisor" 
                                         v-model="props.row.column" 
                                         dense 
                                         :data-cy="genCy('doc-detail-col', props.row.column)"/>
                                <q-input  v-else 
                                          borderless standout="bg-yellow text-white" 
                                          input-style="font-weight: bold;"
                                          :readonly="!isSupervisor" 
                                          v-model="props.row.column" 
                                          dense 
                                          :data-cy="genCy('doc-detail-col', props.row.column)"/>
                            </q-td>
                            <q-td key="type" :props="props">
                                <q-select borderless 
                                         :options="data_types"
                                         standout="bg-yellow text-white" 
                                         :readonly="!isSupervisor" 
                                         v-model="props.row.type" 
                                         dense 
                                         :data-cy="genCy('doc-detail-type', props.row.column)"/>
                            </q-td>
                            <q-td key="required" :props="props">
                                <q-checkbox v-model="props.row.required" :disable="!isSupervisor || (props.row.column == id_col)" :data-cy="genCy('doc-detail-req', props.row.column)"/>
                            </q-td>
                        </q-tr>
                    </template>
            </q-table>
        </div>
    </q-page>
</template>

<script>
import {
    retrieveData,
    postData,
    genCy,
    data_types
} from '@/utils.js';

import { ref, onMounted, computed, watch, defineEmits} from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
    name: 'DocPage',
}
const columns = [
        { name: 'delete', label: 'Delete', field: 'delete', align: 'center', classes: "tab", headerStyle:"font-size:large;", style: 'width: 3vw;font-size:large;', sortable: false},
        { name: 'column', align: 'left', label: 'Column', field: 'column', classes: "tab", headerStyle:"font-size:large;", style: 'width: 15vw;font-size:large;', sortable: false},
        { name: 'type', align: 'left', label: 'Data Type', field: 'type',  classes: "tab", headerStyle:"font-size:large;", style: 'width: 15vw;font-size:large;', sortable: false },
        { name: 'required', align: 'left', label: 'Required?', field: 'required',  classes: "tab", headerStyle:"font-size:large;", style: 'width: 15vw;font-size:large;', sortable: false },
    ]
</script>

<script setup>

    const emit = defineEmits(['update_doc'])

    const route = useRoute()
    const router = useRouter()

    const store = useStore()

    const rows = ref([])
    const csv = ref()

    const doc_type = ref()
    const doc_descr = ref()
    const id_col = ref('')

    const schema_fields = ref([])

    const isSupervisor = ref(computed(() => store.getters.isSupervisor))
    const authenticated = ref(computed(() => store.getters.authenticated))

    onMounted(() => {
        if (route.params.doc_type){
            getTableData()
        }
        else{
            getNewTableData()
        }
    })

    watch(id_col, (newVal, oldVal) => {
      if (newVal && rows.value.length) {
        setIdCol(newVal)
      } 
    })

    watch(rows, (newVal, oldVal) => {
      if (newVal && rows.value.length) {
        schema_fields.value = rows.value.map(row => row['column'])
      }
    })

    function setIdCol(col_name){
        for (let i = 0; i < rows.value.length; i++){
            if (rows.value[i].column == col_name){
                rows.value[i]['required'] = true
            }
        }
    }

    async function getTableData() {
        doc_type.value = route.params.doc_type
        let detail_data = await retrieveData('doc/?search=' + route.params.doc_type.toLowerCase());
        detail_data = detail_data[0]
        let schema = detail_data['schema']
        if (!id_col.value){
            id_col.value = detail_data['id_col']
        }
        doc_descr.value = detail_data['description']
        rows.value = formatSchema(schema, id_col.value)
    }

    function formatSchema(schema, id_col_str){
        delete schema['row_num']
        delete schema['creation_tm']

        let id_row = {'column': id_col_str, 'type': schema[id_col_str+'*'], 'required': true}

        schema = Object.fromEntries(Object.entries(schema).filter(([k,v]) => k != id_col_str+'*'));
        let schema_rows = formatRows(schema)
        schema_rows.unshift(id_row)
        return schema_rows
    }

    async function clearFile(){
        csv.value = null;
    }

    async function readCsvTemplate(csv){
        var reader = new FileReader();
        reader.readAsText(csv)
        reader.onload = function(e) {
            let allTextLines = reader.result.split(/\r\n|\n/);
            let cols = allTextLines[0].split(','); 
            rows.value = cols.map(function (col) {
                col = col.replaceAll('"', '')
                let required = false
                if (col && (col == id_col.value)){
                    required = true
                }
                return {'column': col, 'type': 'string', 'required': required}
            })
        }
    }

    async function getNewTableData() {
        rows.value = [{'column': 'lot_id', 'type': 'string', 'required': true}]
        id_col.value = 'lot_id'
        for (let i=0; i<5; i++){
            rows.value.push({'column': '', 'type': 'string', 'required': false})
        }
    }

    async function deleteRow(row) {
        let del_idx = rows.value.indexOf(row)
        rows.value.splice(del_idx, 1)
    }

    async function saveDoc() {
        let schema = toSchema(rows.value)
        let body = {'doc_type': doc_type.value, 'schema': schema, 'description': doc_descr.value, 'id_col': id_col.value}
        let res = await postData('doc/', body, 'Page updated successfully.') 
        if (res.status < 300){
            router.push('/ui-doc-detail/' + doc_type.value)
        }
        emit('update_doc')
    }

    function filterFn (val, update) {
        if (val === ''){
        update(() => {
            schema_fields.value = rows.value.map(row => row['column']);
        })
        return;
        }
        update(() => {
            const needle = val.toUpperCase()
            schema_fields.value = schema_fields.value.filter(v => v.toUpperCase().indexOf(needle) > -1)
        })
    }

    function toSchema(row_list) {
        let schema = {}
        for (const field of row_list) {
            let col_name = field['column']
            let dtype = field['type']
            if (field['required']) {
                col_name += '*'
            }
            schema[col_name] = dtype;
        }
        return schema
    }

    async function addNewRow(){
        rows.value.push({'column': '', 'type': 'string', 'required': false})
    }

    function formatRows(doc_detail) {
        let row_list = []
        for (const [key, value] of Object.entries(doc_detail)) {
            let is_required = key.includes('*')
            let display_key = key.replace('*', "")
            row_list.push({'column': display_key, 'type': value, 'required': is_required})
        }
        return row_list
    }

</script>

<style scoped>

.text-box {
   width: 20vw; 
}

.doc-btn {
    height: 4em;
    margin: 2vw;
}

.doc-tools{
    margin-bottom: 2vh;
    margin-top: 3vh
}

.spacer{
    height: 1vw
}

.tooltip{
    font-size: 1em; 
    text-align: center
}

.doc-select{
    font-size: 150%;
}

.btn-spacer{
    margin-right: 2vw
}

</style>