<template>
  <q-page>
    <div class="q-pa-md row">
      <q-table
        title="Doctypes"
        :rows="rows"
        :columns="columns"
        separator="cell"
        row-key="doctype"
        :rows-per-page-options="[0]"
        data-cy="doctype-table"
      >
        <template v-slot:top-left>
          <div class="row">
            <q-card-actions>
              <q-input
                v-model="filter_val"
                @keydown.enter.prevent="applyFilter(`&search=${filter_val}`)"
                label="filter value"
                data-cy="data-filter-input"
              />
            </q-card-actions>
            <q-card-actions>
              <q-btn
                round
                color="primary"
                @click="clearFilters()"
                icon="clear"
                size="sm"
                data-cy="data-clear-filter-btn"
              >
              </q-btn>
            </q-card-actions>
          </div>
        </template>
        <template v-slot:top-right>
          <q-btn
            color="primary"
            v-show="isAdmin && isAuthenticated"
            @click="add_doctype = true"
            label="Add Doctype"
            icon-right="add"
            no-caps
            data-cy="data-row-btn"
          >
          </q-btn>
        </template>
        <template v-slot:header="props">
          <q-th v-show="isAdmin && isAuthenticated" style="width: 15em"> </q-th>
          <q-th v-for="col in columns" :key="col.name" :props="props">
            {{ col.label }}
          </q-th>
        </template>
        <template v-slot:body="props">
          <q-tr
            :props="props"
            @click="
              props.row._new_row && !props.selected
                ? (props.selected = true)
                : false
            "
          >
            <q-td v-show="isAdmin && isAuthenticated">
              <q-btn
                round
                color="negative"
                @click="deleteSelected(props.row['name'])"
                icon="delete"
                size="xs"
                data-cy="data-delete-btn"
              >
              </q-btn>
              &nbsp;
              <q-btn
                round
                color="primary"
                @click="updateSelected(props.row)"
                icon="edit"
                size="xs"
                data-cy="data-edit-btn"
              >
              </q-btn>
            </q-td>
            <q-td
              v-for="col in props.cols"
              :key="col.name"
              :props="props"
              class="text-center"
            >
              <a
                v-if="col.name === 'jira_temp'"
                :href="props.row['jira_temp_url']"
                target="_blank"
              >
                {{ props.row[col.name] }}
              </a>
              <span v-else>{{ props.row[col.name] }}</span>
            </q-td>
          </q-tr>
        </template>
        <template v-slot:bottom>
          <q-btn
            @click="getTableData(page_num - 1)"
            :disable="page_num == 1"
            data-cy="data-prev-btn"
          >
            {{ "&lt;" }}
          </q-btn>
          <q-input
            input-class="text-right"
            v-model="page_num"
            class="page-input"
            @keydown.enter.prevent="getTableData(page_num)"
            data-cy="data-page-input"
          />
          <div class="num-pages" data-cy="data-num-pages">
            &nbsp;/ {{ num_pages }}
          </div>
          <q-btn
            @click="getTableData(page_num + 1)"
            :disable="page_num == num_pages"
            data-cy="data-next-btn"
          >
            {{ ">" }}
          </q-btn>
          <q-space />
          <q-btn
            color="primary"
            :href="apiServerHost + '/doctype/?output_csv=true' + filter_slug"
            target="_blank"
            icon="file_download"
            data-cy="open-file"
          />
        </template>
      </q-table>
      <q-dialog v-model="add_doctype">
        <create-doctype-dialog
          :doctypeRow="{}"
          :createMode="true"
          @updateTable="getTableData(page_num)"
        />
      </q-dialog>
      <q-dialog v-model="upd_doctype">
        <create-doctype-dialog
          :doctypeRow="doctypeRow"
          :createMode="false"
          @updateTable="getTableData(page_num)"
        />
      </q-dialog>
    </div>
  </q-page>
</template>

<script>
import { apiServerHost, retrieveData, deleteData } from "@/utils.js";

import { ref, onMounted, computed, defineProps, watch } from "vue";
import { useStore } from "vuex";
import CreateDoctypeDialog from "@/views/doctype/CreateDoctype.vue";

export default {
  name: "DoctypePage",
  components: {
    CreateDoctypeDialog,
  },
};
</script>

<script setup>
const rows_per_page = 20;

const store = useStore();

const rows = ref([]);
const selected = ref([]);

