<template>
  <q-page>
    <div class="q-pa-md row">
      <q-table
        title="Token Management"
        :rows="rows"
        :columns="columns"
        selection="single"
        row-key="user"
        separator="cell"
        v-model:selected="selected"
        :rows-per-page-options="[0]"
        data-cy="token-table"
      >
        <template v-slot:top-right>
          <q-btn
            color="primary"
            v-show="isAdmin"
            @click="new_tok = true"
            label="Add Token"
            icon-right="add"
            no-caps
            data-cy="token-create-btn"
          >
          </q-btn>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td class="text-center">
              <q-btn
                v-show="!props.selected"
                round
                color="primary"
                @click="props.selected = !props.selected"
                icon="visibility"
                size="xs"
                data-cy="set-show"
              >
              </q-btn>
              <q-btn
                v-show="props.selected"
                round
                color="primary"
                @click="props.selected = !props.selected"
                icon="visibility_off"
                size="xs"
                data-cy="clear-show"
              >
              </q-btn>
              &nbsp;
              <q-btn
                round
                color="negative"
                @click="deleteToken(props.row['user'])"
                icon="delete"
                size="xs"
                data-cy="data-delete-btn"
              >
              </q-btn>
            </q-td>
            <q-td
              v-for="col in props.cols"
              :key="col.name"
              :props="props"
              class="cell"
            >
              {{ col.value }}
            </q-td>
          </q-tr>
          <q-tr v-show="props.selected" :props="props">
            <q-td colspan="100%">
              <q-input
                label="Token Value"
                v-model.trim="tok_vals[props.row.user]"
                data-cy="tok-role"
                readonly
                borderless
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
    <q-dialog v-model="new_tok">
      <create-token-dialog @newToken="tokenCreated()" />
    </q-dialog>
  </q-page>
</template>

<script>
import { retrieveData, deleteData, postData } from "@/utils.js";

import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";
import CreateTokenDialog from "@/views/token/CreateToken.vue";

export default {
  name: "TokenPage",
  components: {
    CreateTokenDialog,
  },
};
const columns = [
  {
    name: "user",
    align: "center",
    label: "User",
    field: "user",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "created",
    align: "center",
    label: "Created",
    field: "created",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "exp_date",
    align: "center",
    label: "Expires in",
    field: "expires_in",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "expired",
    align: "center",
    label: "Expired",
    field: "expired",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "admin",
    align: "center",
    label: "Admin",
    field: "admin",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "read_all",
    align: "center",
    label: "Read All",
    field: "read_all",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
  {
    name: "active",
    align: "center",
    label: "Active",
    field: "active",
    classes: "tab page-col",
    headerStyle: "font-size:large;",
    style: "width: 15em;",
    sortable: true,
  },
];
</script>

<script setup>
import { useRouter } from "vue-router";

const store = useStore();
const isAdmin = ref(computed(() => store.getters.isAdmin));

const new_tok = ref(false);
const router = useRouter();
const rows = ref([]);
const selected = ref([]);
const tok_vals = ref({});

onMounted(() => {
  if (!isAdmin.value) router.push("/");
  getTokenList();
});

async function tokenCreated() {
  new_tok.value = false;
  getTokenList();
}

async function getTokenVal(user) {
  if (typeof user !== "undefined" && user) {
    let res = await postData(`auth/token/${user}`, {}, null);
    return res["Authorization"];
  }
}

async function getTokenList() {
  rows.value = await retrieveData("auth/token");

  tok_vals.value = {};
  for (const row of rows.value) {
    let tok = await getTokenVal(row["user"]);
    tok_vals.value[row["user"]] = tok;
  }
}

async function deleteToken(user) {
  if (!window.confirm(`Delete token for user: ${user}?`)) {
    return;
  }

  await deleteData(
    `auth/token/${user}`,
    {},
    `Successfully deleted token for ${user}`
  );
  getTokenList();
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
  margin-bottom: 2em;
  margin-top: 5em;
}

.schema-col {
  text-align: left;
  width: 15em;
}

.cell {
  font-size: 1em;
}
</style>