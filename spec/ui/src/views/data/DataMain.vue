<template>
    <q-page class="flex flex-center">
        <div class="q-pa-md window-width">
        
            <div class="q-gutter-x-md q-gutter-x-sm row items-center tool-row">
                <div class='col col-2'>
                    <q-select outlined 
                        :options="filter_display_cols"
                        v-model= "filter_select"
                        use-input
                        input-debounce="0"
                        color="blue"
                        label="Select filter"
                        class="q-pa-sm text-h6"
                        clearable
                        @clear="clearFilter()"
                        @filter="filterFn"
                        data-cy="data-filter-select">
                    </q-select>
                    </div>
                <div class='col col-2'>
                    <q-input class="q-pa-sm text-h6" 
                            v-model="filter_val"
                            @keydown.enter.prevent="applyFilter(`&_${filter_select}=${filter_val}`)" 
                            outlined
                            label="filter value"
                            data-cy="data-filter-input"/>
                </div>
                <div class="row justify-center col-7 q-gutter-x-md q-gutter-x-sm" >
                    <q-btn color="primary" 
                            @click="router.push('/ui-doc-detail/' + route.params.doc_type)"
                            size="md"
                            class="doc-btn"
                            data-cy="data-manage-btn">
                            Manage<br>Page
                    </q-btn>
                    <q-btn color="primary" 
                            @click="saveSelected()"
                            size="md"
                            class="doc-btn"
                            :disable="!authenticated"
                            data-cy="data-save-btn">
                            Save<br>Selected
                    </q-btn>
                    <q-btn color="negative" 
                            v-if="isSupervisor"
                            @click="deleteSelected()"
                            size="md"
                            class="doc-btn"
                            :disable="!isSupervisor"
                            data-cy="data-delete-btn">
                            Delete<br>Selected
                    </q-btn>
                    <q-btn :style="[filtered ? {'background': '#044880'} : {'background': '#027be3'}]"
                            @click="advanced_filter = true"
                            size="md"
                            text-color="white"
                            class="doc-btn"
                            data-cy="data-advanced-filter-btn">
                            Advanced <br> Filter
                    </q-btn>
                    <q-btn color="primary" 
                            @click="clearFilters()"
                            size="md"
                            class="doc-btn"
                            data-cy="data-clear-filter-btn">
                            Clear<br>Filters
                    </q-btn>
                </div>
            </div>
            <q-table
                :title="route.params.doc_type + ' Data'"
                :rows="rows"
                :columns="columns"
                virtual-scroll
                :rows-per-page-options="[0]"
                :row-key="row => row.row_num + ' ' + row.creation_tm"
                selection="multiple"
                v-model:selected="selected"
                :visible-columns="[]"
                :separator="'cell'"
                data-cy="data-table">
                <template v-slot:header="props">
                    <q-th>
                        <q-btn color="blue-grey-2" 
                               text-color="black" 
                               @click="clearSelected()" 
                               data-cy="data-clear-selected">
                            clear <br> Selected
                        </q-btn>
                    </q-th>
                    <q-th v-for="col in props.cols" 
                          :key="col.name" 
                          :props="props" 
                          @mouseover="hover_target = col.name"
                          @mouseout="hover_target = null"
                          @click="applySort(col.name)">
                            {{col.label}}
                        <q-icon v-if="col.name == sort_col"
                               :name="getSortIcon()"/> 
                        <q-icon v-else
                               :name="(hover_target == col.name) ? 'arrow_upward' : null"/>
                    </q-th>
                </template>
                <template v-slot:top-left>
                    <div class="row">
                    <div class="page-title">{{route.params.doc_type}} Data</div>
                    <div class="num-selected" v-if="selected.length > 0">{{selected.length}} row(s) selected</div>
                    </div>
                </template>
                <template v-slot:top-right>
                    <q-btn color="primary" 
                        @click="addNewRow()"
                        label="Add Row"
                        icon-right="add"
                        :disable="!authenticated"
                        no-caps
                        data-cy="data-row-btn">
                    </q-btn>
                    <div class="spacer"/>
                    <q-btn
                    color="primary"
                    icon-right="archive"
                    label="Export to csv"
                    no-caps
                    @click="exportTable"
                    data-cy="data-export-btn"/>
                </template>
                <template v-slot:body="props">
                    <q-tr :props="props" @click="props.row._new_row && !props.selected ? props.selected=true : false">
                        <q-td class="text-center">
                            <q-checkbox v-model="props.selected" v-if="props.row._new_row || isSupervisor" color="primary" />
                        </q-td>
                        <q-td v-for="col in props.cols" :key="col.name" :props="props" class='justify-center'>
                            <q-input
                                v-bind:style="{ width: props.row[col.name] ? props.row[col.name].length/1.5 + 'em': '100%', }" 
                                class="col-md-auto col-row-width" 
                                borderless 
                                :hidden="isNewTime(props.row, col.name)" 
                                standout="bg-yellow text-white" 
                                :readonly="!isEditable(props.row, col.name)" 
                                v-model="props.row[col.name]" 
                                :data-cy="genCy(col.name, props.row[col.name])"/>
                        </q-td>
                    </q-tr>
                </template>
                <template v-slot:bottom>
                    <q-btn @click="getTableData(page_num - 1)" :disable="page_num == 1" data-cy="data-prev-btn">
                        {{'<'}}
                    </q-btn>
                    <q-input input-class="text-right" 
                             v-model="page_num" 
                             class="page-input" 
                             @keydown.enter.prevent="getTableData(page_num)" 
                             data-cy="data-page-input"/>
                    <div class="num-pages" data-cy="data-num-pages">
                         &nbsp;/ {{num_pages}}
                    </div>
                    <q-btn @click="getTableData(page_num + 1)" :disable="page_num == num_pages" data-cy="data-next-btn">
                        {{'>'}}
                    </q-btn>
                </template>
            </q-table>
            <q-dialog v-model="advanced_filter">
                <filter-dialogue-window
                    :col_names="columns.map(col => col['name']).filter(col => !metadata_cols.includes(col))"
                    :rows="rows"
                    :clearFilter="clearFilter"
                    :advanced_filter_dict = advanced_filter_dict
                    @newFilterSlug="applyAdvancedFilters($event)"/>
            </q-dialog >
        </div>
    </q-page>