const add_doctype = ref(false);
const filter_select = ref();
const filter_val = ref();
const filtered = ref(false);
const filter_slug = ref("");
const doctypeRow = ref();
const sort_slug = ref("");
const upd_doctype = ref(false);

const page_num = ref(1);
const num_pages = ref();

const isAuthenticated = ref(computed(() => store.getters.authenticated));
const isAdmin = ref(computed(() => store.getters.isAdmin));

const props = defineProps({
  rerender: Boolean,
});

onMounted(() => {
  getTableData(1);
});

watch(
  () => props.rerender,
  (newVal, oldVal) => {
    if (newVal === false) {
      getTableData(page_num.value);
    }
  }
);

async function getTableData(page_number) {
  add_doctype.value = false; // Close Add Doctype popup, if open
  upd_doctype.value = false; // Close Update Doctype popup, if open
  let data_url = `doctype/?_=_${pagination_slug(page_number)}`;
  if (filter_slug.value) {
    data_url = data_url + `${filter_slug.value}`;
  }
  if (sort_slug.value) {
    data_url = data_url + `${sort_slug.value}`;
  }
  let data_rows = await retrieveData(data_url);
  rows.value = formatRows(data_rows["results"]);

  set_pagination_params(page_number, data_rows.count);
  setSelected();
}

async function deleteSelected(doctype) {
  if (!window.confirm(`Delete doctype: ${doctype}?`)) {
    return;
  }

  let res = await deleteData(
    `doctype/${doctype}`,
    "{}",
    `Deleted doctype: ${doctype} successfully.`
  );
  if (res.__resp_status < 300) {
    clearSelected();
    getTableData(1);
  }
}

async function clearSelected() {
  selected.value = [];
}

async function updateSelected(row) {
  doctypeRow.value = row;
  upd_doctype.value = true;
}

function pagination_slug(page_number) {
  return `&limit=${rows_per_page}&offset=${(page_number - 1) * rows_per_page}`;
}

function set_pagination_params(page_number, num_rows) {
  if (num_pages.value) {
    if (page_number > num_pages.value) {
      page_number = num_pages.value;
    }
  }
  num_pages.value = Math.ceil(num_rows / rows_per_page);
  page_num.value = page_number;
}

function formatRows(rows) {
  return rows;
}

function getRowIdx(row_num, creation_tm) {
  for (let i = 0; i < rows.value.length; i++) {
    let row = rows.value[i];
    if (row.row_num === row_num && row.creation_tm === creation_tm) {
      return i;
    }
  }
  return null;
}

// Data in selected rows is be overwritten when table is rerendered when data is modified
// So when table is rerendered, the selected row data must be set in the table
function setSelected() {
  for (const row of selected.value) {
    let row_idx = getRowIdx(row.row_num, row.creation_tm);
    if (row_idx != null) {
      rows.value[row_idx] = row;
    }
  }
}

// Delete input box filter on advanced filter
// Add documentation about basic vs. advanced filter
async function applyFilter(filter_str) {
  if (!filter_str) {
    filtered.value = false;
    filter_slug.value = "";
    getTableData(1);
    return;
  }
  filter_slug.value = filter_str;
  getTableData(1);
  filtered.value = true;
}

async function clearFilter() {
  filter_select.value = null;
  filter_val.value = null;
  filter_slug.value = null;
  getTableData(1);
}

async function clearFilters() {
  filtered.value = false;
  clearFilter();
}

const columns = [
  {
    name: "name",
    align: "center",
    label: "Name",
    field: "name",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "descr",
    align: "center",
    label: "Description",
    field: "descr",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "confidential",
    align: "center",
    label: "Confidential",
    field: "confidential",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "jira_temp",
    align: "center",
    label: "Jira Template",
    field: "jira_temp",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "sunset_interval",
    align: "center",
    label: "Sunset Interval",
    field: "jira_temp",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "sunset_warn",
    align: "center",
    label: "Sunset Warning",
    field: "jira_temp",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
];
</script>

<style scoped>
.doc-btn {
  height: 4em;
  margin: 2vw;
}

.page-input {
  width: 4em;
  margin-left: 2vw;
  text-align: right;
}

.num-selected {
  margin-left: 1vw;
  font-size: 1.2em;
  margin-top: 0.7em;
  font-weight: bold;
}

.tool-row {
  margin-bottom: 2vh;
  margin-top: 1vh;
}

.col-row-width {
  min-width: 100%;
}

.num-pages {
  margin-right: 1vw;
  font-size: 1.15em;
}

.page-title {
  font-size: 2em;
}
</style>
