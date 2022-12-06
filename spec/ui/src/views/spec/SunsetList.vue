<template>
  <q-page>
    <div>
      <q-table
        :rows="rows"
        :columns="columns"
        :rows-per-page-options="[0]"
        data-cy="spec-table"
      >
        <template v-slot:header="props">
          <q-th
            v-for="col in columns"
            :key="col.name"
            :props="props"
            style="vertical-align: top"
          >
            {{ col.label }}
          </q-th>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td
              v-for="col in props.cols"
              :key="col.name"
              :props="props"
              class="text-center"
            >
              <span v-if="col.name === 'num'">
                <router-link
                  :to="'/ui-spec/' + props.row['num'] + '/' + props.row['ver']"
                >
                  {{ props.row["num"] }}/{{ props.row["ver"] }}
                </router-link>
              </span>
              <span
                v-else-if="
                  ['sunset_dt', 'approved_dt', 'sunset_extended_dt'].includes(
                    col.name
                  )
                "
                >{{ dispDate(props.row[col.name]) }}</span
              >
              <span v-else>{{ props.row[col.name] }}</span>
            </q-td>
          </q-tr>
        </template>
        <template v-slot:bottom>
          <q-space />
          <q-btn
            color="primary"
            :href="apiServerHost + '/sunset/?output_csv=true'"
            target="_blank"
            icon="file_download"
            data-cy="open-file"
          />
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script>
import { apiServerHost, dispDate, retrieveData } from "@/utils.js";

import { ref, onMounted } from "vue";

export default {
  name: "SunsetList",
};
</script>

<script setup>
const rows = ref([]);

onMounted(() => {
  getTableData();
});

async function getTableData() {
  let data_rows = await retrieveData("sunset/");
  rows.value = formatRows(data_rows);
}

function formatRows(rows) {
  return rows;
}

const columns = [
  {
    name: "sunset_dt",
    align: "left",
    label: "Sunset",
    field: "sunset_dt",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "num",
    align: "left",
    label: "Spec",
    field: "num",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "title",
    align: "left",
    label: "Title",
    field: "title",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "doc_type",
    align: "left",
    label: "Doc Type",
    field: "doc_type",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "department",
    align: "left",
    label: "Department",
    field: "department",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "approved_dt",
    align: "left",
    label: "Approved",
    field: "approved_dt",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
  {
    name: "sunset_extended_dt",
    align: "left",
    label: "Extended",
    field: "sunset_extended_dt",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: false,
  },
];
</script>