</template>

<script>
import {
    retrieveData,
    postData,
    putData,
    deleteData,
    dateString,
    showNotif,
    genCy,
    metadata_cols,
} from '@/utils.js';

import { ref, onMounted, computed, defineProps, watch} from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { exportFile, useQuasar } from 'quasar'
import FilterDialogueWindow from '@/components/Filter.vue'

export default {
    name: 'DataPage',
    components: {
        FilterDialogueWindow,
    },
}
</script>

<script setup>

    const sort_icons = [null, 'arrow_upward', 'arrow_downward']
    const sort_toggle = [null, 'asc', 'desc']

    const rows_per_page = 20

    const $q = useQuasar()

    const route = useRoute()
    const router = useRouter()

    const store = useStore()

    const hover_target = ref('')

    const rows = ref([])
    const columns = ref([])
    const selected = ref([])

    const advanced_filter = ref(false);
    const filter_select = ref()
    const filter_val = ref()
    const filtered = ref(false)
    const filter_slug = ref('')
    const sort_slug = ref('')
    const advanced_filter_dict = ref({})
    const filter_display_cols = ref([])
    const filter_cols = ref([])
    const sort_value = ref(0)
    const sort_col = ref('')

    const page_num = ref(1)
    const num_pages = ref()

    const authenticated = ref(computed(() => store.getters.authenticated))
    const isSupervisor = ref(computed(() => store.getters.isSupervisor))

    const props = defineProps({
        rerender: Boolean,
    })

    onMounted(() => {
        getTableData(1)
    })

    watch(() => props.rerender, (newVal, oldVal) => {
        if (newVal === false){
            getTableData(page_num.value)
        }
    })

    async function getTableData(page_number) {
        let data_url = `data/?_doc_type=${route.params.doc_type.toLowerCase()}${pagination_slug(page_number)}`
        if (filter_slug.value){
            data_url = data_url + `${filter_slug.value}`
        }
        if (sort_slug.value){
            data_url = data_url + `${sort_slug.value}`
        }
        let doc_schema = await retrieveData('doc/?search=' + route.params.doc_type.toLowerCase());
        let data_rows = await retrieveData(data_url);
        columns.value = formatCols(doc_schema[0]['schema'])
        rows.value = formatRows(data_rows['results'])

        // Column names used in the filter select box
        filter_cols.value = columns.value.map(col => col['name']).filter(col => !metadata_cols.includes(col))
        set_pagination_params(page_number, data_rows.count)
        setSelected()
    }

    function isEditable(row, name){
        return (row._new_row || isSupervisor.value) && (name != 'creation_tm')
    }

    function isNewTime(row, name){
        return row._new_row && (name == 'creation_tm')
    }

    async function addNewRow() {
        let empty_row = {}
        for (const col of columns.value) {
            empty_row[col['name']] = null;
        }
        empty_row['row_num'] = rows.value.length + 1
        empty_row['creation_tm'] = rows.value.length + 1
        empty_row['_new_row'] = true
        rows.value.unshift(empty_row)
    }

    async function deleteSelected(){
        if (selected.value.length < 1) {
            showNotif('No selected rows to delete.', 'grey')
            return
        }
        // Don't try to delete new rows
        let deleted_rows = selected.value.filter(row => !row['_new_row']).map(function(row) {
            delete row['_new_row']
            return row
        })
        let delete_body = {'doc_type': route.params.doc_type, 'data': deleted_rows}
        deleteData('data/', delete_body, `Deleted ${deleted_rows.length} rows successfully.`).then((res) => {
            if (res.status < 300){
                clearSelected()
                getTableData(1)
            }
        })
    }

    async function clearSelected(){
        selected.value = []
    }

    async function saveSelected(){
        if (selected.value.length < 1) {
            showNotif('No selected rows to save.', 'grey')
            return
        }
        let updated_rows = selected.value.filter(row => !row['_new_row']).map(row => {
            delete row['_new_row']
            return row
        })
        let new_rows = selected.value.filter(row => row['_new_row']).map(row => {
            delete row['_new_row']
            return row
        })
        await saveRows(new_rows, updated_rows).then((pass) => {
            if (pass){
                clearSelected()
                getTableData(1)
            }
        }); 
    }

    async function saveRows(new_rows, updated_rows){
        var post_status = 0;
        var put_status = 0;
        if (new_rows.length > 0){
            let post_body = {'doc_type': route.params.doc_type, 'data': new_rows}
            let post_resp = await postData('data/', post_body, `Added ${new_rows.length} rows successfully.`)
            post_status = post_resp.status
        }
        if ((updated_rows.length > 0) & (post_status < 300)){
            let put_body = {'doc_type': route.params.doc_type, 'data': updated_rows}
            let put_resp = await putData('data/', put_body, `Updated ${updated_rows.length} rows successfully.`)
            put_status = put_resp.status
        }
        if ((put_status < 300) & (post_status < 300)){
            return true
        }

        return false
    }

    function pagination_slug(page_number){
        return `&limit=${rows_per_page}&offset=${(page_number-1)*rows_per_page}`
    }

    function set_pagination_params(page_number, num_rows){
        if (num_pages.value){
            if (page_number > num_pages.value) {
                page_number = num_pages.value
            }
        }
        num_pages.value = Math.ceil(num_rows/rows_per_page)
        page_num.value = page_number
    }

    function formatRows(rows) {
        return rows.map(function(row) {
            row['data']['_new_row'] = false
            row['data']['row_num'] = row['row_num']
            row['data']['creation_tm'] = row['creation_tm']
            return row['data']
        })
    }

    function getCol(col_name, required=true, disp_name=null){
        if (disp_name === null){
            disp_name = col_name
        }
        return {
                name: col_name, 
                label: disp_name, 
                field: col_name, 
                align: 'center', 
                classes: "tab", 
                headerStyle:"font-size:large;", 
                style: 'font-size:large;', 
                required: required,
            }
    }

    function formatCols(doc_schema){
        let cols = Object.keys(doc_schema).map(col => col.replace('*', ''))
        let columns =  cols.map(function (col) {
            return getCol(col)
        })
        // genaralize these two to a function 
        columns.push(getCol('creation_tm', true, 'Time Posted'))
        columns.push(getCol('row_num', false))
        columns.push({
            name: '_new_row', 
            label: '_new_row', 
            field: '_new_row', 
        })
        return columns
    }

    function applyAdvancedFilters(filter_dict){
        advanced_filter_dict.value = filter_dict
        let filter_str = ''
        for (let [key, value] of Object.entries(filter_dict)){
            filter_str += `&_${key}=${value}`
        }
        applyFilter(filter_str)
    }

    function getRowIdx(row_num, creation_tm){
        for (let i = 0; i < rows.value.length; i++){
            let row = rows.value[i]
            if ((row.row_num === row_num) && (row.creation_tm === creation_tm)){
                return i
            }
        }
        return null
    }

    // Data in selected rows is be overwritten when table is rerendered when data is modified
    // So when table is rerendered, the selected row data must be set in the table
    function setSelected(){
        for (const row of selected.value){
            let row_idx = getRowIdx(row.row_num, row.creation_tm)
            if (row_idx != null){
                rows.value[row_idx] = row
            }
        }
    }

    // Delete input box filter on advanced filter
    // Add documentation about basic vs. advanced filter
    async function applyFilter(filter_str){
        if (!filter_str){
            filtered.value = false;
            filter_slug.value = ""
            getTableData(1)
            return;
        }
        filter_slug.value = filter_str
        getTableData(1)
        filtered.value = true;
    }

    async function clearFilter(){
        filter_select.value = null;
        filter_val.value = null;
        filter_slug.value = null;
        advanced_filter_dict.value = {}
        getTableData(1)
    }

    async function clearFilters(){
        filtered.value = false;
        clearFilter()
    }

    async function exportTable () {
        let data_url = `data/?_doc_type=${route.params.doc_type.toLowerCase()}`
        if (filter_slug.value){
            data_url = data_url + `&${filter_slug.value}`
        }
        let data_rows = await retrieveData(data_url);
        let cols_to_csv = columns.value.map(col => col['field']).filter(col => !['row_num', '_new_row'].includes(col))
        let rows_to_csv = data_rows['results']
        toCsv(rows_to_csv, cols_to_csv)
      }

    function mapVal(row, col){
        if (col === 'creation_tm'){
                  return row[col]
              }
        return row['data'][col]
    }

    function toCsv(rows_to_csv, cols_to_csv){
        // naive encoding to csv format
        let content = cols_to_csv.join(',') + '\r\n'
        content += rows_to_csv.map(row => cols_to_csv.map(col => mapVal(row, col)).join(',')).join('\r\n')

        const status = exportFile(
          `${route.params.doc_type}_export_${dateString()}.csv`,
          content,
          'text/csv'
        )

        if (status !== true) {
          $q.notify({
            message: 'Browser denied file download...',
            color: 'negative',
            icon: 'warning'
          })
        }
    }

    function filterFn (val, update) {
        if (val === ''){
            update(() => {
                filter_display_cols.value = filter_cols.value;
            })
        return;
        }
        update(() => {
            filter_display_cols.value = filter_cols.value
            const needle = val.toUpperCase()
            filter_display_cols.value = filter_display_cols.value.filter(v => v.toUpperCase().indexOf(needle) > -1)
        })
    }

    function getSortIcon(){
        return sort_icons[sort_value.value]
    }

    function applySort(col_name){
        sort_slug.value = ''
        if (col_name === sort_col.value){
            sort_value.value = (sort_value.value + 1) % 3
        }
        else{
            sort_col.value = col_name
            sort_value.value = 1
        }
        if (sort_value.value != 0){
            sort_slug.value = `&sort_${sort_col.value}=${sort_toggle[sort_value.value]}`
        }
        getTableData(1)
    }

</script>

<style scoped>

.doc-btn {
    height: 4em;
    margin: 2vw;
}

.page-input {
    width:4em; 
    margin-left: 2vw;
    text-align: right;
}

.num-selected {
    margin-left: 1vw;
    font-size: 1.2em;
    margin-top: .7em;
    font-weight: bold;
}

.tool-row{
    margin-bottom: 2vh; 
    margin-top: 1vh
}

.spacer{
    width: 2vh
}

.col-row-width{
    min-width: 100%
}

.num-pages{
     margin-right: 1vw; 
     font-size: 1.15em;
}

 .page-title{
    font-size: 2em
 }

</style>
