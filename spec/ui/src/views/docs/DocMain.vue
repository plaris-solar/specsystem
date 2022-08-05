<template>
    <q-page class="flex flex-center">
        <div class="q-pa-md window-width no-top-pad">
        
            <div class="row manage-tools">
                <q-chip size="lg">
                    <q-select borderless v-model="selected_doc" 
                            :options="display_docs"
                            use-input
                            data-cy="doc-table-select"
                            color="blue"
                            label="Select Page"
                            class="q-pa-sm text-h6"
                            clearable
                            @filter="filterFn"
                            @update:model-value="filterDocs(selected_doc)">
                    </q-select>
                </q-chip>
                <div class="text-right upload-btn">  
                    <q-btn color="blue-grey" size='large' :disable="!isSupervisor" @click="toNewDocPage" data-cy="doc-new-page-btn">
                        <div class="text-center">
                            Create New Page
                        </div>
                    </q-btn>
                </div>
            </div>
            <q-table
            title="Page Management"
            :rows="rows"
            virtual-scroll
            :columns="columns"
            row-key="page"
            :separator="'cell'"
            data-cy="doc-table">
                <template v-slot:body="props">
                    <q-tr :props="props" >
                        <q-td key="page" :props="props">
                            <q-btn flat class="hyperlink doc-name" @click="toDocDetail(props.row.doc_type)" size="lg">
                                {{ props.row.doc_type }}
                            </q-btn>
                        </q-td>
                        <q-td key="description" :props="props">
                            {{props.row.description}}
                        </q-td>
                        <q-td key="columns" :props="props">
                            <div class="column inline col-md-auto schema-col">
                                <div v-for="(item, key) in props.row.schema.slice(0, ceil(props.row.schema_len/3))" :key="key">
                                    <div v-text="item" class="page-col" v-if="isRequired(item)"/>
                                    <div v-text="item" v-if="!isRequired(item)"/>
                                </div>
                            </div>
                            <div class="column inline col-md-auto schema-col">
                                <div v-for="(item, key) in props.row.schema.slice(ceil(props.row.schema_len/3), 2*ceil(props.row.schema_len/3))" :key="key">
                                    <div v-text="item" class="page-col" v-if="isRequired(item)"/>
                                    <div v-text="item" v-if="!isRequired(item)"/>
                                </div>
                            </div>
                            <div class="column inline col-md-auto schema-col">
                                <div v-for="(item, key) in props.row.schema.slice(2*ceil(props.row.schema_len/3), props.row.schema_len)" :key="key">
                                    <div v-text="item" class="page-col" v-if="isRequired(item)"/>
                                    <div v-text="item" v-if="!isRequired(item)"/>
                                </div>
                            </div>
                        </q-td>
                    </q-tr>
                </template>
            </q-table>
            <div class="text-center">
                <h5>*- Required Column (No empty values allowed)</h5>
            </div>
        </div>
    </q-page>
</template>

<script>
import {
    retrieveData
} from '@/utils.js';

import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
    name: 'DocPage',
}
</script>

<script setup>

    const columns = [
            { name: 'page', align: 'left', label: 'Page', field: 'doc_type', classes: "tab page-col", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: true},
            { name: 'description', align: 'left', label: 'Description', field: 'description',  classes: "tab", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: false },
            { name: 'columns', align: 'left', label: 'Columns', field: 'schema',  classes: "tab", headerStyle:"font-size:large;", style: 'width: 15em;', sortable: false },
        ]

    const store = useStore()
    const router = useRouter()

    const selected_doc = ref()

    const rows = ref([])

    const full_doc_data = ref([])
    const docs = ref([])
    const display_docs = ref([])

    const isSupervisor = ref(computed(() => store.getters.isSupervisor))

    onMounted(() => {
        getDocData()
    })

    function ceil(num){
        return Math.ceil(num)
    }

    async function filterDocs(doc_type) {
        if (!doc_type){
            rows.value = full_doc_data.value.map(format_row)
        }
        else {
            rows.value = rows.value.filter( row => row['doc_type'] === doc_type)
        }
    }

    async function getDocData() {
        full_doc_data.value = await retrieveData('doc/');
        full_doc_data.value = full_doc_data.value.map(removeMetaData)
        rows.value = full_doc_data.value.map(format_row)
        docs.value = full_doc_data.value.map(row => row['doc_type'].toUpperCase())
        display_docs.value = docs.value;
    }

    function removeMetaData(row) {
        delete row['schema']['row_num']
        delete row['schema']['creation_tm']
        return row
    }

    function format_row(row) {
        const schema_list = Object.keys(row['schema'])
        return {"doc_type": row['doc_type'].toUpperCase(),  "description": row['description'], "schema": schema_list, schema_len: schema_list.length}
    }

    function toDocDetail(new_doc_type) {
        router.push('/ui-doc-detail/' + new_doc_type)
    }

    function toNewDocPage() {
        router.push('/ui-doc-detail/')
    }

    function isRequired(col) {
        return col.includes('*')
    }

    function filterFn (val, update) {
        if (val === ''){
        update(() => {
            display_docs.value = docs.value;
        })
        return;
        }
        update(() => {
        const needle = val.toUpperCase()
        display_docs.value = docs.value.filter(v => v.toUpperCase().indexOf(needle) > -1)
        })
    }

</script>

<style scoped>
li {
    font-size: 20px;
}

.tab {
    font-size: large;
}

.page-col {
    font-weight: bold;
}

.hyperlink {
    color: blue;
}

.upload-btn {
    padding-left: 5vh;
}

.manage-tools {
    margin-bottom:2em;
}

.schema-col {
    text-align: left; 
    width: 15em;
}

.no-top-pad{
    padding-top: 0vh
}

.doc-name{
    padding: 1em;
}

</style>